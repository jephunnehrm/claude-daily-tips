#!/usr/bin/env python3
"""
Validates that every post has all required frontmatter fields.

Required fields: layout, title, date, type, summary, image, tags
Exit 1 if any post is missing a required field.
"""

import sys
from pathlib import Path

POSTS_DIR = Path("_posts")
REQUIRED_FIELDS = {"layout", "title", "date", "type", "summary", "image", "tags"}
VALID_TYPES = {"how-to", "deep-dive", "comparison", "troubleshooting", "real-world"}


def parse_frontmatter(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return fields

    if not lines or lines[0].strip() != "---":
        return fields

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key = line.split(":", 1)[0].strip()
            fields[key] = line.split(":", 1)[1].strip()
    return fields


def main() -> None:
    errors: list[str] = []

    for path in sorted(POSTS_DIR.rglob("*.md")):
        fields = parse_frontmatter(path)
        missing = REQUIRED_FIELDS - set(fields.keys())
        if missing:
            errors.append(f"{path}: missing fields: {sorted(missing)}")

        article_type = fields.get("type", "").strip('"').strip("'")
        if "type" in fields and article_type not in VALID_TYPES:
            errors.append(
                f"{path}: invalid type '{article_type}'. "
                f"Must be one of: {sorted(VALID_TYPES)}"
            )

    if errors:
        print(f"[FAIL] {len(errors)} frontmatter issue(s) found:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print(f"[OK] All {sum(1 for _ in POSTS_DIR.rglob('*.md'))} posts have valid frontmatter.")


if __name__ == "__main__":
    main()
