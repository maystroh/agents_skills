# parsepdf

Convert PDFs to Markdown (tables, LaTeX equations, headings) with [LlamaParse](https://cloud.llamaindex.ai), from any AI agent or a plain terminal.

[All skills](../README.md) · [Agent instructions](SKILL.md)

## What it does

- Parses PDF files, whole folders of PDFs, or PDF URLs into one Markdown file each, with `<!-- page N -->` markers.
- Uses the `cost_effective` tier by default (about 3 credits per page). Pass `--agentic` (about 10 credits per page) when you want the higher-quality tier.
- Rotates across `LLAMA_CLOUD_API_KEY`, `LLAMA_CLOUD_API_KEY2`, `LLAMA_CLOUD_API_KEY3` and `LLAMA_CLOUD_API_KEY4`. When a key is invalid, out of credits or rate limited, it moves to the next one and remembers the cooldown.
- Skips PDFs that were already parsed, and logs pages, credits and key name to `manifest.csv`. It never prints key values.

The skill is a standard `SKILL.md` plus one standalone Python script, so it works the same in Claude Code, Codex, Cursor, Gemini CLI or any agent that can run a shell command.

## Install

**1. Copy the skill folder** to where your agent looks for skills:

| Agent | Skill folder |
| --- | --- |
| Claude Code | `~/.claude/skills/parsepdf/` (or `.claude/skills/parsepdf/` in a project) |
| Codex | `~/.codex/skills/parsepdf/`, or ask Codex: `$skill-installer install the parsepdf skill from https://github.com/maystroh/agents_skills/tree/main/parsepdf` |
| Other agents | Anywhere. Point the agent at `SKILL.md` (for example from `AGENTS.md` or Cursor rules). |

```bash
git clone --depth 1 https://github.com/maystroh/agents_skills /tmp/agents_skills
mkdir -p ~/.claude/skills && cp -r /tmp/agents_skills/parsepdf ~/.claude/skills/
```

On Windows PowerShell: `Copy-Item -Recurse agents_skills\parsepdf $HOME\.claude\skills\`.

**2. Install the dependency**, unless you use [uv](https://docs.astral.sh/uv/), which installs it on the fly with `uv run`:

```bash
pip install -r requirements.txt   # llama-cloud>=1.4
```

**3. Add your keys.** Copy `.env.example` to `.env` and fill in your LlamaCloud keys. The script looks for `.env` in the current folder and its parents, then in the skill folder, then in `~/.config/parsepdf/.env`. Environment variables take precedence. Never commit the filled-in `.env`.

```bash
python scripts/parsepdf.py --check   # shows which key names were found; no credits used
```

## Use it

Ask your agent, for example:

```text
Use parsepdf on ~/papers/ and summarize the results tables.
Parse https://example.org/paper.pdf with parsepdf in agentic mode.
```

Or run it yourself:

```bash
python scripts/parsepdf.py paper.pdf                      # -> parsed_pdfs/paper.md
python scripts/parsepdf.py papers/ --out parsed/ --json   # a folder, JSON summary per PDF
python scripts/parsepdf.py paper.pdf --agentic            # -> parsed_pdfs/paper.agentic.md
python scripts/parsepdf.py short.pdf --stdout             # print the Markdown
```

| Option | Effect |
| --- | --- |
| `--agentic` / `--tier {fast,cost_effective,agentic,agentic_plus}` | Parsing tier (default `cost_effective`). |
| `--out DIR` | Output folder (default `./parsed_pdfs`). |
| `--stdout` | Print Markdown instead of writing files. |
| `--json` | One JSON object per PDF on stdout. |
| `--overwrite` | Re-parse PDFs that already have output. |
| `--env-file PATH` | Use a specific `.env`. |
| `--check` | List configured keys and whether each is usable. |
| `--reset-state` | Forget saved key cooldowns (stored in `~/.cache/parsepdf/key_state.json`, names and hashes only). |

## Tiers

Measured on a 10-page MICCAI paper (October 2026):

| Tier | Credits per page | Result |
| --- | --- | --- |
| `fast` | 1 | Plain text, no tables. |
| `cost_effective` (default) | 3 | Correct Markdown tables, LaTeX equations and headings. |
| `agentic` | 10 | Slightly cleaner headings; fixes tables that `cost_effective` collapses into one cell. |
| `agentic_plus` | more | Highest quality, not benchmarked. |

On 186 MRI papers, `cost_effective` was clean for 173. The other 13 had collapsed tables, and re-parsing them with `--agentic` fixed all of them.
