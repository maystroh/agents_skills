#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["llama-cloud>=1.4", "httpx"]
# ///
"""Convert PDFs to Markdown with LlamaParse (LlamaCloud), rotating API keys.

Keys come from LLAMA_CLOUD_API_KEY, LLAMA_CLOUD_API_KEY2, LLAMA_CLOUD_API_KEY3 and
LLAMA_CLOUD_API_KEY4 (more numbers also work). Environment variables win over a
.env file. The .env is searched in this order: --env-file, $PARSEPDF_ENV_FILE,
./.env and its parent folders, the skill folder, ~/.config/parsepdf/.env.
When a key fails (bad key, no credits, rate limit) the next one is tried.

Examples:
    parsepdf.py paper.pdf                       # cost_effective tier (default)
    parsepdf.py paper.pdf --agentic             # agentic tier, for hard layouts
    parsepdf.py papers/ --out parsed/           # every PDF under a folder
    parsepdf.py https://example.org/paper.pdf   # LlamaCloud fetches the URL
    parsepdf.py paper.pdf --stdout              # print the Markdown instead
    parsepdf.py --check                         # list key names and their health

Output: <out>/<name>.md per PDF (with <!-- page N --> markers) and a manifest.csv.
Progress goes to stderr; stdout has the output paths, the Markdown with --stdout,
or one JSON object per PDF with --json. Key values are never printed.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import re
import shlex
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

TIERS = ["fast", "cost_effective", "agentic", "agentic_plus"]
DEFAULT_TIER = "cost_effective"
KEY_PATTERN = re.compile(r"^LLAMA_CLOUD_API_KEY(?:_?(\d+))?$")
SKILL_DIR = Path(__file__).resolve().parents[1]
STATE_FILE = Path(
    os.getenv("PARSEPDF_STATE_FILE")
    or Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache") / "parsepdf" / "key_state.json"
)


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- keys


@dataclass(frozen=True)
class Key:
    name: str
    index: int
    value: str

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.value.encode("utf-8")).hexdigest()[:12]


def find_env_file(explicit: str | None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if os.getenv("PARSEPDF_ENV_FILE"):
        candidates.append(Path(os.environ["PARSEPDF_ENV_FILE"]).expanduser())
    cwd = Path.cwd().resolve()
    candidates += [folder / ".env" for folder in (cwd, *cwd.parents)]
    candidates += [SKILL_DIR / ".env", Path.home() / ".config" / "parsepdf" / ".env"]
    for path in candidates:
        if path.is_file() and read_env_file(path):
            return path
    if explicit:
        raise SystemExit(f"--env-file {explicit} has no LLAMA_CLOUD_API_KEY entries.")
    return None


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    line_pattern = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return values
    for line in lines:
        match = line_pattern.match(line)
        if not match or not KEY_PATTERN.match(match.group(1)):
            continue
        raw = match.group(2).strip()
        try:
            parts = shlex.split(raw, comments=True)
            value = " ".join(parts)
        except ValueError:
            value = raw.split("#", 1)[0].strip().strip("'\"")
        if value:
            values[match.group(1)] = value
    return values


def load_keys(env_file: Path | None) -> list[Key]:
    merged = read_env_file(env_file) if env_file else {}
    for name, value in os.environ.items():
        if KEY_PATTERN.match(name) and value.strip():
            merged[name] = value.strip()
    keys, seen = [], set()
    for name, value in merged.items():
        if value in seen:
            continue
        seen.add(value)
        keys.append(Key(name, int(KEY_PATTERN.match(name).group(1) or 1), value))
    return sorted(keys, key=lambda key: (key.index, key.name))


class KeyState:
    """Non-secret key health (cooldowns, failures) keyed by a hash of each key."""

    def __init__(self, path: Path = STATE_FILE):
        self.path = path
        try:
            self.data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.data = {}

    def entry(self, key: Key) -> dict:
        entry = self.data.setdefault(key.fingerprint, {})
        entry["name"] = key.name
        return entry

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(self.path)
        except OSError as exc:  # state is a convenience; never fail a parse over it
            log(f"warning: could not save key state to {self.path}: {exc}")

    def unavailable_reason(self, key: Key, now: datetime) -> str | None:
        entry = self.entry(key)
        if entry.get("disabled"):
            return f"disabled ({entry.get('last_error_category')})"
        until = entry.get("cooldown_until")
        if until and datetime.fromisoformat(until) > now:
            return f"cooling down until {until}"
        return None

    def order(self, key: Key) -> tuple:
        entry = self.entry(key)
        return (entry.get("failures", 0), entry.get("last_attempt") or "", key.index)

    def record(self, key: Key, *, category: str | None = None, cooldown: datetime | None = None,
               disabled: bool = False) -> None:
        entry = self.entry(key)
        entry["last_attempt"] = datetime.now(timezone.utc).isoformat()
        if category is None:
            entry.update(failures=0, disabled=False, cooldown_until=None, last_error_category=None)
            entry["successes"] = entry.get("successes", 0) + 1
        else:
            entry["failures"] = entry.get("failures", 0) + 1
            entry["last_error_category"] = category
            entry["disabled"] = disabled
            entry["cooldown_until"] = cooldown.isoformat() if cooldown else None
        self.save()


def classify_failure(exc: BaseException) -> tuple[str, timedelta | None, bool]:
    """Return (category, cooldown, permanently disabled) for an API error."""
    import httpx

    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    text = str(exc).lower()
    if status in (401, 403) or any(t in text for t in ("invalid api key", "unauthorized", "forbidden")):
        return "auth", None, True
    if status in (402, 429) or any(t in text for t in ("rate limit", "quota", "credit", "limit reached", "exceeded")):
        return "quota", timedelta(hours=12), False
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)) or "timeout" in text:
        return "network", timedelta(minutes=5), False
    if isinstance(status, int) and status >= 500:
        return "server", timedelta(minutes=15), False
    return "error", timedelta(minutes=30), False


def is_input_error(exc: BaseException) -> bool:
    """Errors caused by the document, not the key: retrying another key won't help."""
    status = getattr(exc, "status_code", None)
    return isinstance(exc, OSError) and not _is_network(exc) or status in (400, 413, 415, 422)


