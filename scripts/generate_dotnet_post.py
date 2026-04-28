import os
import time
import glob
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'dotnet', 'csharp', 'claude-code', 'productivity', 'devtools',
    'git', 'automation', 'mcp', 'agents', 'azure',
}

topics = [
    "Claude Code for ASP.NET Core minimal APIs",
    "scaffolding Blazor components with Claude Code",
    "Entity Framework Core query optimization with Claude Code",
    "generating xUnit and integration tests with Claude Code",
    "Clean Architecture patterns in .NET with Claude Code",
    "MAUI cross-platform app development with Claude Code",
    "SignalR real-time feature scaffolding with Claude Code",
    "dependency injection patterns in .NET with Claude Code",
    "Polly resilience and retry policies with Claude Code",
    "OpenTelemetry tracing in ASP.NET Core with Claude Code",
    "NuGet package management and updates with Claude Code",
    "LINQ query refactoring with Claude Code",
    "ASP.NET Core middleware pipeline with Claude Code",
    "Dapper micro-ORM patterns with Claude Code",
    "background services and hosted workers in .NET with Claude Code",
    "gRPC service development in .NET with Claude Code",
    "health checks and readiness probes in ASP.NET Core",
    "feature flags with Microsoft.FeatureManagement and Claude Code",
    "rate limiting and throttling in ASP.NET Core with Claude Code",
    "minimal API endpoint organisation patterns with Claude Code",
]

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

os.makedirs('_posts/dotnet', exist_ok=True)
existing = glob.glob(f"_posts/dotnet/{date_str}-*.md")
if existing:
    print(f"✅ .NET post for {date_str} already exists — skipping.")
    exit(0)

topic = topics[today.timetuple().tm_yday % len(topics)]

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

image_prompt_clean = image_prompt.strip().rstrip('.,;')
pollinations_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}?width=800&height=400&nologo=true&model=flux"
image_url = pollinations_url

try:
    print("🖼️ Downloading image...")
    img_response = requests.get(pollinations_url, timeout=60)
    if img_response.status_code == 200 and img_response.headers.get('content-type', '').startswith('image/'):
        os.makedirs('assets/images', exist_ok=True)
        img_filename = f"assets/images/dotnet-{date_str}-{slug}.jpg"
        with open(img_filename, 'wb') as f:
            f.write(img_response.content)
        image_url = f"/claude-daily-tips/assets/images/dotnet-{date_str}-{slug}.jpg"
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

with open(filename, 'w') as f:
    f.write(post)

print(f"✅ Created: {filename}")
