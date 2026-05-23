#!/usr/bin/env python3
"""
Pre-publish duplicate checker for Claude Daily Tips.

Usage:
    python scripts/check_duplicates.py
    python scripts/check_duplicates.py --title "Your Proposed Title"

Exit codes:
    0 = no blocking issues (warnings are informational only)
    1 = exact duplicate title detected
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

POSTS_DIR = Path("_posts")

# Threshold for fuzzy similarity warnings (informational, not blocking).
SIMILARITY_WARN = 0.82

# Boilerplate phrases stripped before similarity comparison so that
# "Supercharge Reviews with Claude Code" and "Supercharge Unit Tests with
# Claude Code" are not false-positively flagged as duplicates.
BOILERPLATE = re.compile(
    r"\b(with|using|via)\s+(claude\s*code|claude|mcp)\b"
    r"|\bwith\s+claude\b"
    r"|\bclaud(e)?\s*(code)?\b",
    re.IGNORECASE,
)
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


def normalize_topic(title: str) -> str:
    """Strip boilerplate before fuzzy comparison to reduce false positives."""
    stripped = BOILERPLATE.sub("", title)
    return re.sub(r"\s+", " ", normalize(stripped)).strip()


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
    """Warn when topic-normalised similarity is high (informational only)."""
    topic_norm = normalize_topic(candidate)
    issues = []
    for title, path in published:
        if normalize(title) == normalize(candidate):
            continue  # already caught by exact check
        ratio = difflib.SequenceMatcher(None, topic_norm, normalize_topic(title)).ratio()
        if ratio >= SIMILARITY_WARN:
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
    stop = {"with", "your", "the", "and", "for", "from", "in", "to", "a", "an",
            "of", "on", "by", "is", "are", "using", "use", "make", "get", "claude", "code"}
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
    """Returns True (blocking) only on exact matches."""
    print(f"\nChecking: \"{candidate}\"\n{'=' * 60}")
    blocking = False
    has_warnings = False

    exact = check_exact(candidate, published)
    if exact:
        blocking = True
        print(f"\n[FAIL] Exact matches (BLOCKING):")
        for issue in exact:
            print(issue)

    for label, issues in [
        ("Fuzzy / near-duplicate matches (informational)", check_fuzzy(candidate, published)),
        ("Overused opener words", check_opener(candidate, published)),
        ("Topic keyword overlap (informational)", check_topic_cluster(candidate, published)),
    ]:
        if issues:
            has_warnings = True
            print(f"\n[WARN] {label}:")
            for issue in issues:
                print(issue)

    if not blocking and not has_warnings:
        print("\n[OK] No duplicates or issues found. Safe to publish.")
    elif blocking:
        print("\n[BLOCKED] Fix the exact duplicate before publishing.")
    else:
        print("\n[OK] Warnings above are informational. Safe to publish.")

    return blocking


def scan_all(published: list[tuple[str, Path]]) -> bool:
    """Scans the archive. Only exact duplicates cause exit 1."""
    print(f"Scanning {len(published)} published articles for internal duplicates...\n")
    has_exact = False
    has_similar = False

    seen: dict[str, Path] = {}
    for title, path in published:
        norm = normalize(title)
        if norm in seen:
            print(f"[FAIL] EXACT DUPLICATE:\n  '{title}'\n  {seen[norm]}\n  {path}\n")
            has_exact = True
        else:
            seen[norm] = path

    pairs_checked = set()
    for i, (t1, p1) in enumerate(published):
        for t2, p2 in published[i + 1:]:
            key = (str(p1), str(p2))
            if key in pairs_checked:
                continue
            pairs_checked.add(key)
            if normalize(t1) == normalize(t2):
                continue  # already caught above
            ratio = difflib.SequenceMatcher(
                None, normalize_topic(t1), normalize_topic(t2)
            ).ratio()
            if ratio >= SIMILARITY_WARN:
                print(f"[WARN] SIMILAR ({ratio:.0%}) — review manually:\n  '{t1}'\n  '{t2}'\n  {p1}\n  {p2}\n")
                has_similar = True

    if not has_exact and not has_similar:
        print("[OK] No duplicates found across all published articles.")
    elif has_exact:
        print("[FAIL] Exact duplicates found — fix before merging.")
    else:
        print("[OK] Only similarity warnings found — no blocking issues.")

    return has_exact  # only exact duplicates are blocking


def main() -> None:
    parser = argparse.ArgumentParser(description="Check for duplicate article titles.")
    parser.add_argument("--title", help="Proposed title to check before publishing")
    args = parser.parse_args()

    published = load_published_titles()

    if args.title:
        has_blocking = run_checks(args.title, published)
    else:
        has_blocking = scan_all(published)

    sys.exit(1 if has_blocking else 0)


if __name__ == "__main__":
    main()
