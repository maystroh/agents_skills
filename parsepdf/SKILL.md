---
name: parsepdf
description: Convert PDF files or PDF URLs to clean Markdown (tables, LaTeX equations, headings) with LlamaParse, rotating across any number of LlamaCloud API keys. Use when an agent needs to read, extract text or tables from, or summarize a PDF and plain text extraction is not good enough. Default tier is cost_effective; use agentic only when the user asks for it.
---

# parsepdf

Turn PDFs into Markdown with LlamaParse by running one CLI script. It works the same from any agent (Claude Code, Codex, Cursor, Gemini CLI, or a plain shell).

## Run it

```bash
python scripts/parsepdf.py <pdf | folder | https-url> [...]          # cost_effective (default)
python scripts/parsepdf.py <inputs> --agentic                         # only when the user asks
```

`scripts/` is relative to this skill's folder. Use the skill folder's absolute path when you run the script. The script installs its only dependency (`llama-cloud`) into the current Python on first use, so do not ask the user to install anything.

Each PDF becomes `parsed_pdfs/<name>.md` (change the folder with `--out DIR`), with `<!-- page N -->` markers between pages. stdout lists the output paths. Read those files rather than printing whole papers into the conversation. `manifest.csv` in the output folder records pages, credits and the key name used.

Other options:

- `--stdout` prints the Markdown instead of writing files (good for a short PDF).
- `--json` prints one JSON object per PDF (`source`, `output`, `tier`, `pages`, `credits`, `key`).
- `--overwrite` re-parses PDFs that already have output. Without it, existing outputs are skipped, so reruns cost nothing.
- `--check` lists which key names are configured and whether each is usable, without spending credits. `--verify` also tests each key with LlamaCloud, still with no credits used.
- `--env-file PATH` points at a specific `.env`.

## Choosing the tier

- Use `cost_effective` (the default, about 3 credits per page) unless the user says otherwise. It gives correct Markdown tables, LaTeX equations and headings.
- Use `--agentic` (about 10 credits per page) only when the user asks for agentic, the best quality, or a re-parse because tables came out broken. A typical sign is a whole table column collapsed into one cell joined by `<br/>`.
- `--tier fast` (1 credit per page, plain text, no tables) and `--tier agentic_plus` also exist. Use them only when asked.

Agentic output is saved as `<name>.agentic.md`, so it never overwrites the cost_effective file.

## First run, and adding keys

Do this right after the skill is installed, the first time it is used, or whenever the user asks to add or update LlamaCloud keys. Do it yourself and keep the user's part to a single copy-paste.

1. Run `python <skill folder>/scripts/parsepdf.py --check`. It uses no credits. If it lists keys and the user isn't adding a new one, skip to step 4.
2. Ask the user one question: "Which `.env` file holds your LlamaCloud keys? Paste its path, or say 'none' to type them in." Then:
   - **If they give a path**, run `--add-key --from <path>` yourself. This copies every `LLAMA_CLOUD_API_KEY*` entry into `~/.config/parsepdf/.env`, skips keys that are already saved and tests each one. You never see the values.
   - **If they say none, or want to add a new key**, give them the ready-to-paste command that `--check` printed under "Type or paste keys". It contains this machine's full Python and script paths. They run it in their own terminal, paste each key (input is hidden) and press Enter on an empty line to finish. Each key is saved as the next number (`LLAMA_CLOUD_API_KEY5`, `6` and so on). Do not run `--add-key` without `--from` yourself, because it waits for typing.
3. Never ask for key values in the chat, and never read or print the `.env` file.
4. Run `--verify` and report which key names show `ok`. To drop a dead key, run `--remove-key <number>`.

## Keys

The script reads `LLAMA_CLOUD_API_KEY`, `LLAMA_CLOUD_API_KEY2`, `LLAMA_CLOUD_API_KEY3` and so on, as many as are set, from the environment or a `.env` file. Environment variables win. The `.env` is searched in this order: `--env-file`, `$PARSEPDF_ENV_FILE`, `./.env` and each parent folder, this skill's folder, then `~/.config/parsepdf/.env`. See `.env.example`.

When a key is invalid, out of credits or rate limited, the script moves on to the next key and remembers that key's cooldown in `~/.cache/parsepdf/key_state.json`. That file holds only key names and hashes. `--reset-state` clears it after the user fixes or tops up a key.

Never print, log or commit key values. Report keys by name only, as `--check` does.

## When something fails

- "No LlamaCloud keys found": follow "First run, and adding keys" above. Do not ask the user to paste keys into the chat.
- "No usable LlamaCloud key right now": run `--check` and tell the user which keys are cooling down or disabled.
- A URL that the agent cannot download can still be passed directly, because LlamaCloud fetches it on its own servers.
- The exit code is 1 if any PDF failed. The other PDFs in the batch are still written.