def _is_network(exc: BaseException) -> bool:
    import httpx

    return isinstance(exc, (httpx.TransportError, ConnectionError, TimeoutError))


# --------------------------------------------------------------------------- parse


@dataclass
class Result:
    source: str
    output: str | None
    tier: str
    pages: int
    credits: float | None
    key: str
    seconds: float
    markdown: str


async def parse_one(source: str, tier: str, keys: list[Key], state: KeyState) -> Result:
    from llama_cloud import AsyncLlamaCloud

    now = datetime.now(timezone.utc)
    usable = []
    for key in keys:
        reason = state.unavailable_reason(key, now)
        if reason:
            log(f"   skipping {key.name}: {reason}")
        else:
            usable.append(key)
    if not usable:
        raise RuntimeError("No usable LlamaCloud key right now. Run with --check, or --reset-state "
                           "after fixing or topping up keys.")
    usable.sort(key=state.order)

    is_url = source.startswith(("http://", "https://"))
    failures = []
    for key in usable:
        started = time.time()
        log(f"   using {key.name}")
        client = AsyncLlamaCloud(api_key=key.value)
        try:
            kwargs: dict = dict(tier=tier, version="latest")
            if is_url:
                kwargs["source_url"] = source
            else:
                with open(source, "rb") as handle:
                    uploaded = await client.files.create(file=handle, purpose="parse")
                kwargs["file_id"] = uploaded.id
            if tier == "fast":
                kwargs["expand"] = ["text"]
            else:
                kwargs["expand"] = ["markdown"]
                kwargs["output_options"] = {"markdown": {"tables": {"output_tables_as_markdown": True}}}
            parsed = await client.parsing.parse(**kwargs)
            credits = None
            try:
                usage = await client.parsing.get(parsed.job.id, expand=["usage"])
                credits = usage.job.usage.credits if usage.job.usage else None
            except Exception:  # usage is informational only
                pass
            state.record(key)
        except Exception as exc:
            if is_input_error(exc):
                raise
            category, cooldown, disabled = classify_failure(exc)
            state.record(key, category=category, disabled=disabled,
                         cooldown=datetime.now(timezone.utc) + cooldown if cooldown else None)
            failures.append(f"{key.name}: {category}")
            log(f"   {key.name} failed ({category}): {str(exc)[:300]}")
            continue
        finally:
            close = getattr(client, "close", None)
            if callable(close):
                await close()

        if parsed.markdown:
            pages = [(p.page_number, p.markdown) for p in parsed.markdown.pages]
        else:
            pages = [(p.page_number, p.text) for p in parsed.text.pages]
        markdown = "\n\n".join(f"<!-- page {n} -->\n{body}" for n, body in pages)
        return Result(source, None, tier, len(pages), credits, key.name, time.time() - started, markdown)

    raise RuntimeError("All LlamaCloud keys failed: " + "; ".join(failures))


def output_name(source: str) -> str:
    if source.startswith(("http://", "https://")):
        name = Path(unquote(urlparse(source).path)).stem or "document"
    else:
        name = Path(source).stem
    return re.sub(r"[^\w.-]+", "_", name)


def collect_inputs(items: list[str]) -> list[str]:
    sources: list[str] = []
    for item in items:
        if item.startswith(("http://", "https://")):
            sources.append(item)
            continue
        path = Path(item).expanduser()
        if path.is_dir():
            sources += [str(p) for p in sorted(path.rglob("*")) if p.suffix.lower() == ".pdf"]
        elif path.is_file():
            sources.append(str(path))
        else:
            raise SystemExit(f"Not found: {item}")
    return sources


