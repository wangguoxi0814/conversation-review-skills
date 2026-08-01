#!/usr/bin/env python3
"""Append a question group to the global todos.json datastore."""

from __future__ import annotations

import argparse
import json
import sys
import io
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SKILL_ROOT = Path(__file__).resolve().parent.parent
CWD = Path.cwd()
DATA_DIR = CWD / "data"
DATA_FILE = DATA_DIR / "todos.json"


def load_store() -> dict:
    if not DATA_FILE.exists():
        return {"version": 1, "groups": []}
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_store(store: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def normalize_todo_group(raw: dict) -> dict:
    """Normalize input into a question group.

    Input format (supports both 'todos' and 'questions' keys):
    {
      "title": "optional title, defaults to current time",
      "questions": [
        {"original": "用户原话", "text": "补充后的清晰表述"},
        "简单形式（自动复制到 original）"
      ]
    }
    """
    now = datetime.now(timezone.utc).astimezone()
    group_id = now.strftime("%Y%m%d-%H%M%S")

    title = raw.get("title") or now.strftime("%Y-%m-%d %H:%M")

    # Support both 'todos' and 'questions' keys
    items = raw.get("questions") or raw.get("todos") or []

    todos = []
    for i, item in enumerate(items):
        if isinstance(item, str):
            # Simple string form: use same text for both original and text
            todos.append({
                "id": f"t-{group_id}-{i+1:03d}",
                "text": item,
                "original": item,
                "done": False
            })
        elif isinstance(item, dict):
            text = item.get("text", "")
            original = item.get("original", text)  # Default original to text if not provided
            todos.append({
                "id": item.get("id", f"t-{group_id}-{i+1:03d}"),
                "text": text,
                "original": original,
                "done": item.get("done", False)
            })

    return {
        "id": group_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "title": title,
        "todos": todos
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a question group to todos.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    group.add_argument("--file", type=Path, help="Read JSON from file")
    args = parser.parse_args()

    if args.stdin:
        payload = sys.stdin.read()
    else:
        payload = args.file.read_text(encoding="utf-8")

    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    todo_group = normalize_todo_group(raw)

    store = load_store()
    store.setdefault("groups", []).append(todo_group)
    store["groups"].sort(key=lambda g: g.get("timestamp", ""))
    save_store(store)

    print(f"Appended {len(todo_group['todos'])} questions (group {todo_group['id']}) -> {DATA_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
