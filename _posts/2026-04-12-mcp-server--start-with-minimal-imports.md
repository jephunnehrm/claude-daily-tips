---
layout: post
title: "MCP Server: Start with Minimal Imports"
date: 2026-04-12
summary: "Boost your MCP server startup by focusing only on essential imports for quicker iteration and cleaner code."
image: "/claude-daily-tips/assets/images/2026-04-12-mcp-server--start-with-minimal-imports.jpg"
tags:
  - mcp
  - claude-code
  - dotnet
  - productivity
  - devtools
---



![MCP Server: Start with Minimal Imports](/claude-daily-tips/assets/images/2026-04-12-mcp-server--start-with-minimal-imports.jpg)



When building an MCP server from scratch, the temptation is to import every possible utility. Fight this impulse! Begin with only the absolute necessities for your server's core functionality. For a basic HTTP server, this means primarily your MCP server type and maybe a logger. This lean approach drastically reduces compile times and makes your initial code easier to reason about. You can always add more imports as your feature set expands.

Consider a minimal C# MCP server. You'll likely only need `Microsoft.SemanticKernel` and `Microsoft.SemanticKernel.Connectors.OpenAI`.

```csharp
// Using only essential imports for an MCP server
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;

var builder = WebApplication.CreateBuilder(args);

// Configure services and add MCP features here

var app = builder.Build();

// Configure request pipeline here

app.Run();
```

This focused start allows you to quickly define your `KernelBuilder` and configure your AI services without the noise of unused dependencies. As you integrate specific plugins or advanced features, you'll naturally add more targeted imports. This iterative import strategy not only speeds up development but also promotes a more maintainable codebase.
