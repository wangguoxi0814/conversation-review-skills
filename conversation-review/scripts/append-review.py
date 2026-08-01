#!/usr/bin/env python3
"""Append a todo group to the global todos.json datastore."""

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
    """Normalize input into a todo group.

    Input format:
    {
      "title": "optional title, defaults to current time",
      "todos": ["todo text 1", "todo text 2"]
    }
    """
    now = datetime.now(timezone.utc).astimezone()
    group_id = now.strftime("%Y%m%d-%H%M%S")

    title = raw.get("title") or now.strftime("%Y-%m-%d %H:%M")

    todos = []
    for i, item in enumerate(raw.get("todos", [])):
        if isinstance(item, str):
            todos.append({
                "id": f"t-{group_id}-{i+1:03d}",
                "text": item,
                "done": False
            })
        elif isinstance(item, dict):
            todos.append({
                "id": item.get("id", f"t-{group_id}-{i+1:03d}"),
                "text": item.get("text", ""),
                "done": item.get("done", False)
            })

    return {
        "id": group_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "title": title,
        "todos": todos
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a todo group to todos.json")
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

    print(f"Appended {len(todo_group['todos'])} todos (group {todo_group['id']}) -> {DATA_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
