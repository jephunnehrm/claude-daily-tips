---
layout: post
title: "Add a New Feature Folder to a .NET Monolith Quickly"
date: 2026-06-28
type: how-to
summary: "Use Claude Code CLI to quickly create a structured vertical slice feature folder in your ASP.NET Core monolith."
image: "/claude-daily-tips/assets/images/dotnet-2026-06-28-add-a-new-feature-folder-to-a--net-monolith-quickl.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Add a New Feature Folder to a .NET Monolith Quickly](/claude-daily-tips/assets/images/dotnet-2026-06-28-add-a-new-feature-folder-to-a--net-monolith-quickl.jpg)



Setting up new feature directories within a monolithic ASP.NET Core application can be a tedious and error-prone process, especially when adhering to a vertical slice architecture. Developers often find themselves manually creating identical sets of files for controllers, services, Data Transfer Objects (DTOs), and potentially domain entities for each new feature. This repetitive overhead consumes valuable development time and can lead to inconsistencies across the codebase, particularly when onboarding new team members or quickly iterating on new functionality. Tools that can automate this boilerplate generation are therefore highly sought after.

Claude Code, a command-line interface (CLI) tool, can be a powerful ally in streamlining this setup. By leveraging pre-defined templates, the `claude` CLI can scaffold common architectural patterns, including the structured folder layouts expected by vertical slice designs. This means you can generate the foundational structure and placeholder files for a new feature in a matter of seconds, ensuring consistency and allowing your team to immediately dive into implementing the core business logic. The `claude create` command, when configured with appropriate .NET templates, can interpret project context and rapidly lay the groundwork for your next vertical slice.

Here’s a practical example demonstrating how to scaffold a new feature, such as an "Order Management" system, within your monolith's API project. Assuming you have Claude Code installed and a `.NET` template specifically designed for vertical slices available, you would execute the following command from your monolith's root directory:

```csharp
claude create verticalslice --name OrderManagement --project MyMonolith.Api
```

This command, when executed, would generate a `Features/OrderManagement` directory within your `MyMonolith.Api` project. Inside, you'd typically find subfolders for `Contracts`, `Commands`, `Queries`, and `Endpoints`, along with initial C# files for request/response objects and basic handler structures. A critical point to understand is that the exact output and sophistication of these generated files are entirely dependent on the quality and specificity of the Claude Code templates you have access to for your .NET projects. If a robust vertical slice template isn't readily available, you may need to invest time in creating or adapting one, or even use Claude itself to help generate the template's initial structure.

To experience this firsthand, navigate to your ASP.NET Core monolith's project directory in your terminal and run `claude create <template-name> --name MyNewFeature --project <your-api-project-name>`. Experiment with different template names if available to see how Claude Code can accelerate your feature development workflow.
