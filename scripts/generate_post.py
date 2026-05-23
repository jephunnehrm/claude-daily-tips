import os
import time
import glob
import json
import random
import requests
import urllib.parse
from datetime import datetime
from image_utils import download_and_save_image
from article_utils import (
    load_published_titles, is_duplicate, classify_type,
    existing_titles_snippet, banned_openers_instruction, build_frontmatter,
)

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'claude-code', 'mcp', 'productivity', 'cli', 'agents',
    'dotnet', 'git', 'automation', 'devtools', 'java', 'spring', 'junit',
}

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

# Load topics from JSON file
topics_file = "topics.json"
if not os.path.exists(topics_file):
    raise FileNotFoundError(f"Missing {topics_file}. Please create it with available topics.")

with open(topics_file, 'r') as f:
    topics_config = json.load(f)

# Check if topic is scheduled for today
topic = None
if date_str in topics_config.get('scheduled', {}):
    scheduled_topics = topics_config['scheduled'][date_str]
    # Handle both single string and list of topics
    if isinstance(scheduled_topics, str):
        scheduled_list = [scheduled_topics]
    else:
        scheduled_list = scheduled_topics if scheduled_topics else []

    # Find first scheduled topic that doesn't have a post yet
    existing_posts = glob.glob(f"_posts/{date_str}-*.md")
    existing_slugs = set()
    for post in existing_posts:
        # Extract slug from filename: _posts/YYYY-MM-DD-slug.md
        slug = post.split('-', 3)[3].rsplit('.', 1)[0]
        existing_slugs.add(slug)

    for sched_topic in scheduled_list:
        # Generate slug for this topic to check if post exists
        test_slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in sched_topic.lower().replace(' ', '-'))[:50].rstrip('-')
        if test_slug not in existing_slugs:
            topic = sched_topic
            print(f"Using scheduled topic for {date_str}: {topic}")
            break

    if not topic and existing_posts:
        print(f"✅ All scheduled topics for {date_str} already have posts — skipping.")
        exit(0)
    elif not topic:
        raise ValueError(f"No valid topics scheduled for {date_str}")

else:
    # Check if any post exists for today
    existing = glob.glob(f"_posts/{date_str}-*.md")
    if existing:
        print(f"✅ Post for {date_str} already exists: {existing[0]} — skipping.")
        exit(0)

    # Pick a random unused topic
    available = topics_config.get('available_topics', [])
    used = set(topics_config.get('used_topics', []))
    unused_topics = [t for t in available if t not in used]

    if not unused_topics:
        # All topics used, reset the used list
        print("⚠️ All topics used, resetting for new cycle")
        unused_topics = available
        used = set()

    topic = random.choice(unused_topics)
    print(f"Generated random topic for {date_str}: {topic}")

    # Add to used topics
    used.add(topic)
    topics_config['used_topics'] = sorted(list(used))

    # Save updated config
    with open(topics_file, 'w') as f:
        json.dump(topics_config, f, indent=2)
    print(f"Updated {topics_file} with used topic")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

published_titles = load_published_titles()

prompt = f"""You are an expert Claude Code and MCP (Model Context Protocol) developer advocate with deep hands-on experience.
Write a practical daily tip for software developers about: {topic}.

CRITICAL ACCURACY RULES — follow these exactly:
- The Claude Code CLI command is `claude`. Never use `mcp` as a standalone CLI command.
- Hooks are configured in `.claude/settings.json` under a `hooks` key.
- Slash commands use the `/command` syntax inside a Claude Code session.
- Only reference real, documented Claude Code features, real CLI flags, and real config keys.
- If unsure whether a flag, env var, or API exists, do not include it — omit or describe the concept instead.
- Code examples must be complete and copy-pasteable, not illustrative stubs.

TITLE RULES (mandatory):
- {banned_openers_instruction()}
- Your title MUST be clearly different from every title in the "Already published" list below.
- Frame the title around a specific problem or concrete outcome, not a vague category.

ARTICLE TYPE — choose exactly one: how-to | deep-dive | comparison | troubleshooting | real-world

The tip must:
- Open with a real developer pain point or workflow moment (not "Claude Code lets you...")
- Include one complete, copy-pasteable code block, config snippet, or CLI command sequence
- Name at least one limitation or edge case (the "gotcha")
- Include a "**Try it:**" line with one concrete action the reader can take right now
- Be 4-5 substantial paragraphs — enough to actually teach the concept, not just tease it

Already published (do NOT produce a title similar to any of these):
{existing_titles_snippet(published_titles)}

Respond in exactly this format with no extra text:
TITLE: [specific problem/outcome title, max 60 chars, not starting with a banned opener]
TYPE: [how-to|deep-dive|comparison|troubleshooting|real-world]
SUMMARY: [one sentence showing the developer benefit, max 120 chars]
CONTENT: [4-5 paragraphs in markdown as described above, with code block and Try it line]
TAGS: [3-5 comma separated tags from: claude-code, mcp, productivity, cli, agents, dotnet, git, automation, devtools, java, spring, junit]
IMAGE_PROMPT: [10-15 word AI image generation prompt, dark tech theme, terminal or code aesthetic, no people]
"""


