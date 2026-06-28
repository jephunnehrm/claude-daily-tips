---
layout: post
title: "Query Internal Knowledge Base from Claude Code"
date: 2026-06-28
type: how-to
summary: "Integrate Claude Code with your company's REST-based knowledge base to answer developer questions directly."
image: "/claude-daily-tips/assets/images/2026-06-28-query-internal-knowledge-base-from-claude-code.jpg"
tags:
  - claude-code
  - mcp
  - productivity
  - cli
  - agents
---



![Query Internal Knowledge Base from Claude Code](/claude-daily-tips/assets/images/2026-06-28-query-internal-knowledge-base-from-claude-code.jpg)



Ever find yourself digging through internal wikis or documentation just to get a quick answer on how to use a specific company API or library? Claude Code's Model Context Protocol (MCP) allows you to build custom "servers" that can access and process information from your internal systems. By creating an MCP server that queries your company's internal knowledge base via its REST API, you can bring that information directly into your Claude Code sessions, dramatically reducing context switching and speeding up your development workflow.

To achieve this, you'll need to expose your knowledge base as a RESTful service. This service should have endpoints for searching and retrieving information. For example, you might have a `/docs/search?query=<term>` endpoint that returns relevant snippets or full articles. Once this is available, you can configure Claude Code to use this service. The key is defining a custom MCP hook in your `.claude/settings.json` that points to your knowledge base's API and defines how Claude Code should interact with it.

Here’s a snippet of how you might configure a hook in your `.claude/settings.json`. This example assumes your knowledge base API is available at `http://internal-kb.company.com/api/v1` and has a `/search` endpoint that accepts a `q` query parameter.

```json
{
  "hooks": {
    "internal_kb_query": {
      "type": "http",
      "url": "http://internal-kb.company.com/api/v1/search",
      "method": "GET",
      "params": {
        "q": "{{query}}"
      },
      "headers": {
        "Authorization": "Bearer your_internal_api_key"
      },
      "response_path": "$.results[*].content"
    }
  }
}
```

A significant gotcha here is authentication. Internal knowledge bases often require specific API keys or authentication tokens. Ensure your MCP hook configuration includes the necessary headers to authenticate with your knowledge base API securely. Also, pay close attention to the `response_path`. This tells Claude Code how to extract the relevant information from the JSON response of your API; incorrect paths will result in empty or malformed answers. Once configured, you can then use this hook in a Claude Code session. For instance, if you wanted to find information about your company's authentication service, you might invoke it as `/call internal_kb_query { "query": "company authentication service" }`.

Try it: Add the `internal_kb_query` hook configuration to your `.claude/settings.json` and then, in a Claude Code session, try asking a question about a topic covered in your internal knowledge base using the `/call` command.
