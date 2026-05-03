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
    'dotnet', 'csharp', 'claude-code', 'productivity', 'devtools',
    'git', 'automation', 'mcp', 'agents', 'azure',
}

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

os.makedirs('_posts/dotnet', exist_ok=True)

# Load topics from JSON file
topics_file = "topics.json"
if not os.path.exists(topics_file):
    raise FileNotFoundError(f"Missing {topics_file}. Please create it with available topics.")

with open(topics_file, 'r') as f:
    topics_config = json.load(f)

# Check if topic is scheduled for today
topic = None
if date_str in topics_config.get('dotnet_scheduled', {}):
    scheduled_topics = topics_config['dotnet_scheduled'][date_str]
    # Handle both single string and list of topics
    if isinstance(scheduled_topics, str):
        scheduled_list = [scheduled_topics]
    else:
        scheduled_list = scheduled_topics if scheduled_topics else []

    # Find first scheduled topic that doesn't have a post yet
    existing_posts = glob.glob(f"_posts/dotnet/{date_str}-*.md")
    existing_slugs = set()
    for post in existing_posts:
        slug = post.split('-', 4)[4].rsplit('.', 1)[0]
        existing_slugs.add(slug)

    for sched_topic in scheduled_list:
        test_slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in sched_topic.lower().replace(' ', '-'))[:50].rstrip('-')
        if test_slug not in existing_slugs:
            topic = sched_topic
            print(f"Using scheduled .NET topic for {date_str}: {topic}")
            break

    if not topic and existing_posts:
        print(f"✅ All scheduled .NET topics for {date_str} already have posts — skipping.")
        exit(0)
    elif not topic:
        raise ValueError(f"No valid topics scheduled for {date_str}")

else:
    # Check if any post exists for today
    existing = glob.glob(f"_posts/dotnet/{date_str}-*.md")
    if existing:
        print(f"✅ .NET post for {date_str} already exists — skipping.")
        exit(0)

    # Pick a random unused topic
    available = topics_config.get('dotnet_available_topics', [])
    used = set(topics_config.get('dotnet_used_topics', []))
    unused_topics = [t for t in available if t not in used]

    if not unused_topics:
        # All topics used, reset the used list
        print("⚠️ All .NET topics used, resetting for new cycle")
        unused_topics = available
        used = set()

    topic = random.choice(unused_topics)
    print(f"Generated random .NET topic for {date_str}: {topic}")

    # Add to used topics
    used.add(topic)
    topics_config['dotnet_used_topics'] = sorted(list(used))

    # Save updated config
    with open(topics_file, 'w') as f:
        json.dump(topics_config, f, indent=2)
    print(f"Updated {topics_file} with used .NET topic")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

prompt = f"""You are an expert .NET developer advocate with deep hands-on experience in ASP.NET Core, C#, and Claude Code.
Write a practical daily tip for .NET developers about: {topic}.

CRITICAL ACCURACY RULES — follow these exactly:
- Only reference real NuGet packages, real .NET CLI commands, and real ASP.NET Core APIs.
- Code examples must use real namespaces and compile — no placeholder stubs.
- Claude Code CLI command is `claude`. Only reference real, documented Claude Code features.
- If unsure whether an API or flag exists, describe the concept without fabricating specifics.

The tip must:
- Open with a real .NET developer pain point or workflow moment
- Include one complete, copy-pasteable code block or CLI command sequence that actually works
- Include a "**Try it:**" line with one concrete action the reader can take right now
- Be 4-5 substantial paragraphs — enough to actually teach the concept

Respond in exactly this format with no extra text:
TITLE: [catchy .NET developer-focused title, max 60 chars]
SUMMARY: [one sentence showing the developer benefit, max 120 chars]
CONTENT: [4-5 paragraphs in markdown as described above, with code block and Try it line]
TAGS: [3-5 comma separated tags from: dotnet, csharp, claude-code, productivity, devtools, git, automation, mcp, agents, azure]
IMAGE_PROMPT: [10-15 word AI image generation prompt, dark tech theme, C# or .NET code aesthetic, no people]
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
    if 'dotnet' not in valid:
        valid.insert(0, 'dotnet')
    return valid if valid else ['dotnet', 'claude-code']


MAX_RETRIES = 3
parsed = {}

for attempt in range(MAX_RETRIES):
    print(f"Calling Gemini API for .NET tip (attempt {attempt + 1}/{MAX_RETRIES})...")
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
        raise Exception(f"Failed to generate valid .NET content after {MAX_RETRIES} attempts: {error}")


title = parsed.get('title', f'.NET Tip {today.strftime("%B %d")}')
summary = parsed.get('summary', '')
content = parsed.get('content', '')
tags_list = normalize_tags(parsed.get('tags', 'dotnet'))
image_prompt = parsed.get('image_prompt', 'dark C# dotnet code terminal purple digital technology')

slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:50].rstrip('-')
filename = f"_posts/dotnet/{date_str}-{slug}.md"

try:
    image_url = download_and_save_image(image_prompt, 'dotnet', date_str, slug)
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

with open(filename, 'w') as f:
    f.write(post)

print(f"✅ Created: {filename}")
