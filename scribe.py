#!/usr/bin/env python3
"""Scribe — generate a self-contained HTML book from Claude Code transcripts.

Usage:
    python scribe.py                        # auto-find all transcripts, output scribe-book.html
    python scribe.py --project <hash>       # only one project folder
    python scribe.py --out book.html        # custom output path
    python scribe.py --days 30              # only sessions in last N days

No external dependencies. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def find_projects_dir() -> Path:
    """Locate ~/.claude/projects regardless of platform."""
    home = Path.home()
    candidate = home / ".claude" / "projects"
    if candidate.exists():
        return candidate
    raise SystemExit(f"Couldn't find Claude projects dir at {candidate}. Is Claude Code installed?")


def load_jsonl(path: Path) -> list[dict]:
    """Parse a .jsonl file, tolerating corrupt lines."""
    records = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return records


def parse_sessions(jsonl_files: list[Path]) -> dict[str, dict]:
    """Group transcript records into sessions keyed by sessionId."""
    sessions: dict[str, dict] = {}
    for fp in jsonl_files:
        for rec in load_jsonl(fp):
            if rec.get("type") == "queue-operation":
                continue
            sid = rec.get("sessionId")
            if not sid:
                continue
            s = sessions.setdefault(sid, {
                "id": sid,
                "cwd": rec.get("cwd") or "",
                "gitBranch": rec.get("gitBranch") or "",
                "messages": [],
                "firstTs": rec.get("timestamp"),
                "lastTs": rec.get("timestamp"),
                "firstUserText": "",
            })
            ts = rec.get("timestamp")
            if ts:
                if not s["firstTs"] or ts < s["firstTs"]:
                    s["firstTs"] = ts
                if not s["lastTs"] or ts > s["lastTs"]:
                    s["lastTs"] = ts
            if rec.get("cwd"):
                s["cwd"] = rec["cwd"]
            if rec.get("gitBranch"):
                s["gitBranch"] = rec["gitBranch"]
            if rec.get("type") in ("user", "assistant"):
                s["messages"].append(rec)
                if rec["type"] == "user" and not s["firstUserText"]:
                    content = rec.get("message", {}).get("content")
                    if isinstance(content, list):
                        for c in content:
                            if c.get("type") == "text":
                                s["firstUserText"] = (c.get("text") or "")[:200]
                                break
                    elif isinstance(content, str):
                        s["firstUserText"] = content[:200]
    return sessions


def filter_by_age(sessions: dict[str, dict], days: int) -> dict[str, dict]:
    if days <= 0:
        return sessions
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    kept = {}
    for sid, s in sessions.items():
        ts = s.get("lastTs")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt >= cutoff:
                kept[sid] = s
        except (ValueError, AttributeError):
            kept[sid] = s
    return kept


HTML_SHELL_PATH_CANDIDATES = [
    Path(__file__).parent / "Scribe.html",
    Path.cwd() / "Scribe.html",
]


def load_html_shell() -> str:
    for p in HTML_SHELL_PATH_CANDIDATES:
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise SystemExit("Scribe.html not found next to scribe.py. Download both from the repo.")


def inject_data(html: str, sessions: dict[str, dict]) -> str:
    """Embed sessions data into the HTML so it opens pre-loaded."""
    payload = json.dumps({"sessions": sessions}, ensure_ascii=False, separators=(",", ":"))
    script = (
        "<script>window.SCRIBE_EMBEDDED_DATA = "
        + payload
        + ";</script>\n</body>"
    )
    return html.replace("</body>", script, 1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="Only this project hash (subfolder under .claude/projects/). Default: all.")
    ap.add_argument("--out", default="scribe-book.html", help="Output HTML path. Default: ./scribe-book.html")
    ap.add_argument("--days", type=int, default=0, help="Only keep sessions in the last N days. 0 = all.")
    args = ap.parse_args()

    projects_dir = find_projects_dir()
    if args.project:
        target = projects_dir / args.project
        if not target.exists():
            raise SystemExit(f"Project not found: {target}")
        dirs = [target]
    else:
        dirs = [d for d in projects_dir.iterdir() if d.is_dir()]

    jsonl_files: list[Path] = []
    for d in dirs:
        jsonl_files.extend(d.rglob("*.jsonl"))
    if not jsonl_files:
        raise SystemExit(f"No .jsonl files found in {projects_dir}.")

    print(f"Reading {len(jsonl_files)} transcript files from {len(dirs)} project folder(s)…")
    sessions = parse_sessions(jsonl_files)
    if args.days:
        before = len(sessions)
        sessions = filter_by_age(sessions, args.days)
        print(f"  {before} sessions → {len(sessions)} after --days {args.days} filter")

    total_msgs = sum(len(s["messages"]) for s in sessions.values())
    print(f"  Parsed {len(sessions)} sessions · {total_msgs} messages")

    html = load_html_shell()
    out_html = inject_data(html, sessions)
    out_path = Path(args.out).resolve()
    out_path.write_text(out_html, encoding="utf-8")
    print(f"✓ Wrote {out_path}")
    print(f"  Open it in a browser to read your sessions (no imports needed — data is baked in).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
