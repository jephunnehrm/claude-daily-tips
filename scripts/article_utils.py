"""
Shared utilities for article generation scripts.
Centralises title uniqueness checks, type classification, and frontmatter writing.
"""

import difflib
import re
from pathlib import Path

POSTS_DIR = Path("_posts")
SIMILARITY_THRESHOLD = 0.75

OVERUSED_OPENERS = [
    "Automate", "Supercharge", "Streamline", "Effortless",
    "Turbocharge", "Boost", "Generate", "Scaffold",
]

# --- Title uniqueness ---

def load_published_titles() -> list[str]:
    titles = []
    for path in POSTS_DIR.rglob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("title:"):
                title = line.split("title:", 1)[1].strip().strip('"').strip("'")
                if title:
                    titles.append(title)
                break
    return titles


def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def is_duplicate(candidate: str, published: list[str]) -> tuple[bool, str]:
    norm = normalize(candidate)
    for existing in published:
        if normalize(existing) == norm:
            return True, f"Exact match: '{existing}'"
        ratio = difflib.SequenceMatcher(None, norm, normalize(existing)).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            return True, f"Too similar ({ratio:.0%}) to: '{existing}'"
    return False, ""


# --- Type classification ---

_COMPARISON = [r"\bvs\b", r"when to choose", r"strengths.*rival", r"know when to deploy"]
_TROUBLESHOOTING = [r"n\+1", r"to the rescue", r"madness\?", r"blues\?",
                    r"dependency hell", r"instant error", r"dreading\?"]
_DEEP_DIVE = [r"agentic ai", r"evolving role", r"scoped context", r"mcp server.*cach",
              r"slice and dice", r"powerhouse", r"token.*hawk", r"context window"]
_REAL_WORLD = [r"safely", r"git worktrees?", r"multiple git branch", r"observability",
               r"microservice config", r"eureka.*centrali", r"deploy with confidence"]


def classify_type(title: str) -> str:
    t = title.lower()
    for pat in _COMPARISON:
        if re.search(pat, t):
            return "comparison"
    for pat in _TROUBLESHOOTING:
        if re.search(pat, t):
            return "troubleshooting"
    for pat in _DEEP_DIVE:
        if re.search(pat, t):
            return "deep-dive"
    for pat in _REAL_WORLD:
        if re.search(pat, t):
            return "real-world"
    return "how-to"


# --- Prompt helpers ---

def existing_titles_snippet(published: list[str], limit: int = 20) -> str:
    sample = published[-limit:] if len(published) > limit else published
    return "\n".join(f"- {t}" for t in sample)


def banned_openers_instruction() -> str:
    return (
        "BANNED title openers (do not start with these words): "
        + ", ".join(OVERUSED_OPENERS)
        + ". Instead use specific problem/outcome framing."
    )


# --- Frontmatter builder ---

def build_frontmatter(
    title: str,
    date_str: str,
    article_type: str,
    summary: str,
    image_url: str,
    tags_yaml: str,
) -> str:
    return f"""---
layout: post
title: "{title}"
date: {date_str}
type: {article_type}
summary: "{summary}"
image: "{image_url}"
tags:
{tags_yaml}
---"""
