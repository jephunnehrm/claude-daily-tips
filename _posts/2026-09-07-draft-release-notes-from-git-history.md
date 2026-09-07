---
layout: post
title: "Draft Release Notes from Git History"
date: 2026-09-07
type: how-to
summary: "Transform your git commit messages into structured release notes with Claude Code, saving manual effort."
image: "/claude-daily-tips/assets/images/2026-09-07-draft-release-notes-from-git-history.jpg"
tags:
  - claude-code
  - cli
  - git
  - productivity
  - automation
---



![Draft Release Notes from Git History](/claude-daily-tips/assets/images/2026-09-07-draft-release-notes-from-git-history.jpg)



Manually updating `CHANGELOG.md` with every commit can be a significant time sink, leading to outdated entries and user frustration. The process of deciphering commit messages, categorizing them, and crafting user-friendly descriptions is tedious and prone to errors. Fortunately, you can automate the drafting of these essential release notes by leveraging Claude Code to process your Git history.

The core strategy involves feeding recent commit messages to Claude Code and instructing it to synthesize them into a release note format. A practical starting point is to fetch commits since your last Git tag or a specific commit hash. This output can then be directly piped into the `claude` CLI. For instance, to generate notes from commits made since the last tag, you would use a command similar to this:

```bash
git log --pretty=format:"- %s" $(git describe --tags --abbrev=0)..HEAD | claude --input-mode text --prompt "You are a release note writer specializing in user-facing documentation. Summarize the following git commit messages into a concise changelog section. Group similar improvements and bug fixes, and use clear language that a non-technical user can understand. For each item, start with an action verb and focus on the *what* and *why* for the end-user."
```

This command retrieves the subject line of each commit since the most recent tag, formats them as a bulleted list, and then sends this raw text to Claude Code. The `--input-mode text` flag ensures Claude Code treats the input as plain text, while the `--prompt` provides specific context and instructions for transforming the commit messages into valuable release notes, explaining the user benefit of each change.

A critical factor in the success of this approach is the quality and consistency of your commit messages. Cryptic messages like "fix bug" without further context will yield generic or unhelpful release notes. Claude Code's effectiveness is directly proportional to the clarity of its input. You'll likely need to establish clear commit message conventions or be prepared to perform some manual refinement on the generated output. Furthermore, while Claude Code excels at summarization, highly complex or nuanced technical changes might require more precise prompting or a thorough post-generation review to ensure accuracy and user comprehension.

**Try it:** Navigate to a Git repository with at least 5 commits and execute `git log --pretty=format:"- %s" HEAD~5 | claude --input-mode text --prompt "Summarize these commits into release notes for end-users."` to generate a preliminary draft of your release notes.
