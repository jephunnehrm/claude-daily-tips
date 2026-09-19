---
layout: post
title: "Simplify C# Classes with Primary Constructors"
date: 2026-09-19
type: how-to
summary: "Leverage Claude Code to automatically refactor classes to use C# 12 primary constructors and collection expressions for cleaner code."
image: "assets/images/placeholder.jpg"
tags:
  - csharp
  - claude-code
  - productivity
  - devtools
  - dotnet
---



![Simplify C# Classes with Primary Constructors](assets/images/placeholder.jpg)



Many .NET developers grapple with the verbose nature of traditional constructors, especially for simple data-holding classes and immutable records. The common pattern of declaring properties and then meticulously assigning them within a constructor body, often coupled with explicit property initializers, can lead to significant code bloat. This verbosity becomes even more apparent when initializing collections, where the boilerplate can obscure the actual intent of the code. Fortunately, C# 12's introduction of primary constructors directly on classes and structs, alongside collection expressions, offers a more streamlined and expressive syntax for these common scenarios. Manually refactoring existing codebases to adopt these modern constructs can be a time-consuming and error-prone task.

This is where tools like Claude Code can dramatically accelerate the adoption of C# 12's syntactic sugar. By intelligently analyzing your existing C# classes, Claude Code can pinpoint opportunities to transform conventional constructors into concise primary constructors. It can also identify opportunities to replace verbose collection initialization with the elegant shorthand provided by collection expressions. This transformation not only enhances code readability by reducing boilerplate but also significantly lowers the cognitive load when defining simple types, allowing you to focus on the core logic of your application. Imagine taking a typical `Record` or `class` definition and seeing it instantly condensed into its modern, C# 12 equivalent.

Consider a common scenario: a class designed to hold application settings. Traditionally, this might involve multiple lines for property declarations and their assignments within a constructor. Claude Code can automatically refactor this into a more compact primary constructor pattern. For instance, initializing a list of allowed hosts can be further simplified using collection expressions when the list is created.

```csharp
// Original class with traditional constructor
public class AppSettings
{
    public string ApiKey { get; }
    public List<string> AllowedHosts { get; }

    public AppSettings(string apiKey, List<string> allowedHosts)
    {
        ApiKey = apiKey;
        AllowedHosts = allowedHosts;
    }
}

// Refactored using C# 12 primary constructor
public class AppSettings(string apiKey, List<string> allowedHosts)
{
    public string ApiKey { get; } = apiKey;
    public List<string> AllowedHosts { get; } = allowedHosts;
}

// Further simplified with collection expression for initialization
public class AppSettings(string apiKey, params string[] allowedHosts)
{
    public string ApiKey { get; } = apiKey;
    public List<string> AllowedHosts { get; } = new List<string>(allowedHosts);
}
```

While Claude Code excels at these straightforward refactorings, it's crucial to be aware of potential complexities. If your existing constructors contain intricate logic beyond simple property assignments, such as conditional assignments or side effects, a manual review will be necessary as primary constructors are designed for simpler initialization. Similarly, when dealing with complex inheritance hierarchies where constructor chaining is involved, careful consideration and potential manual adjustments are required to ensure compatibility with primary constructors. Additionally, to leverage C# 12 features, ensure your project's target framework is set to .NET 8 or later.

**Try it:** Use `claude refactor --feature primary-constructors` within your project to discover how many of your classes can be simplified.
