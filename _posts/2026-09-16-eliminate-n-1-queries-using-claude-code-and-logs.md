---
layout: post
title: "Eliminate N+1 Queries Using Claude Code and Logs"
date: 2026-09-16
type: how-to
summary: "Find and fix inefficient N+1 database query patterns directly from your application's slow query logs."
image: "/claude-daily-tips/assets/images/2026-09-16-eliminate-n-1-queries-using-claude-code-and-logs.jpg"
tags:
  - claude-code
  - productivity
  - cli
  - dotnet
  - devtools
---



![Eliminate N+1 Queries Using Claude Code and Logs](/claude-daily-tips/assets/images/2026-09-16-eliminate-n-1-queries-using-claude-code-and-logs.jpg)



Slow database queries cripple application performance, and the insidious N+1 query anti-pattern is a primary offender. This occurs when your application executes one query to fetch a collection of items, followed by N separate queries to retrieve related data for each individual item, instead of a single, optimized join. Manually sifting through slow query logs to detect these patterns is not only time-consuming but also prone to human error. Claude Code, however, can dramatically streamline this process by analyzing your logs and intelligently pinpointing these inefficient query patterns.

To effectively leverage Claude Code for N+1 query detection, you'll configure a custom hook within your Claude Code setup. This hook will direct Claude Code to ingest your slow query logs, identify query sequences exhibiting N+1 characteristics—typically a bulk retrieval followed by numerous individual lookups for related data—and then propose concrete refactoring solutions. For instance, a hook can be trained to recognize a `SELECT * FROM users` query being immediately followed by multiple `SELECT * FROM posts WHERE user_id = ?` queries.

Here's an example demonstrating how to configure such a hook in your `.claude/settings.json` file. This snippet assumes your slow query logs are accessible and contain clear indicators of N+1 issues. The core of the hook is its prompt, which guides Claude Code on what to look for and how to present its findings.

```json
{
  "hooks": {
    "analyze-nplus1-logs": {
      "description": "Analyzes slow query logs for N+1 query patterns and suggests optimizations.",
      "command": "claude analyze --prompt \"Analyze the provided slow query log entries for the N+1 query anti-pattern. For each detected pattern, explain the root cause (e.g., fetching a list of users and then making separate queries for each user's posts) and recommend specific refactoring strategies like eager loading via your ORM or constructing a single JOIN query. Prioritize clarity and actionable advice for a developer.\"",
      "args": {
        "log_file": "--log-file"
      }
    }
  }
}
```

A key consideration for success is the quality and format of the log data fed to Claude Code. Inconsistent log formatting or highly complex, dynamically generated queries can challenge Claude Code's pattern recognition. You might need to pre-process your logs or refine the prompt within the hook, tailoring it to your specific ORM (e.g., SQLAlchemy, Eloquent) and database dialect (e.g., PostgreSQL, MySQL) for optimal accuracy. For example, explicitly mentioning your ORM's eager loading methods in the prompt can yield more precise suggestions. To try this, gather a sample of your application's slow query logs that you suspect contains N+1 issues, and then execute: `claude analyze --log-file /path/to/your/slow_queries.log` to simulate the hook's execution.
