#!/usr/bin/env python3
"""
Pre-publish duplicate checker for Claude Daily Tips.

Usage:
    python scripts/check_duplicates.py
    python scripts/check_duplicates.py --title "Your Proposed Title"

Exit codes:
    0 = no issues found
    1 = duplicates or near-duplicates detected
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

POSTS_DIR = Path("_posts")
SIMILARITY_THRESHOLD = 0.75
OVERUSED_OPENERS = {
    "automate", "supercharge", "streamline", "effortless",
    "turbocharge", "boost", "generate", "scaffold", "effortlessly",
}
MAX_SAME_OPENER = 2


def extract_title(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("title:"):
                return line.split("title:", 1)[1].strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def opener_word(title: str) -> str:
    return title.strip().split()[0].lower().rstrip("!?,.")


def load_published_titles() -> list[tuple[str, Path]]:
    results = []
    for path in sorted(POSTS_DIR.rglob("*.md")):
        title = extract_title(path)
        if title:
            results.append((title, path))
    return results


def check_exact(candidate: str, published: list[tuple[str, Path]]) -> list[str]:
    norm = normalize(candidate)
    return [
        f"  EXACT MATCH: '{title}'\n    -> {path}"
        for title, path in published
        if normalize(title) == norm
    ]


def check_fuzzy(candidate: str, published: list[tuple[str, Path]]) -> list[str]:
    norm = normalize(candidate)
    issues = []
    for title, path in published:
        ratio = difflib.SequenceMatcher(None, norm, normalize(title)).ratio()
        if ratio >= SIMILARITY_THRESHOLD and normalize(title) != norm:
            issues.append(
                f"  SIMILAR ({ratio:.0%}): '{title}'\n    -> {path}"
            )
    return issues


def check_opener(candidate: str, published: list[tuple[str, Path]]) -> list[str]:
    word = opener_word(candidate)
    if word not in OVERUSED_OPENERS:
        return []
    count = sum(1 for t, _ in published if opener_word(t) == word)
    if count >= MAX_SAME_OPENER:
        return [
            f"  OVERUSED OPENER: '{word}' already starts {count} published articles."
            f" Choose a more specific or distinct title opener."
        ]
    return []


def check_topic_cluster(candidate: str, published: list[tuple[str, Path]]) -> list[str]:
    """Flag articles whose core keywords overlap heavily with existing ones."""
    stop = {"with", "your", "the", "and", "for", "from", "in", "to", "a", "an",
            "of", "on", "by", "is", "are", "using", "use", "make", "get"}
    cand_words = {w for w in normalize(candidate).split() if w not in stop and len(w) > 3}
    issues = []
    for title, path in published:
        pub_words = {w for w in normalize(title).split() if w not in stop and len(w) > 3}
        overlap = cand_words & pub_words
        if len(overlap) >= 3:
            issues.append(
                f"  TOPIC OVERLAP ({len(overlap)} shared keywords: {overlap}):\n"
                f"    '{title}'\n    -> {path}"
            )
    return issues


def run_checks(candidate: str, published: list[tuple[str, Path]]) -> bool:
    print(f"\nChecking: \"{candidate}\"\n{'=' * 60}")
    found_issues = False

    sections = [
        ("Exact matches", check_exact(candidate, published)),
        ("Fuzzy / near-duplicate matches", check_fuzzy(candidate, published)),
        ("Overused opener words", check_opener(candidate, published)),
        ("Topic keyword overlap", check_topic_cluster(candidate, published)),
    ]

    for label, issues in sections:
        if issues:
            found_issues = True
            print(f"\n[FAIL] {label}:")
            for issue in issues:
                print(issue)

    if not found_issues:
        print("\n[OK] No duplicates or issues found. Safe to publish.")
    else:
        print("\n[BLOCKED] Resolve the issues above before publishing.")

    return found_issues


def scan_all(published: list[tuple[str, Path]]) -> bool:
    print(f"Scanning {len(published)} published articles for internal duplicates...\n")
    found_any = False

    seen: dict[str, Path] = {}
    for title, path in published:
        norm = normalize(title)
        if norm in seen:
            print(f"[FAIL] EXACT DUPLICATE:\n  '{title}'\n  {seen[norm]}\n  {path}\n")
            found_any = True
        else:
            seen[norm] = path

    pairs_checked = set()
    for i, (t1, p1) in enumerate(published):
        for t2, p2 in published[i + 1:]:
            key = (str(p1), str(p2))
            if key in pairs_checked:
                continue
            pairs_checked.add(key)
            ratio = difflib.SequenceMatcher(None, normalize(t1), normalize(t2)).ratio()
            if ratio >= SIMILARITY_THRESHOLD and normalize(t1) != normalize(t2):
                print(f"[WARN] SIMILAR ({ratio:.0%}):\n  '{t1}'\n  '{t2}'\n  {p1}\n  {p2}\n")
                found_any = True

    if not found_any:
        print("[OK] No duplicates found across all published articles.")
    return found_any


def main() -> None:
    parser = argparse.ArgumentParser(description="Check for duplicate article titles.")
    parser.add_argument("--title", help="Proposed title to check before publishing")
    args = parser.parse_args()

    published = load_published_titles()

    if args.title:
        has_issues = run_checks(args.title, published)
    else:
        has_issues = scan_all(published)

    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
