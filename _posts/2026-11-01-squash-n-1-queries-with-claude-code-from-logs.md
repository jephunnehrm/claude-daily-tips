---
layout: post
title: "Squash N+1 Queries with Claude Code from Logs"
date: 2026-11-01
type: how-to
summary: "Identify and fix inefficient database query patterns by analyzing your application's slow query logs using Claude Code."
image: "/claude-daily-tips/assets/images/2026-11-01-squash-n-1-queries-with-claude-code-from-logs.jpg"
tags:
  - claude-code
  - cli
  - productivity
  - devtools
  - dotnet
---



![Squash N+1 Queries with Claude Code from Logs](/claude-daily-tips/assets/images/2026-11-01-squash-n-1-queries-with-claude-code-from-logs.jpg)



You’ve pushed a new feature, and the user reports of sluggish performance start flooding in. When you dive into your application’s slow query logs, a familiar, frustrating pattern emerges: for every request that fetches a list of items, there are dozens, sometimes hundreds, of identical `SELECT` statements. This is the infamous N+1 query problem, a notorious performance bottleneck that can overwhelm your database and cripple application responsiveness. Manually parsing thousands of log lines to confirm this anti-pattern and trace it back to the specific code responsible is a tedious and error-prone ordeal.

Claude Code can dramatically streamline this debugging process by automating the analysis of your slow query logs and pinpointing N+1 query anti-patterns. By feeding your log data into Claude Code, you can harness its understanding of database query structures to rapidly identify suspicious activity. The core idea is to establish a hook that processes your log files and directs Claude Code to search for the characteristic signature of N+1 queries. This works because Claude is trained on vast amounts of code and data, including common performance anti-patterns, allowing it to recognize the repetitive nature and often sequential execution of queries indicative of this problem.

Here's how you can configure a hook in your `.claude/settings.json` file to achieve this automation. This hook will ingest your slow query log file and instruct Claude Code to analyze it, providing specific guidance on the repeated queries and potential code origins.

```json
{
  "hooks": {
    "analyze-nplus1-logs": {
      "command": "claude --input {{.Input}} \"Analyze this slow query log for N+1 query patterns. Identify the specific `SELECT` statement that is being repeated excessively and provide a reasoned hypothesis for the application code section likely responsible for generating this pattern.\"",
      "description": "Analyzes slow query logs for N+1 query anti-patterns and suggests code fixes."
    }
  }
}
```

Once configured, you can trigger this hook directly from your terminal. For instance, if your slow query log resides in `slow_queries.log`, you would execute: `claude analyze-nplus1-logs --input slow_queries.log`. Claude Code will then process the log and deliver its findings. A significant gotcha to be aware of is that the analysis's accuracy is highly dependent on the richness and format of your slow query logs. If the logs lack sufficient detail, such as precise query timings or contextual information about the originating request, Claude Code might struggle to definitively confirm the N+1 pattern or accurately correlate it to specific application code paths, potentially leading to false positives or missed issues.

To test this, create a sample `slow_queries.log` file containing a few examples of repeated `SELECT` statements and run `claude analyze-nplus1-logs --input slow_queries.log`. Observe how Claude Code identifies the pattern and offers its interpretation.
