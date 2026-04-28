import os
import time
import glob
import requests
import urllib.parse
from datetime import datetime

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

ALLOWED_TAGS = {
    'claude-code', 'mcp', 'dotnet', 'azure', 'agents', 'architecture',
    'devtools', 'productivity', 'git', 'automation', 'csharp', 'openai',
    'rag', 'identity', 'java', 'spring', 'junit',
}

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')
week_number = today.isocalendar()[1]

series_rotation = [
    {
        "id": "foundations",
        "name": "Claude Code Foundations",
        "topics": [
            "Claude Code installation, setup and first project walkthrough",
            "Mastering CLAUDE.md — structuring project context for AI",
            "Slash commands and custom workflow automation in Claude Code",
            "Context window management strategies for large codebases",
            "Claude Code permissions, trust model and security best practices",
            "Headless and CI mode — running Claude Code in pipelines",
        ]
    },
    {
        "id": "mcp-deep-dive",
        "name": "MCP Deep Dive",
        "topics": [
            "MCP architecture — how servers, clients and tools connect",
            "Building your first MCP server from scratch with Node.js",
            "MCP filesystem and shell tools for real developer workflows",
            "MCP server for database querying and schema introspection",
            "Connecting multiple MCP tools to Claude Code simultaneously",
            "Publishing and sharing MCP servers with your team",
        ]
    },
    {
        "id": "agent-pipelines",
        "name": "Agent Pipelines and Orchestration",
        "topics": [
            "Multi-agent pipeline design — orchestrator and sub-agent patterns",
            "Parallel Claude Code sessions using git worktrees",
            "Building a Product Owner to QA software delivery pipeline",
            "Error handling, retries and recovery strategies in agent pipelines",
            "Token optimization and cost control in multi-agent systems",
            "Evaluating and testing agent pipeline outputs automatically",
        ]
    },
    {
        "id": "dotnet-and-claude",
        "name": ".NET and Claude Code",
        "topics": [
            "Claude Code for ASP.NET Core — scaffolding, refactoring and review",
            "Generating xUnit and integration tests with Claude Code",
            "Clean Architecture in .NET accelerated by Claude Code",
            "Entity Framework Core migrations and query optimization with Claude",
            "OpenTelemetry and AI-powered diagnostics in .NET applications",
            "Duende IdentityServer patterns and OAuth 2.0 flows with Claude Code",
        ]
    },
    {
        "id": "azure-ai-integration",
        "name": "Azure AI Integration",
        "topics": [
            "Azure OpenAI vs Claude API — architecture decision guide",
            "Claude Code with Azure DevOps — PR reviews and pipeline automation",
            "Building RAG pipelines with Azure AI Search and Claude",
            "Azure AI Foundry and MCP — connecting enterprise AI to your workflow",
            "Azure Functions as MCP tool endpoints for Claude agents",
            "Hybrid AI architecture — Azure OpenAI and Claude working together",
        ]
    },
    {
        "id": "patterns-and-architecture",
        "name": "AI Patterns and Architecture",
        "topics": [
            "When to use agents vs direct Claude API calls — decision framework",
            "Prompt engineering patterns for developer productivity tools",
            "Security patterns for MCP servers and AI pipelines",
            "Observability and monitoring for AI-powered applications",
            "Cost modelling and token budgeting for production AI systems",
            "Designing self-healing and adaptive AI workflows",
        ]
    },
    {
        "id": "java-and-claude",
        "name": "Java and Claude Code",
        "topics": [
            "Claude Code for Spring Boot — scaffolding REST APIs and services",
            "Generating JUnit 5 and Mockito tests with Claude Code",
            "Refactoring Java microservices with Claude Code",
            "Gradle and Maven build automation with Claude Code",
            "Java design patterns and clean code accelerated by Claude Code",
            "OpenTelemetry and observability in Java apps with Claude",
        ]
    },
]

