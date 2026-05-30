---
layout: post
title: "Detect N+1 Database Queries from Slow Logs"
date: 2026-05-30
type: how-to
summary: "Use Claude Code to analyze application slow query logs and pinpoint N+1 database query issues."
image: "/claude-daily-tips/assets/images/2026-05-30-detect-n-1-database-queries-from-slow-logs.jpg"
tags:
  - claude-code
  - productivity
  - cli
  - java
  - spring
---



![Detect N+1 Database Queries from Slow Logs](/claude-daily-tips/assets/images/2026-05-30-detect-n-1-database-queries-from-slow-logs.jpg)



It's a frustratingly common experience: your application's performance degrades, and a review of your database logs reveals a swarm of repetitive, near-identical queries. This is the tell-tale sign of the N+1 query problem. It occurs when an initial query to fetch a collection of items is followed by a separate, individual query for each item to retrieve its related data. Manually sifting through lengthy slow query logs to uncover these patterns is not only tedious but also prone to human error, often leaving developers guessing at the root cause.

Fortunately, tools like Claude Code can dramatically speed up this diagnostic process. The underlying principle is Claude Code's sophisticated natural language processing and pattern recognition capabilities. By feeding your slow query logs into Claude Code, you can instruct it to actively search for the distinct signature of an N+1 anti-pattern. This typically involves identifying a "parent" query that retrieves a set of records, immediately followed by a high volume of "child" queries that are nearly identical and likely fetching data for each of those parent records.

To initiate this analysis, you'll need a slow query log file, for example, `slow_queries.log`. Then, within a Claude Code session, you can present the log content along with a carefully crafted prompt. The prompt should explicitly guide Claude Code to look for the specific sequence: a query fetching multiple items, then many subsequent queries that appear to be related to those individual items.

Here’s an example prompt you can use. Ensure you have your log file ready and then execute the command:

```bash
cat slow_queries.log | claude --message "Analyze this slow query log and identify potential N+1 database query patterns. Specifically, look for a query that retrieves a list of items, followed by a large number of similar queries fetching related data for each item in the list. For each pattern found, identify the parent query and a sample of the repetitive child queries."
```

It's crucial to understand the limitations. Claude Code's accuracy hinges on the clarity and consistency of your slow query logs. If logs are poorly formatted, heavily obfuscated, or if the N+1 pattern is unusually complex or spread across a vast log file, Claude Code may require more precise prompting to isolate the issue. Moreover, Claude Code acts as a powerful diagnostic assistant, pinpointing *where* the problem lies, but it won't automatically refactor your application code to resolve the N+1 queries. You'll still need to implement the code changes yourself.

**Experimentation:** To see this in action, copy a section of your application's slow query log into a file named `my_slow_queries.log`. Then, run the following command: `cat my_slow_queries.log | claude --message "Examine these slow queries for N+1 patterns and highlight any potential issues."` Observe how Claude Code interprets the log and identifies potential N+1 scenarios.
