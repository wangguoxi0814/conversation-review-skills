#!/usr/bin/env python3
"""Render conversation review HTML report from datastore."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = SKILL_ROOT / "data" / "reviews.json"
TEMPLATE_FILE = SKILL_ROOT / "assets" / "report-template.html"
DEFAULT_OUTPUT = SKILL_ROOT / "data" / "report.html"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate HTML report from reviews.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output HTML path")
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="Reviews JSON path")
    args = parser.parse_args()

    if not TEMPLATE_FILE.exists():
        print(f"Template not found: {TEMPLATE_FILE}", file=__import__("sys").stderr)
        return 1

    store = {"version": 1, "reviews": []}
    if args.data.exists():
        store = json.loads(args.data.read_text(encoding="utf-8"))

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    injection = f"window.__REVIEW_DATA__ = {json.dumps(store, ensure_ascii=False)};"
    html = template.replace("/*__REVIEW_DATA__*/", injection)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Report written -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