series_index = week_number % len(series_rotation)
series = series_rotation[series_index]
topic_index = (week_number // len(series_rotation)) % len(series["topics"])
topic = series["topics"][topic_index]
series_id = series["id"]
series_name = series["name"]

week_str = f"week{week_number}"
existing_week = glob.glob(f"_playbook/{series_id}-{week_str}-*.md")
if existing_week:
    print(f"✅ Chapter for week {week_number} already exists — skipping.")
    exit(0)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

prompt = f"""You are a senior software architect and developer advocate specialising in Claude Code, MCP, .NET, Java, and Azure AI.

Write a deep-dive playbook chapter for experienced developers about: {topic}
This chapter is part of the series: {series_name}

CRITICAL ACCURACY RULES — follow these exactly:
- The Claude Code CLI command is `claude`. Never use `mcp` as a standalone CLI command.
- Only reference real Claude Code CLI flags, real MCP SDK APIs, real NuGet/Maven package names, and real Azure service names.
- All code examples must be complete and runnable — no placeholder-only stubs marked "conceptual".

The chapter must:
- Start with a ## TL;DR section containing 3-5 bullet points summarising what the reader will learn
- Be practical AND architectural — show both how to use it and how to design systems around it
- Include real code examples, config snippets, or CLI commands that actually work
- Include a ## Anti-patterns section showing 2-3 things developers commonly get wrong and why
- Cover common pitfalls and how to avoid them
- Be 1200-1600 words in markdown with ## subheadings and code blocks
- Feel like a senior engineer wrote it, not a tutorial blog post

Respond in exactly this format with no extra text:
TITLE: [clear chapter title, max 70 chars]
SUMMARY: [2 sentences describing what the reader will learn]
CONTENT: [full chapter content in markdown with ## subheadings, code blocks, TL;DR, and Anti-patterns sections]
TAGS: [4-6 comma separated tags from: claude-code, mcp, dotnet, azure, agents, architecture, devtools, productivity, git, automation, csharp, openai, rag, identity, java, spring, junit]
IMAGE_PROMPT: [10-15 word AI image generation prompt, dark tech theme, architectural diagram aesthetic, no people]
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
    if word_count < 400:
        return False, f"content too short ({word_count} words, need 400+)"
    return True, None


def normalize_tags(raw_tags):
    tags = [t.strip().lower() for t in raw_tags.split(',')]
    valid = [t for t in tags if t in ALLOWED_TAGS]
    return valid if valid else ['claude-code', 'architecture']


MAX_RETRIES = 3
parsed = {}

for attempt in range(MAX_RETRIES):
    print(f"📖 Generating chapter: {topic} (attempt {attempt + 1}/{MAX_RETRIES})")
    print(f"📚 Series: {series_name}")
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


title = parsed.get('title', f'{series_name} — Week {week_number}')
summary = parsed.get('summary', '')
content = parsed.get('content', '')
tags_list = normalize_tags(parsed.get('tags', 'claude-code, architecture, devtools'))
image_prompt = parsed.get('image_prompt', f'dark tech architecture diagram {series_id}')

slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in title.lower().replace(' ', '-'))[:60].rstrip('-')
filename = f"_playbook/{series_id}-{week_str}-{slug}.md"

image_prompt_clean = image_prompt.strip().rstrip('.,;')
pollinations_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}?width=800&height=400&nologo=true&model=flux"
image_url = pollinations_url

try:
    print("🖼️ Downloading chapter image...")
    img_response = requests.get(pollinations_url, timeout=60)
    if img_response.status_code == 200 and img_response.headers.get('content-type', '').startswith('image/'):
        os.makedirs('assets/images', exist_ok=True)
        img_filename = f"assets/images/chapter-{series_id}-{week_str}.jpg"
        with open(img_filename, 'wb') as f:
            f.write(img_response.content)
        image_url = f"/claude-daily-tips/assets/images/chapter-{series_id}-{week_str}.jpg"
        print(f"✅ Image saved: {img_filename}")
    else:
        print(f"⚠️ Image failed: {img_response.status_code}")
except Exception as e:
    print(f"⚠️ Image error: {e}")

tags_yaml = '\n'.join([f'  - {t}' for t in tags_list])

chapter = f"""---
layout: chapter
title: "{title}"
date: {date_str}
series: "{series_id}"
series_name: "{series_name}"
week: {week_number}
summary: "{summary}"
image: "{image_url}"
tags:
{tags_yaml}
---



![{title}]({image_url})



{content}
"""

os.makedirs('_playbook', exist_ok=True)
with open(filename, 'w') as f:
    f.write(chapter)

print(f"✅ Chapter created: {filename}")
