# parsepdf

Convert PDFs to Markdown (tables, LaTeX equations, headings) with [LlamaParse](https://cloud.llamaindex.ai), from any AI agent or a plain terminal.

[All skills](../README.md) · [Agent instructions](SKILL.md)

## What it does

- Parses PDF files, whole folders of PDFs, or PDF URLs into one Markdown file each, with `<!-- page N -->` markers.
- Uses the `cost_effective` tier by default (about 3 credits per page). Pass `--agentic` (about 10 credits per page) when you want the higher-quality tier.
- Rotates across all your keys (`LLAMA_CLOUD_API_KEY`, `LLAMA_CLOUD_API_KEY2`, `LLAMA_CLOUD_API_KEY3` and so on, with no limit). When a key is invalid, out of credits or rate limited, it moves to the next one and remembers the cooldown.
- Skips PDFs that were already parsed, and logs pages, credits and key name to `manifest.csv`. It never prints key values.

The skill is a standard `SKILL.md` plus one standalone Python script, so it works the same in Claude Code, Codex, Cursor, Gemini CLI or any agent that can run a shell command.

## Install

**1. Install the skill.** In Codex, paste:

```text
$skill-installer install the parsepdf skill from https://github.com/maystroh/agents_skills/tree/main/parsepdf
```

In Claude Code, paste:

```text
Install the skill from https://github.com/maystroh/agents_skills/tree/main/parsepdf into ~/.claude/skills/parsepdf
```

In any other agent that can run shell commands (Cursor, Gemini CLI and so on), paste:

```text
Install the skill from https://github.com/maystroh/agents_skills/tree/main/parsepdf into your skills folder, or reference its SKILL.md from AGENTS.md if you don't have one
```

Start a new session afterwards so the agent loads the skill.

**2. Ask the agent to set it up.** In a new chat, say:

```text
Set up $parsepdf
```

It installs its dependency, then asks for the path of the `.env` that holds your keys. Paste the path and it imports the keys and tests them. If you don't have a `.env`, it gives you one command to copy into your terminal, where you paste your keys with hidden input. The keys never go through the chat.

**3. Use it:** `Use $parsepdf on C:\papers\paper.pdf`. Add "in agentic mode" for the higher tier. To add a new key later, say "add a LlamaCloud key to parsepdf".

### Managing keys

Keys are saved in `~/.config/parsepdf/.env` as `LLAMA_CLOUD_API_KEY`, `LLAMA_CLOUD_API_KEY2`, `LLAMA_CLOUD_API_KEY3` and so on, and every agent on the machine uses them. Environment variables, or a `.env` in your project folder, take precedence.

| Command | Effect |
| --- | --- |
| `--add-key` | Add new keys with hidden prompts, numbered after the existing ones. Duplicates are skipped. |
| `--add-key --from FILE` | Import every `LLAMA_CLOUD_API_KEY*` from a `.env`. Safe for an agent to run. |
| `--remove-key 3` | Remove `LLAMA_CLOUD_API_KEY3`. |
| `--check` | List the saved key names and whether each is usable. |
| `--verify` | Test each key with LlamaCloud. No credits are used. |

## Use it

Ask your agent, for example:

```text
Use $parsepdf on ~/papers/ and summarize the results tables.
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
| `--reset-state` | Forget saved key cooldowns (stored in `~/.cache/parsepdf/key_state.json`, names and hashes only). |

## Tiers

Measured on a 10-page PDF scientific paper (October 2026):

| Tier | Credits per page | Result |
| --- | --- | --- |
| `fast` | 1 | Plain text, no tables. |
| `cost_effective` (default) | 3 | Correct Markdown tables, LaTeX equations and headings. |
| `agentic` | 10 | Slightly cleaner headings; fixes tables that `cost_effective` collapses into one cell. |
| `agentic_plus` | more | Highest quality, not benchmarked. |

On 186 MRI papers, `cost_effective` was clean for 173. The other 13 had collapsed tables, and re-parsing them with `--agentic` fixed all of them.
