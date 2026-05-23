#!/usr/bin/env python3
"""
One-time script: classifies existing posts and inserts `type:` into frontmatter.
Safe to re-run — skips posts that already have a type field.

Usage: python scripts/classify_articles.py [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path

POSTS_DIR = Path("_posts")

COMPARISON_PATTERNS = [
    r"\bvs\b", r"when to choose", r"strengths.*rival", r"know when to deploy",
]
TROUBLESHOOTING_PATTERNS = [
    r"n\+1", r"to the rescue", r"madness\?", r"blues\?",
    r"dependency hell", r"instant error", r"dreading\?",
]
DEEP_DIVE_PATTERNS = [
    r"agentic ai", r"your evolving role", r"scoped context", r"mcp server.*cach",
    r"slice and dice", r"sub-agents.*powerhouse", r"token.*hawk",
    r"streamline your.*prompts", r"context window",
]
REAL_WORLD_PATTERNS = [
    r"safely", r"git worktrees?", r"multiple git branch", r"parallel claude",
    r"observability", r"microservice config", r"eureka.*centrali",
    r"feature flags?.*safer", r"deploy with confidence",
]


def classify(title: str) -> str:
    t = title.lower()
    for pat in COMPARISON_PATTERNS:
        if re.search(pat, t):
            return "comparison"
    for pat in TROUBLESHOOTING_PATTERNS:
        if re.search(pat, t):
            return "troubleshooting"
    for pat in DEEP_DIVE_PATTERNS:
        if re.search(pat, t):
            return "deep-dive"
    for pat in REAL_WORLD_PATTERNS:
        if re.search(pat, t):
            return "real-world"
    return "how-to"


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("title:"):
            return line.split("title:", 1)[1].strip().strip('"').strip("'")
    return ""


def already_has_type(text: str) -> bool:
    in_front = False
    for line in text.splitlines():
        if line.strip() == "---":
            if in_front:
                return False
            in_front = True
            continue
        if in_front and line.startswith("type:"):
            return True
    return False


def insert_type(text: str, article_type: str) -> str:
    lines = text.splitlines(keepends=True)
    result = []
    in_front = False
    inserted = False

    for line in lines:
        result.append(line)
        if line.strip() == "---":
            if not in_front:
                in_front = True
            continue
        if in_front and not inserted and line.startswith("date:"):
            result.append(f"type: {article_type}\n")
            inserted = True

    return "".join(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    updated = skipped = 0

    for path in sorted(POSTS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")

        if already_has_type(text):
            skipped += 1
            continue

        title = extract_title(text)
        article_type = classify(title)
        new_text = insert_type(text, article_type)

        if args.dry_run:
            print(f"[DRY] {path}: would set type={article_type} (title: {title})")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"[OK]  {path}: type={article_type}")
        updated += 1

    print(f"\nDone. Updated: {updated}, Already typed: {skipped}")
    if args.dry_run and updated:
        print("Re-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
