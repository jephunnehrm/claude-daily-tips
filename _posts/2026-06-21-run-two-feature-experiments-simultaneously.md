---
layout: post
title: "Run Two Feature Experiments Simultaneously"
date: 2026-06-21
type: how-to
summary: "Use Claude Code worktrees to test parallel feature branches without disruptive context switching."
image: "/claude-daily-tips/assets/images/2026-06-21-run-two-feature-experiments-simultaneously.jpg"
tags:
  - claude-code
  - git
  - productivity
  - cli
  - devtools
---



![Run Two Feature Experiments Simultaneously](/claude-daily-tips/assets/images/2026-06-21-run-two-feature-experiments-simultaneously.jpg)



Switching between Git branches to test two distinct feature ideas often results in a fragmented workflow. You might be tempted to commit half-baked changes just to switch contexts, or struggle to differentiate between stable code and ongoing experiments. Claude Code's `worktree` integration offers a more robust solution, enabling you to maintain separate, active development environments for each experiment directly within your project. This allows you to keep your main branch or one feature branch checked out in your primary terminal, while simultaneously running another experiment in an isolated Claude Code worktree.

The power of this approach lies in leveraging Claude Code's `claude` CLI with the `--worktree` flag. When you initiate a Claude Code session targeting a specific directory that serves as your worktree, Claude Code meticulously associates all its configurations, context, and agent memory with that particular worktree. This isolation is fundamental: modifications within one worktree's Claude Code session—whether code edits, tool configurations, or even the agent's conversational history—remain completely independent of other sessions. By running `claude` multiple times, each directed to a distinct worktree directory, you achieve true parallel experimentation.

To implement this, begin by creating dedicated directories for your worktrees. Assuming your main project resides in `my-project`, and you're experimenting with feature A and feature B, you would create subdirectories like `my-project/feature-a` and `my-project/feature-b`. Utilize Git's `worktree` command to check out the respective feature branches into these new directories. Subsequently, launch separate Claude Code sessions for each experiment.

```bash
# Navigate to your primary project directory
cd my-project

# Create separate Git worktrees for each feature branch
git worktree add feature-a feature-a-branch
git worktree add feature-b feature-b-branch

# Launch Claude Code for the first experiment in its dedicated worktree
claude --worktree feature-a

# In a *separate terminal window*, launch Claude Code for the second experiment
claude --worktree feature-b
```

A crucial limitation to acknowledge is that while Claude Code isolates individual sessions and their immediate contexts, fundamental Git repository configurations, such as those in `.git/config`, are shared across all worktrees. Consequently, changes to global Git settings could unintentionally impact every worktree. Furthermore, dependency management can introduce complexity if each worktree necessitates entirely different dependency versions. You'll need to ensure your build and development tooling are configured to correctly resolve dependencies within each isolated worktree environment.

**Try it:** Create a new Git worktree for a dummy branch, then launch `claude --worktree <your-new-worktree-dir>` in a separate terminal and observe the isolated session.
