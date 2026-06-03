---
layout: post
title: "Simplify C# Classes with Claude Code"
date: 2026-06-03
type: how-to
summary: "Reduce boilerplate code in C# 12 using primary constructors and collection expressions with Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Simplify C# Classes with Claude Code](assets/images/placeholder.jpg)



As a .NET developer, you've likely encountered the tedium of writing boilerplate code for simple C# classes, particularly when defining constructors and initializing properties for data transfer objects (DTOs) or configuration settings. These classes often serve as mere data holders, yet their traditional declaration can feel verbose. Wouldn't it be beneficial to leverage modern C# features like primary constructors and collection expressions to drastically reduce this syntactic overhead, allowing you to focus on your application's core logic? Claude Code can be a powerful ally in this endeavor.

C# 12 introduced primary constructors, enabling you to declare constructor parameters directly on the class or struct declaration, elegantly merging parameter definition with class structure. This significantly streamlines the common pattern of assigning constructor arguments to properties. Complementing this, collection expressions offer a more concise syntax for initializing collections. Claude Code excels at identifying opportunities to refactor your existing C# code to embrace these advancements. It can seamlessly transform a conventional class with explicit constructor and property assignments into a primary constructor class and modernize collection initializations with the new syntax.

Consider a typical scenario involving a class designed to hold application settings. Manually refactoring this to utilize a primary constructor and collection expressions can involve multiple steps. Claude Code automates this transformation. For instance, a standard `AppSettings` class:

```csharp
using System.Collections.Generic;

public class AppSettings
{
    public string ApiKey { get; }
    public List<string> FeatureFlags { get; }

    public AppSettings(string apiKey, List<string> featureFlags)
    {
        ApiKey = apiKey;
        FeatureFlags = featureFlags;
    }
}
```

Can be elegantly refactored by Claude Code into a more compact primary constructor form:

```csharp
public class AppSettings(string ApiKey, List<string> FeatureFlags);
```

Similarly, when initializing a list within a method:

```csharp
var flags = new List<string> { "FeatureA", "FeatureB" };
```

Claude Code can suggest modernization, perhaps to a more performant array if immutability is acceptable:

```csharp
string[] flags = ["FeatureA", "FeatureB"];
```

A crucial point for senior developers is understanding the limitations. While primary constructors are excellent for simple data holders, they are not a silver bullet. If your constructor needs to perform complex validation logic, conditional initialization, or interact with dependencies, a traditional constructor remains more readable and maintainable. Furthermore, ensure your target framework version supports these features; for full class primary constructor support and robust collection expression functionality, .NET 8 is recommended.

**Try it:** Use `claude refactor --fix-primary-constructors path/to/your/project` to identify and refactor classes suitable for primary constructors within your .NET project.
