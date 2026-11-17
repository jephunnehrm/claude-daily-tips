---
layout: post
title: "Capture Refactoring Rationale with ADRs from Diffs"
date: 2026-11-17
type: how-to
summary: "Automatically document architectural decisions made during refactoring directly from your pull request diffs."
image: "/claude-daily-tips/assets/images/2026-11-17-capture-refactoring-rationale-with-adrs-from-diffs.jpg"
tags:
  - claude-code
  - cli
  - git
  - productivity
  - devtools
---



![Capture Refactoring Rationale with ADRs from Diffs](/claude-daily-tips/assets/images/2026-11-17-capture-refactoring-rationale-with-adrs-from-diffs.jpg)



The inherent challenge of code refactoring lies not just in executing the change, but in preserving the *why* for future teams. Architectural shifts, often driven by subtle but significant technical debt, can easily become lost in the ephemeral nature of commit messages or scattered across communication channels. When faced with a substantial refactoring in a pull request, the initial focus naturally gravitates towards functional correctness. However, understanding the underlying architectural intent is paramount for long-term maintainability and effective knowledge transfer. Manually reconstructing this rationale into an Architecture Decision Record (ADR) after the fact is a time-consuming task, frequently leading to incomplete or entirely forgotten documentation.

This is where generative AI, specifically Claude Code, can significantly streamline the process by assisting in ADR creation directly from a Git diff. By feeding the diff of your refactoring pull request into Claude Code, you can prompt it to analyze the changes and articulate the architectural considerations, bridging the gap between code evolution and structured documentation. This allows for a more efficient transition from diff inspection to a well-formed ADR, ensuring that critical architectural decisions are captured in a standardized, accessible format. The AI can identify key code transformations, infer the problem being addressed, and suggest relevant architectural approaches based on the code modifications.

To initiate this workflow, imagine a refactoring staged in a branch named `feature/refactor-module`, intended for merging into `main`. First, generate the diff locally:

```bash
git diff main..feature/refactor-module > refactor_diff.txt
```

Next, leverage the `claude` CLI to process this diff and generate your ADR. A robust prompt is key to eliciting the desired output:

```bash
cat refactor_diff.txt | claude --prompt "Analyze this Git diff and generate an Architecture Decision Record (ADR) structured with 'Problem', 'Proposed Solution', and 'Consequences' sections. Focus on the architectural motivations behind these code changes, not just their functional effect."
```

**Crucial Consideration:** The quality of Claude Code's output is directly proportional to the clarity and descriptive nature of the input diff. If the diff lacks context regarding the *intent* or the *specific problem* being solved (e.g., recurring performance regressions, unmanageable complexity, security vulnerabilities), the generated ADR might be overly generic or miss essential architectural nuances. It is therefore imperative that your refactoring efforts, as represented in the code changes, are sufficiently self-explanatory to convey the underlying architectural drivers. The generated ADR serves as a draft, requiring human review to validate and enrich with any missing implicit context before being finalized and integrated into your project's documentation. This practice transforms ADR creation from a post-hoc burden into a natural, integrated part of the development and refactoring lifecycle.
