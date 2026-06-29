#!/usr/bin/env python3
"""Append a conversation review JSON entry to the local datastore."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_ROOT / "data"
DATA_FILE = DATA_DIR / "reviews.json"


def load_store() -> dict:
    if not DATA_FILE.exists():
        return {"version": 1, "reviews": []}
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_store(store: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def normalize_review(raw: dict) -> dict:
    review = dict(raw)
    if not review.get("id"):
        review["id"] = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    if not review.get("timestamp"):
        review["timestamp"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    return review


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a review entry to reviews.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stdin", action="store_true", help="Read JSON from stdin")
    group.add_argument("--file", type=Path, help="Read JSON from file")
    args = parser.parse_args()

    if args.stdin:
        payload = sys.stdin.read()
    else:
        payload = args.file.read_text(encoding="utf-8")

    try:
        review = normalize_review(json.loads(payload))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    store = load_store()
    store.setdefault("reviews", []).append(review)
    store["reviews"].sort(key=lambda r: r.get("timestamp", ""))
    save_store(store)

    print(f"Appended review {review['id']} -> {DATA_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