async def run(args: argparse.Namespace, keys: list[Key]) -> int:
    sources = collect_inputs(args.inputs)
    if not sources:
        raise SystemExit("No PDFs found.")
    out_dir = Path(args.out).expanduser()
    state = KeyState()
    manifest = None
    if not args.stdout:
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = out_dir / "manifest.csv"
        new = not manifest_path.exists()
        manifest = manifest_path.open("a", newline="", encoding="utf-8")
        writer = csv.writer(manifest)
        if new:
            writer.writerow(["source", "output", "tier", "pages", "credits", "key", "seconds", "parsed_at"])

    failed = total_credits = 0
    try:
        for number, source in enumerate(sources, 1):
            suffix = "" if args.tier == DEFAULT_TIER else f".{args.tier}"
            target = out_dir / f"{output_name(source)}{suffix}.md"
            if not args.stdout and target.exists() and not args.overwrite:
                log(f"[{number}/{len(sources)}] skip, already parsed: {target}")
                emit(args, Result(source, str(target), args.tier, 0, 0, "", 0, ""), skipped=True)
                continue
            log(f"[{number}/{len(sources)}] {source} ({args.tier})")
            try:
                result = await parse_one(source, args.tier, keys, state)
            except Exception as exc:
                failed += 1
                log(f"   failed: {exc}")
                if args.json:
                    print(json.dumps({"source": source, "error": str(exc)}), flush=True)
                continue
            total_credits += result.credits or 0
            if args.stdout:
                print(result.markdown, flush=True)
            else:
                target.write_text(result.markdown, encoding="utf-8")
                result.output = str(target)
                writer.writerow([source, target, result.tier, result.pages, result.credits, result.key,
                                 f"{result.seconds:.1f}", datetime.now(timezone.utc).isoformat()])
                manifest.flush()
                emit(args, result)
            log(f"   {result.pages} pages, {result.credits} credits via {result.key}")
    finally:
        if manifest:
            manifest.close()
    log(f"Done: {len(sources) - failed}/{len(sources)} ok, {total_credits:g} credits.")
    return 1 if failed else 0


def emit(args: argparse.Namespace, result: Result, skipped: bool = False) -> None:
    if args.json:
        record = {k: v for k, v in result.__dict__.items() if k != "markdown"}
        record["skipped"] = skipped
        print(json.dumps(record), flush=True)
    else:
        print(result.output, flush=True)


def check(keys: list[Key], env_file: Path | None) -> int:
    state = KeyState()
    now = datetime.now(timezone.utc)
    print(f".env file: {env_file or 'none found'}")
    print(f"key state: {state.path}")
    if not keys:
        print("No LlamaCloud keys found.")
        return 1
    for key in keys:
        reason = state.unavailable_reason(key, now)
        print(f"  {key.name}: {'unavailable, ' + reason if reason else 'available'}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="*", help="PDF files, folders (searched recursively) or http(s) URLs")
    parser.add_argument("--tier", choices=TIERS, default=DEFAULT_TIER, help="default: cost_effective")
    parser.add_argument("--agentic", dest="tier", action="store_const", const="agentic",
                        help="shorthand for --tier agentic")
    parser.add_argument("--out", default="parsed_pdfs", help="output folder (default: ./parsed_pdfs)")
    parser.add_argument("--stdout", action="store_true", help="print Markdown to stdout, write no files")
    parser.add_argument("--json", action="store_true", help="print one JSON object per PDF on stdout")
    parser.add_argument("--overwrite", action="store_true", help="re-parse PDFs that already have output")
    parser.add_argument("--env-file", help="path to a .env file holding the keys")
    parser.add_argument("--check", action="store_true", help="list configured key names and health, then exit")
    parser.add_argument("--reset-state", action="store_true", help="forget saved key cooldowns and failures")
    args = parser.parse_args()

    env_file = find_env_file(args.env_file)
    keys = load_keys(env_file)
    if args.reset_state:
        STATE_FILE.unlink(missing_ok=True)
        log(f"Cleared {STATE_FILE}")
    if args.check:
        sys.exit(check(keys, env_file))
    if not args.inputs:
        if args.reset_state:
            sys.exit(0)
        parser.error("give at least one PDF, folder or URL")
    if not keys:
        raise SystemExit("No LlamaCloud keys found. Set LLAMA_CLOUD_API_KEY (and _KEY2.._KEY4) in the "
                         "environment or a .env file; see .env.example next to this skill.")
    try:
        import llama_cloud  # noqa: F401
    except ImportError:
        raise SystemExit("Missing dependency: pip install 'llama-cloud>=1.4'  (or run with: uv run parsepdf.py ...)")
    sys.exit(asyncio.run(run(args, keys)))


if __name__ == "__main__":
    main()
