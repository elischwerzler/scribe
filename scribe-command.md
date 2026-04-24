# Scribe

Usage: `/scribe` — generate a self-contained Scribe book from the user's Claude Code transcripts, open it in their browser. AI-driven: no file picker, no manual import.

Optional args:
- `/scribe 7` — only sessions in the last 7 days
- `/scribe <project-hash>` — only one project folder

---

You are **Scribe**. Arguments: **$ARGUMENTS**

1. **Locate the Scribe repo locally.** Check these paths in order; use the first that exists:
   - `c:\Users\elisc\Desktop\ScribeRepo\` (Windows; this user)
   - `~/Desktop/ScribeRepo/`
   - Output of `git clone https://github.com/elischwerzler/scribe.git` into a temp path.

2. **Parse $ARGUMENTS:**
   - If it's a number → `--days <that number>`
   - If it's a hex-looking hash or folder name → `--project <that value>`
   - If empty → no extra flags

3. **Run the CLI:**
   ```
   cd <SCRIBE_DIR>
   python scribe.py --out "<USER_CWD>/scribe-book.html" <optional flags>
   ```
   Use the user's current working directory as output path so the book lands where they can find it.

4. **Open the resulting file in their default browser:**
   - Windows: `start "" "<out_path>"`
   - macOS: `open "<out_path>"`
   - Linux: `xdg-open "<out_path>"`

5. **Report back:** one line like `Wrote scribe-book.html — N sessions, M messages. Open it in your browser.`

## Style rules
- Don't dump the whole session list in chat — the HTML book IS the output.
- If no transcripts found, say so and stop — don't fabricate sessions.
- If Python isn't installed, tell the user `python --version` failed and suggest installing Python 3.9+.
