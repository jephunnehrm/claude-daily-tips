---
layout: post
title: "Find N+1 Queries in Slow Logs with Claude Code"
date: 2026-10-22
type: how-to
summary: "Quickly pinpoint inefficient N+1 database query patterns by analyzing your application's slow query logs."
image: "/claude-daily-tips/assets/images/2026-10-22-find-n-1-queries-in-slow-logs-with-claude-code.jpg"
tags:
  - claude-code
  - cli
  - productivity
  - java
  - spring
---



![Find N+1 Queries in Slow Logs with Claude Code](/claude-daily-tips/assets/images/2026-10-22-find-n-1-queries-in-slow-logs-with-claude-code.jpg)



Debugging slow API endpoints often leads developers into the labyrinth of database logs, where the tell-tale signs of the N+1 query problem — a primary query followed by a cascade of repetitive, similar sub-queries — can be hidden. Manually sifting through these logs to untangle this performance bottleneck is not only time-consuming but also prone to human error. Fortunately, Claude Code can significantly accelerate this process by automating the analysis of your slow query logs.

The efficacy of this approach lies in Claude Code's natural language processing capabilities. By feeding it your application's slow query logs, you can instruct it to identify patterns characteristic of the N+1 problem. This typically involves recognizing a distinct initial query that fetches a collection of records, immediately followed by a loop of nearly identical queries, each targeting an individual record from that collection, often sharing the same `WHERE` clause parameters. Claude Code can discern this repetitive structure far more efficiently than manual inspection.

To put this into practice, save your slow query logs to a file, say `slow_queries.log`. Then, using the `claude` CLI, you can prompt Claude Code to analyze this file. For instance, a prompt like this would guide the analysis:

```bash
claude analyze ./slow_queries.log --prompt "Examine this slow query log. I'm looking for the N+1 query anti-pattern. Specifically, find instances where a query retrieves a list of IDs or records, followed by many subsequent queries that use those individual IDs in their WHERE clauses. Please present the identified problematic query pairs and explain why they indicate an N+1 issue."
```

It's crucial to understand that Claude Code's accuracy is directly tied to the consistency and detail of your slow query logs. If your logs have highly variable formatting, or if the queries themselves are complex or heavily obfuscated (e.g., using dynamic SQL that Claude can't easily parse), the model may struggle to reliably identify the N+1 pattern. There's also a risk of false positives: legitimate bulk operations that might appear repetitive if log entries aren't sufficiently distinct could be flagged. Therefore, always critically review Claude Code's findings and validate them against your application's source code.

**Try it:** Copy a few representative lines from your actual slow query logs into a file named `my_slow_queries.log`. Then execute: `claude analyze ./my_slow_queries.log --prompt "Find N+1 query patterns in these logs, highlighting the initial query and the subsequent repeated queries."`
