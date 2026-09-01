---
layout: post
title: "Document Refactoring Changes with ADRs"
date: 2026-09-01
type: how-to
summary: "Automatically create Architecture Decision Records from your refactoring PR diffs to maintain project knowledge."
image: "/claude-daily-tips/assets/images/2026-09-01-document-refactoring-changes-with-adrs.jpg"
tags:
  - claude-code
  - cli
  - git
  - productivity
  - devtools
---



![Document Refactoring Changes with ADRs](/claude-daily-tips/assets/images/2026-09-01-document-refactoring-changes-with-adrs.jpg)



As developers, we often wrestle with the "why" behind architectural changes, particularly during extensive refactoring. Relying on fragmented commit messages and pull request descriptions can lead to lost context and a significant knowledge gap over time. While Architecture Decision Records (ADRs) are the established solution for codifying these choices, manually generating them post-refactor is a time-consuming and often neglected task. This is where Claude Code can streamline the process, enabling you to derive ADRs directly from the code diffs of your pull requests.

The fundamental principle is to harness Claude Code's ability to interpret code changes and articulate their architectural implications. By feeding it the diff between your refactoring branch and the main branch, you can prompt it to identify key architectural shifts, infer their underlying rationale (which you may need to subtly guide with your prompt), and anticipate potential consequences. This transforms a passive comparison of code into an active, structured documentation artifact.

To implement this, you'll need a way to deliver the diff to Claude Code. A practical approach involves using your Git client to generate the diff output and then piping it to the `claude` CLI. For a more integrated experience, consider configuring a hook within your `.claude/settings.json` file. It's crucial to recognize that Claude Code is an AI assistant; it may not always perfectly grasp the nuanced architectural "why" if that reasoning isn't explicitly present in code comments or commit messages within the diff. Therefore, always review and refine the generated ADR for accuracy and completeness, especially concerning underlying business or technical motivations that AI might not infer.

Here's a concrete example to get you started. Ensure you have a `.claude/settings.json` file in your project root with the following configuration:

```json
{
  "hooks": {
    "generate_adr_from_pr_diff": "claude --prompt \"You are an ADR author. Analyze the following Git diff from a refactoring pull request. Identify the key architectural decisions made, the problem they solve, and the proposed solution. Format the output as an Architecture Decision Record (ADR) with sections like 'Title', 'Status', 'Context', 'Decision', and 'Consequences'. Consider the code changes and their implications on the system's architecture. Git Diff: {diff}\""
  }
}
```

Once configured, navigate to your Git repository and execute this command while on your feature branch, comparing it against `main`:

```bash
git diff main..HEAD | claude --hook generate_adr_from_pr_diff
```

This command generates the diff between your current branch (`HEAD`) and `main`, pipes it to `claude`, and invokes the `generate_adr_from_pr_diff` hook. Claude Code will then analyze the diff and, guided by the prompt, produce a draft ADR.

**Give it a try:** On your next refactoring branch, run `git diff main..HEAD | claude --hook generate_adr_from_pr_diff` and carefully examine the generated output, refining it as necessary.
