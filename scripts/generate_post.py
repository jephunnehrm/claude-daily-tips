import os
import time
import glob
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'claude-code', 'mcp', 'productivity', 'cli', 'agents',
    'dotnet', 'git', 'automation', 'devtools', 'java', 'spring', 'junit',
}

topics = [
    "Claude Code CLI installation and setup", "navigating Claude Code slash commands",
    "building MCP servers from scratch", "connecting MCP tools to Claude Code",
    "writing effective CLAUDE.md files", "multi-agent pipelines with Claude Code",
    "using Claude Code for code reviews", "Claude Code git workflow automation",
    "debugging faster with Claude Code", "Claude Code context window management",
    "parallel Claude Code sessions with git worktrees", "Claude Code for refactoring legacy code",
    "Claude Code sub-agents and orchestration", "MCP server for database querying",
    "Claude Code for test generation", "using Claude Code hooks",
    "Claude Code for API integration", "MCP filesystem and shell tools",
    "Claude Code project scaffolding", "monitoring Claude Code token usage",
    "Claude Code for .NET and C# development", "MCP tools for Azure DevOps",
    "Claude Code headless and CI mode", "custom slash commands in Claude Code",
    "Claude Code for documentation generation",
    "Claude Code for Spring Boot development",
    "generating JUnit 5 tests with Claude Code",
    "refactoring Java microservices with Claude Code",
    "Claude Code for Gradle and Maven workflows",
]

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

existing = glob.glob(f"_posts/{date_str}-*.md")
if existing:
    print(f"✅ Post for {date_str} already exists: {existing[0]} — skipping.")
    exit(0)

topic = topics[today.timetuple().tm_yday % len(topics)]

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

image_prompt_clean = image_prompt.strip().rstrip('.,;')
pollinations_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}?width=800&height=400&nologo=true&model=flux"
image_url = pollinations_url

try:
    print("🖼️ Downloading image...")
    img_response = requests.get(pollinations_url, timeout=60)
    if img_response.status_code == 200 and img_response.headers.get('content-type', '').startswith('image/'):
        os.makedirs('assets/images', exist_ok=True)
        img_filename = f"assets/images/{date_str}-{slug}.jpg"
        with open(img_filename, 'wb') as f:
            f.write(img_response.content)
        image_url = f"/claude-daily-tips/assets/images/{date_str}-{slug}.jpg"
        print(f"✅ Image saved: {img_filename}")
    else:
        print(f"⚠️ Image download failed: {img_response.status_code}, using direct URL")
except Exception as e:
    print(f"⚠️ Image download error: {e}, using direct URL")

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
