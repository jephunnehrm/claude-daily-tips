import os
import time
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

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
    "Claude Code for documentation generation"
]

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

# Skip if post for today already exists
import glob
existing = glob.glob(f"_posts/{date_str}-*.md")
if existing:
    print(f"✅ Post for {date_str} already exists: {existing[0]} — skipping.")
    exit(0)

topic = topics[today.timetuple().tm_yday % len(topics)]

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

prompt = f"""You are an expert Claude Code and MCP (Model Context Protocol) developer advocate.
Write a practical daily tip for software developers about: {topic}.

The tip should be actionable, specific, and help developers become more proficient with Claude Code and MCP tools in their daily workflow.

Respond in exactly this format with no extra text:
TITLE: [catchy developer-focused title, max 60 chars]
SUMMARY: [one sentence showing the developer benefit, max 120 chars]
CONTENT: [3-4 paragraphs in markdown. Must include at least one real code example, command, or config snippet. Be specific and practical.]
TAGS: [3-5 comma separated tags from: claude-code, mcp, productivity, cli, agents, dotnet, git, automation, devtools]
IMAGE_PROMPT: [10-15 word AI image generation prompt, dark tech theme, terminal or code aesthetic, no people]
"""

payload = {"contents": [{"parts": [{"text": prompt}]}]}

print("Calling Gemini API...")
response = requests.post(url, json=payload)
print(f"Status code: {response.status_code}")

data = response.json()
print(f"Full response: {data}")

if 'candidates' not in data:
    error_msg = data.get('error', {}).get('message', str(data))
    raise Exception(f"Gemini API error: {error_msg}")

text = data['candidates'][0]['content']['parts'][0]['text'].strip()
print(f"Generated text: {text[:200]}")

# Parse sections
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

title = parsed.get('title', f'Claude Tip {today.strftime("%B %d")}')
summary = parsed.get('summary', '')
content = parsed.get('content', '')
tags = parsed.get('tags', 'claude-code, mcp, productivity')
image_prompt = parsed.get('image_prompt', f'claude code terminal dark purple digital technology')

# ✅ slug and date_str defined BEFORE image block
slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:50].rstrip('-')
filename = f"_posts/{date_str}-{slug}.md"

# Download and save image locally
image_prompt_clean = image_prompt.strip().rstrip('.,;')
pollinations_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}?width=800&height=400&nologo=true&model=flux"
image_url = pollinations_url  # fallback

try:
    print(f"🖼️ Downloading image...")
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

tags_yaml = '\n'.join([f'  - {t.strip()}' for t in tags.split(',')])

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
