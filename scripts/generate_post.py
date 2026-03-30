import os
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

topics = [
    "writing better prompts", "Claude Code CLI tips", "system prompt design",
    "multi-turn conversation tricks", "Claude for debugging code",
    "Claude for writing and editing", "using Claude artifacts",
    "Claude API best practices", "agentic workflows with Claude",
    "Claude for productivity", "advanced prompting techniques",
    "Claude for data analysis", "Claude memory and context tricks",
    "Claude for brainstorming", "Claude vs other AI tools"
]

today = datetime.now()
topic = topics[today.timetuple().tm_yday % len(topics)]

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

prompt = f"""Write a practical daily tip about Claude AI focused on: {topic}.

Respond in exactly this format with no extra text:
TITLE: [catchy title, max 60 chars]
SUMMARY: [one sentence, max 120 chars]
CONTENT: [3-4 paragraphs in markdown. Include a practical example with code if relevant.]
TAGS: [3-5 comma separated tags]
IMAGE_PROMPT: [10-15 word AI image generation prompt, tech/AI themed, no people]
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
tags = parsed.get('tags', 'claude, ai, tips')
image_prompt = parsed.get('image_prompt', f'claude ai {topic} purple digital technology')

image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt)}?width=800&height=400&nologo=true"

slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:50].rstrip('-')
date_str = today.strftime('%Y-%m-%d')
filename = f"_posts/{date_str}-{slug}.md"

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

print(f"Created: {filename}")
