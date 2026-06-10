---
layout: post
title: "Uncover Untested Functions with Claude Code"
date: 2026-06-10
type: how-to
summary: "Pinpoint functions lacking test coverage in your codebase using Claude Code and custom hooks."
image: "assets/images/placeholder.jpg"
tags:
  - claude-code
  - cli
  - productivity
  - java
  - junit
---



![Uncover Untested Functions with Claude Code](assets/images/placeholder.jpg)



The sting of uncertainty – "Did I actually test that utility function?" – is a familiar frustration for many developers. In large or fast-moving codebases, manually verifying that every line of logic has been exercised by a test can be a time-consuming and error-prone chore. This oversight can easily lead to subtle bugs slipping into production. Claude Code, empowered by its flexible hook system, offers a proactive solution to unearth these gaps.

By defining custom hooks in your `.claude/settings.json` file, you can automate tasks that run before or after Claude Code analyzes your code. For this specific challenge, we'll utilize a hook that triggers a static analysis tool to report on test coverage. The critical factor is selecting a tool capable of providing granular, function-level coverage insights. For Java projects employing JUnit, tools like JaCoCo are excellent choices as they can generate detailed reports, including XML output, that are readily parsable.

Here's how you can integrate a hook into your `.claude/settings.json` to run JaCoCo and enable Claude Code to process its output. The following hook executes the JaCoCo command-line agent, generating an XML report. This assumes Claude Code is equipped to understand and interpret this specific report format, identifying functions with zero test coverage.

```json
{
  "hooks": {
    "pre_analyze": [
      {
        "name": "Run JaCoCo Coverage Analysis",
        "command": "mvn org.jacoco:jacoco-maven-plugin:report",
        "run_if": "always",
        "capture_output": true,
        "parser": "jacoco_xml"
      }
    ]
  }
}
```

A crucial limitation to be aware of is that this method fundamentally relies on having a coverage tool already configured and integrated into your project's build pipeline. The `parser: "jacoco_xml"` directive is conceptual; Claude Code needs built-in support for parsing specific report formats like JaCoCo's XML output to effectively identify untested functions. If a direct parser isn't available, you might need to develop a custom parsing script to bridge the gap. To experiment, create a `.claude/settings.json` file in your project's root directory, add the `hooks` configuration provided, and then execute `claude analyze .` to observe Claude Code leveraging the generated coverage data.
