# Article Guidelines — Claude Daily Tips

A practical reference for creating new posts. Follow every section before publishing.

---

## 1. Pre-publish Duplicate Check (Mandatory)

Run the checker before creating a new article:

```bash
# Scan the full archive for existing duplicates
python scripts/check_duplicates.py

# Check a proposed title before you write anything
python scripts/check_duplicates.py --title "Your Proposed Title"
```

A non-zero exit code means do not publish. Fix the title or pick a different topic.

---

## 2. Topic Uniqueness Rules

### One article per specific angle per track

The archive is split into three tracks: **General**, **Java/Spring**, **.NET/C#**. Each track may cover a topic once per distinct angle:

| Track | Example topic | Allowed angle A | Allowed angle B |
|---|---|---|---|
| General | Unit tests | First-time generation | CI integration |
| Java | JUnit | Mockito setup | Testcontainers |
| .NET | NuGet | Outdated detection | Breaking-change prevention |

A second article on the same topic is only valid if it covers a **demonstrably different angle** that could not be added as a section to the existing post.

### Banned topic cluster re-use

These themes are already saturated — do not publish another article in the same cluster without a clearly distinct angle:

| Cluster | Existing count | New articles allowed only if... |
|---|---|---|
| Code review automation | 5 | Covers a new tool or pipeline stage |
| JUnit / test generation | 6 | Covers a new framework or strategy |
| Documentation generation | 4 | Covers a new output format or trigger |
| NuGet management | 3 | Covers a new scenario (e.g., security auditing) |
| MCP filesystem | 2 | Covers a new MCP capability |
| SignalR scaffolding | 2 | Do not add more |

---

## 3. Title Rules

### Do not start with overused words

The following openers are banned (too generic, too many existing articles):

> Automate · Supercharge · Streamline · Effortless · Turbocharge · Boost

Prefer openers that name the problem or the outcome:

| Instead of | Write |
|---|---|
| "Supercharge Your JPA Queries" | "Eliminate N+1 Queries from Your Spring Boot App" |
| "Effortless NuGet Updates" | "Stay Ahead of Breaking NuGet Changes" |
| "Automate Code Reviews" | "Catch Regressions Before They Merge with Claude Hooks" |

### Title must contain the specific problem

Good titles answer "what problem does this solve?" in under ten words.

**Bad:** "Streamline Your .NET Workflow with Claude Code"  
**Good:** "Generate Missing OpenAPI Specs from Your ASP.NET Controllers"

### No synonym substitution

Do not publish a new article that is an existing article with words swapped:

- "Effortless X" → "Hassle-Free X" → "X Without the Pain" are all the same article.

---

## 4. Article Structure (Required Format)

Every post must follow this structure:

```
1. The Problem (1–2 paragraphs)
   - Describe a real, specific pain point a developer would recognise
   - State what goes wrong without the solution

2. The Approach (1 paragraph)
   - Explain the Claude Code technique at a conceptual level
   - Name the specific feature, flag, hook, or command being used

3. Working Example (code block)
   - Runnable code in a realistic scenario
   - Include both the prompt/command AND the expected output or result

4. Gotcha / Trade-off (1 paragraph)
   - One thing that can go wrong, or a limitation to be aware of
   - This is what separates a useful article from a marketing post

5. Try It (1 sentence)
   - A single, concrete action the reader can take right now
```

---

## 5. Quality Rubric

Score your article before submitting. Each dimension is pass/fail.

| Dimension | Pass condition |
|---|---|
| **Specificity** | Targets one precise scenario, not a broad category |
| **Actionability** | Reader can reproduce the result in under 10 minutes |
| **Depth** | Explains WHY the approach works, not just WHAT to type |
| **Uniqueness** | Contains at least one insight not in any existing post |
| **Gotcha coverage** | Names at least one limitation or failure mode |

All five must pass. An article that fails any dimension should be revised before publishing.

---

## 6. Article Types

Each article must be one of these types (add `type:` to frontmatter):

| Type | Purpose | When to use |
|---|---|---|
| `how-to` | Step-by-step walkthrough | New workflow or feature |
| `deep-dive` | Internals or architecture | Explaining why something works |
| `comparison` | X vs Y with decision criteria | Choosing between approaches |
| `troubleshooting` | Problem → diagnosis → fix | Common failure modes |
| `real-world` | Production scenario with trade-offs | Applied, end-to-end example |

---

## 7. Frontmatter Template

```yaml
---
layout: post
title: "<specific problem or outcome, not a generic category>"
date: YYYY-MM-DD
type: how-to          # how-to | deep-dive | comparison | troubleshooting | real-world
summary: "<one sentence: what the reader gains and what specific technique achieves it>"
image: "/claude-daily-tips/assets/images/YYYY-MM-DD-slug.jpg"
tags:
  - claude-code
  - <language or framework>
  - <specific feature area>
---
```

---

## 8. Ideas That Still Have Room

These areas are underrepresented in the current archive:

- **Debugging workflows** — using Claude Code to trace a specific class of bug
- **Security scenarios** — SAST integration, secrets detection, dependency auditing
- **Performance profiling** — using Claude Code to interpret flamegraphs or slow query logs
- **Team workflows** — PR templates, onboarding automation, shared CLAUDE.md strategies
- **Claude Code internals** — how context windows affect results, token budgeting strategies
- **Migration guides** — moving from one framework version to another with Claude Code
- **Failure post-mortems** — what Claude Code got wrong and how to correct it
- **Prompt engineering for code** — patterns that consistently produce better output
