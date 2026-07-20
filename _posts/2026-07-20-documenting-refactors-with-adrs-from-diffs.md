---
layout: post
title: "Documenting Refactors with ADRs from Diffs"
date: 2026-07-20
type: how-to
summary: "Capture architectural decisions made during refactoring automatically by generating ADRs from Git diffs."
image: "/claude-daily-tips/assets/images/2026-07-20-documenting-refactors-with-adrs-from-diffs.jpg"
tags:
  - claude-code
  - cli
  - git
  - automation
  - productivity
---



![Documenting Refactors with ADRs from Diffs](/claude-daily-tips/assets/images/2026-07-20-documenting-refactors-with-adrs-from-diffs.jpg)



You've just completed a complex refactoring, meticulously updating code to enhance its structure, performance, or maintainability. Now, the challenge is to articulate *why* these changes were essential and the trade-offs you navigated. Manually crafting an Architecture Decision Record (ADR) from a Pull Request diff is often a time-consuming endeavor, prone to overlooking crucial details. Claude Code can significantly streamline this process by interpreting your Git diff and generating a comprehensive ADR draft.

The power of this approach lies in leveraging Claude Code's deep understanding of code evolution. By feeding it your refactoring PR's diff, it can meticulously analyze the "before" and "after" states of your codebase. This allows it to infer the underlying problems that necessitated the refactor and the specific solutions implemented, forming the bedrock of a well-structured ADR and saving you from the laborious task of drafting its descriptive components from scratch.

To leverage this capability, ensure your Claude Code is properly configured and have your Git diff readily available. The most efficient method involves using the `claude` CLI with a prompt specifically designed to generate an ADR from your diff. You can pipe the output of `git diff` directly into the `claude` command for seamless integration.

```bash
git diff HEAD~1 HEAD | claude --model claude-3-sonnet-20240229 --prompt "Generate an Architecture Decision Record (ADR) for the following code diff. Focus on the 'Motivation' and 'Decision' sections, explaining the problem being solved and the architectural choice made. Assume this diff represents a refactoring aimed at improving code clarity and reducing technical debt."
```

A key consideration is that Claude Code excels at understanding code syntax and structure. However, it may not inherently grasp *external* business imperatives or subtle architectural constraints that aren't explicitly manifest in the code itself. Consequently, while the generated ADR provides an exceptional starting point, it's crucial to review and enrich it with non-code-related context to ensure its completeness and accuracy.

**Try it:** Make a small refactoring change in a local Git repository, commit it, and then run the `git diff` command piped into `claude` with a similar prompt.
