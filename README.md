# 📜 Scribe

**Turn your Claude Code transcripts into a searchable, readable book.**

Find out what you worked on yesterday, last week, last month. Ever forgotten what files you touched in a late-night coding session? What command fixed the build? What you decided during that long Claude convo last Tuesday? Scribe lets you re-read it all.

Single-file HTML app + a ~100-line Python script. No install beyond Python 3.9+. No backend. No upload. All your transcripts stay local.

---

## Two ways to use it

### 🤖 AI-driven (recommended — the AI does it all)

Put the slash command [`scribe-command.md`](scribe-command.md) into your Claude Code `commands/` folder (global: `~/.claude/commands/` or per-project `.claude/commands/`).

Then any Claude Code session can run:

```
/scribe              # all sessions, full history
/scribe 7            # last 7 days only
/scribe <proj-hash>  # only one project
```

Claude locates the repo, runs `scribe.py`, produces a self-contained `scribe-book.html` in your current directory, and opens it. Zero file-picking.

### 🖱 Manual (run the Python script yourself)

```bash
python scribe.py                   # all transcripts -> ./scribe-book.html
python scribe.py --days 7          # last 7 days only
python scribe.py --out ~/book.html # custom output
python scribe.py --project <hash>  # one project only
```

Double-click the resulting `scribe-book.html`. Everything is embedded — no imports needed.

### 🖱 Manual (HTML-only, no Python)

Open [`Scribe.html`](Scribe.html) directly, click **📂 Load Transcripts**, pick `.jsonl` files from `~/.claude/projects/<project>/` — the original flow is still there if you'd rather skip Python.

---

## What it shows you

- **Timeline of sessions** grouped by date, per project directory, with git branch
- **Every message** you sent and Claude sent back — rendered cleanly
- **Tool calls** Claude made (Bash, Edit, Write, Grep, etc.) with file paths / commands inline
- **Artifacts panel** extracts the useful stuff automatically:
  - 📄 **Files touched** (with edit counts)
  - 📝 **Commits made** (parsed from `git commit -m "..."`)
  - 💻 **Commands run** (bash/powershell history)
- **Full-text search** across every message, file path, command, and tool call
- **⬇ Export Session** → get any session as Markdown, drop-in for devlog posts or PR descriptions

---

## Why

Claude sessions compound real work. Scrolling a giant terminal buffer or digging through `.jsonl` files by hand loses everything. Scribe treats your sessions as a book.

Use it to:

- Write your weekly/monthly devlog without re-remembering
- Onboard to your own old codebase by re-reading what you did
- Find that one command that fixed the build three weeks ago
- Audit what you actually shipped vs. what you talked about shipping

---

## For AI agents working inside a user's repo

If a user asks *"what was I doing last time I was in this codebase?"*:

1. Check the repo root for a `devlog/` folder or `SCRIBE.md`.
2. If missing, suggest they run `/scribe` — or run it yourself if they've granted permission.
3. Read the generated book for context before making recommendations.

Much cheaper than re-deriving the answer from `git log`, and more accurate than guessing from file timestamps.

---

## Privacy

100% local. Your transcripts never leave the machine. `scribe.py` only reads `~/.claude/projects/` and writes the output file you name. `Scribe.html` has no network calls — you can read the whole source.

---

## Feed it different transcripts

Scribe parses Claude Code's `.jsonl` format. It should also work on any JSONL with the same shape (`type`, `message.role`, `message.content`, `timestamp`, `sessionId`). If you have another AI tool that exports in a different format, open an issue with a sample and I'll add a parser.

---

## License

MIT. Fork it, remix it, turn it into whatever you need.
