import os
import time
import glob
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'java', 'spring', 'junit', 'claude-code', 'productivity', 'devtools',
    'git', 'automation', 'agents',
}

topics = [
    "Claude Code for Spring Boot REST API development",
    "generating JUnit 5 tests with Mockito and Claude Code",
    "Spring Data JPA query optimisation with Claude Code",
    "refactoring Java microservices with Claude Code",
    "Gradle build script automation with Claude Code",
    "Maven dependency management with Claude Code",
    "Spring Security configuration patterns with Claude Code",
    "Hibernate entity mapping and relationships with Claude Code",
    "Spring Boot actuator and observability with Claude Code",
    "Java streams and functional programming with Claude Code",
    "Docker containerisation for Spring Boot with Claude Code",
    "Spring Cloud Config and microservice configuration",
    "Lombok and MapStruct code generation with Claude Code",
    "OpenAPI specification generation in Spring Boot with Claude Code",
    "Spring Batch processing pipelines with Claude Code",
    "reactive programming with Spring WebFlux and Claude Code",
    "Testcontainers integration testing with Claude Code",
    "Spring Cache abstraction patterns with Claude Code",
    "Java design patterns accelerated by Claude Code",
    "Flyway database migrations with Claude Code",
]

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

os.makedirs('_posts/java', exist_ok=True)
existing = glob.glob(f"_posts/java/{date_str}-*.md")
if existing:
    print(f"✅ Java post for {date_str} already exists — skipping.")
    exit(0)

topic = topics[today.timetuple().tm_yday % len(topics)]

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

prompt = f"""You are an expert Java developer advocate with deep hands-on experience in Spring Boot, Java, and Claude Code.
Write a practical daily tip for Java developers about: {topic}.

CRITICAL ACCURACY RULES — follow these exactly:
- Only reference real Maven/Gradle dependencies, real Spring Boot APIs, and real Java standard library classes.
- Code examples must use real package names and compile — no placeholder stubs.
- Claude Code CLI command is `claude`. Only reference real, documented Claude Code features.
- If unsure whether an API or annotation exists, describe the concept without fabricating specifics.

The tip must:
- Open with a real Java developer pain point or workflow moment
- Include one complete, copy-pasteable code block or CLI command sequence that actually works
- Include a "**Try it:**" line with one concrete action the reader can take right now
- Be 4-5 substantial paragraphs — enough to actually teach the concept

Respond in exactly this format with no extra text:
TITLE: [catchy Java developer-focused title, max 60 chars]
SUMMARY: [one sentence showing the developer benefit, max 120 chars]
CONTENT: [4-5 paragraphs in markdown as described above, with code block and Try it line]
TAGS: [3-5 comma separated tags from: java, spring, junit, claude-code, productivity, devtools, git, automation, agents]
IMAGE_PROMPT: [10-15 word AI image generation prompt, dark tech theme, Java or Spring code aesthetic, no people]
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
    if 'java' not in valid:
        valid.insert(0, 'java')
    return valid if valid else ['java', 'claude-code']


MAX_RETRIES = 3
parsed = {}

for attempt in range(MAX_RETRIES):
    print(f"Calling Gemini API for Java tip (attempt {attempt + 1}/{MAX_RETRIES})...")
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
        raise Exception(f"Failed to generate valid Java content after {MAX_RETRIES} attempts: {error}")


title = parsed.get('title', f'Java Tip {today.strftime("%B %d")}')
summary = parsed.get('summary', '')
content = parsed.get('content', '')
tags_list = normalize_tags(parsed.get('tags', 'java'))
image_prompt = parsed.get('image_prompt', 'dark Java Spring Boot code terminal green digital technology')

slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:50].rstrip('-')
filename = f"_posts/java/{date_str}-{slug}.md"

image_prompt_clean = image_prompt.strip().rstrip('.,;')
pollinations_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}?width=800&height=400&nologo=true&model=flux"
image_url = pollinations_url

try:
    print("🖼️ Downloading image...")
    img_response = requests.get(pollinations_url, timeout=60)
    if img_response.status_code == 200 and img_response.headers.get('content-type', '').startswith('image/'):
        os.makedirs('assets/images', exist_ok=True)
        img_filename = f"assets/images/java-{date_str}-{slug}.jpg"
        with open(img_filename, 'wb') as f:
            f.write(img_response.content)
        image_url = f"/claude-daily-tips/assets/images/java-{date_str}-{slug}.jpg"
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
