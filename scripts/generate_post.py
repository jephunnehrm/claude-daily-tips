import os
import time
import glob
import json
import random
import requests
import urllib.parse
from datetime import datetime
from image_utils import download_and_save_image

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'claude-code', 'mcp', 'productivity', 'cli', 'agents',
    'dotnet', 'git', 'automation', 'devtools', 'java', 'spring', 'junit',
}

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

existing = glob.glob(f"_posts/{date_str}-*.md")
if existing:
    print(f"✅ Post for {date_str} already exists: {existing[0]} — skipping.")
    exit(0)

# Load topics from JSON file
topics_file = "topics.json"
if not os.path.exists(topics_file):
    raise FileNotFoundError(f"Missing {topics_file}. Please create it with available topics.")

with open(topics_file, 'r') as f:
    topics_config = json.load(f)

# Check if topic is scheduled for today
if date_str in topics_config.get('scheduled', {}):
    topic = topics_config['scheduled'][date_str]
    print(f"Using scheduled topic for {date_str}: {topic}")
else:
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

prompt = f"""You are an expert Claude Code and MCP (Model Context Protocol) developer advocate with deep hands-on experience.
Write a practical daily tip for software developers about: {topic}.

CRITICAL ACCURACY RULES — follow these exactly:
- The Claude Code CLI command is `claude`. Never use `mcp` as a standalone CLI command.
- Hooks are configured in `.claude/settings.json` under a `hooks` key.
- Slash commands use the `/command` syntax inside a Claude Code session.
- Only reference real, documented Claude Code features, real CLI flags, and real config keys.
- If unsure whether a flag, env var, or API exists, do not include it — omit or describe the concept instead.
- Code examples must be complete and copy-pasteable, not illustrative stubs.

The tip must:
- Open with a real developer pain point or workflow moment (not "Claude Code lets you...")
- Include one complete, copy-pasteable code block, config snippet, or CLI command sequence that actually works
- Include a "**Try it:**" line with one concrete action the reader can take right now
- Be 4-5 substantial paragraphs — enough to actually teach the concept, not just tease it

Respond in exactly this format with no extra text:
TITLE: [catchy developer-focused title, max 60 chars]
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
        for key in ['TITLE', 'SUMMARY', 'CONTENT', 'TAGS', 'IMAGE_PROMPT']:
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


def validate_parsed(parsed):
    for key in ['title', 'summary', 'content', 'tags']:
        if not parsed.get(key, '').strip():
            return False, f"missing required field: {key}"
    word_count = len(parsed['content'].split())
    if word_count < 150:
        return False, f"content too short ({word_count} words, need 150+)"
    return True, None


def normalize_tags(raw_tags):
    tags = [t.strip().lower() for t in raw_tags.split(',')]
    valid = [t for t in tags if t in ALLOWED_TAGS]
    return valid if valid else ['claude-code']


MAX_RETRIES = 3
parsed = {}

for attempt in range(MAX_RETRIES):
    print(f"Calling Gemini API (attempt {attempt + 1}/{MAX_RETRIES})...")
    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
    print(f"Status: {response.status_code}")
    data = response.json()

    if 'candidates' not in data:
        error_msg = data.get('error', {}).get('message', str(data))
        if attempt < MAX_RETRIES - 1:
            print(f"API error, retrying: {error_msg}")
            time.sleep(5)
            continue
        raise Exception(f"Gemini API error: {error_msg}")

    text = data['candidates'][0]['content']['parts'][0]['text'].strip()
    print(f"Generated text preview: {text[:200]}")
    parsed = parse_response(text)
    valid, error = validate_parsed(parsed)

    if valid:
        print("✅ Validation passed")
        break

    if attempt < MAX_RETRIES - 1:
        print(f"⚠️ Validation failed ({error}), retrying...")
        time.sleep(3)
    else:
        raise Exception(f"Failed to generate valid content after {MAX_RETRIES} attempts: {error}")


title = parsed.get('title', f'Claude Tip {today.strftime("%B %d")}')
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

post = f"""---
layout: post
title: "{title}"
date: {date_str}
summary: "{summary}"
image: "{image_url}"
tags:
{tags_yaml}
---



![{title}]({image_url})



{content}
"""

os.makedirs('_posts', exist_ok=True)
with open(filename, 'w') as f:
    f.write(post)

print(f"✅ Created: {filename}")