def parse_response(text):
    parsed = {}
    current_key = None
    current_lines = []
    for line in text.split('\n'):
        for key in ['TITLE', 'TYPE', 'SUMMARY', 'CONTENT', 'TAGS', 'IMAGE_PROMPT']:
            if line.startswith(f'{key}:'):
                if current_key:
                    parsed[current_key] = '\n'.join(current_lines).strip()
                current_key = key.lower()
                current_lines = [line[len(key)+1:].strip()]
                break
        else:
            if current_key:
                current_lines.append(line)
    if current_key:
        parsed[current_key] = '\n'.join(current_lines).strip()
    return parsed


def validate_parsed(parsed, published: list[str]):
    for key in ['title', 'summary', 'content', 'tags']:
        if not parsed.get(key, '').strip():
            return False, f"missing required field: {key}"
    word_count = len(parsed['content'].split())
    if word_count < 150:
        return False, f"content too short ({word_count} words, need 150+)"
    dup, reason = is_duplicate(parsed['title'], published)
    if dup:
        return False, f"duplicate title — {reason}"
    return True, None


def normalize_tags(raw_tags):
    tags = [t.strip().lower() for t in raw_tags.split(',')]
    valid = [t for t in tags if t in ALLOWED_TAGS]
    return valid if valid else ['claude-code']


def call_gemini(prompt_text: str) -> str:
    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt_text}]}]})
    data = response.json()
    if 'candidates' not in data:
        raise Exception(data.get('error', {}).get('message', str(data)))
    return data['candidates'][0]['content']['parts'][0]['text'].strip()


def critique_and_improve(draft: dict) -> str:
    critique_prompt = f"""You are a senior developer relations editor reviewing an article draft.
Evaluate the article below and rewrite the CONTENT section only to make it better.

TITLE: {draft.get('title', '')}

CURRENT CONTENT:
{draft.get('content', '')}

Check against these quality gates and fix any that fail:
1. Does the opening sentence name a specific real developer pain point? (not "Claude Code lets you...")
2. Is the code example complete and copy-pasteable — not a stub or pseudocode?
3. Is there a concrete "gotcha" or limitation named — something that would surprise the reader?
4. Does the article explain WHY the approach works, not just WHAT to type?
5. Would a senior developer learn something they couldn't get from reading the docs?

Rewrite the content to pass all five gates. Keep the same length (4-5 paragraphs).
Return ONLY the improved content in markdown — no labels, no commentary."""

    return call_gemini(critique_prompt)


MAX_RETRIES = 3
parsed = {}

for attempt in range(MAX_RETRIES):
    print(f"Calling Gemini API (attempt {attempt + 1}/{MAX_RETRIES})...")
    try:
        text = call_gemini(prompt)
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            print(f"API error, retrying: {e}")
            time.sleep(5)
            continue
        raise

    print(f"Generated text preview: {text[:200]}")
    parsed = parse_response(text)
    valid, error = validate_parsed(parsed, published_titles)

    if valid:
        print("✅ Validation passed — running critique pass...")
        try:
            improved_content = critique_and_improve(parsed)
            parsed['content'] = improved_content
            print("✅ Critique pass complete")
        except Exception as e:
            print(f"⚠️ Critique pass failed (using original): {e}")
        break

    if attempt < MAX_RETRIES - 1:
        print(f"⚠️ Validation failed ({error}), retrying...")
        time.sleep(3)
    else:
        raise Exception(f"Failed to generate valid content after {MAX_RETRIES} attempts: {error}")


title = parsed.get('title', f'Claude Tip {today.strftime("%B %d")}')
article_type = parsed.get('type', classify_type(title)).strip().lower()
summary = parsed.get('summary', '')
content = parsed.get('content', '')
tags_list = normalize_tags(parsed.get('tags', 'claude-code'))
image_prompt = parsed.get('image_prompt', 'claude code terminal dark purple digital technology')

slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:50].rstrip('-')
filename = f"_posts/{date_str}-{slug}.md"

try:
    image_url = download_and_save_image(image_prompt, '', date_str, slug)
except Exception as e:
    print(f"❌ Critical error: Could not download image: {e}")
    raise

tags_yaml = '\n'.join([f'  - {t}' for t in tags_list])
frontmatter = build_frontmatter(title, date_str, article_type, summary, image_url, tags_yaml)

post = f"""{frontmatter}



![{title}]({image_url})



{content}
"""

os.makedirs('_posts', exist_ok=True)
with open(filename, 'w') as f:
    f.write(post)

print(f"✅ Created: {filename}")
