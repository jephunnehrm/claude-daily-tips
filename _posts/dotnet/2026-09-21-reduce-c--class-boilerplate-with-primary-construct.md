---
layout: post
title: "Reduce C# Class Boilerplate with Primary Constructors"
date: 2026-09-21
type: how-to
summary: "Leverage Claude Code to quickly adopt C# 12 primary constructors and collection expressions, simplifying class definitions."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-21-reduce-c--class-boilerplate-with-primary-construct.jpg"
tags:
  - csharp
  - claude-code
  - productivity
  - dotnet
---



![Reduce C# Class Boilerplate with Primary Constructors](/claude-daily-tips/assets/images/dotnet-2026-09-21-reduce-c--class-boilerplate-with-primary-construct.jpg)



As a .NET developer, you've undoubtedly spent time writing classes that are primarily data containers. These often involve a repetitive pattern: a constructor that assigns values to public, get-only properties, and potentially a `List<T>` property that also needs initialization. This boilerplate, while functional, adds visual noise and increases maintenance overhead. C# 12's introduction of primary constructors, especially when combined with collection expressions, offers a significant opportunity to streamline these types. However, manually refactoring existing codebases can be time-consuming and prone to overlooking subtle nuances.

Consider a typical `Product` class designed to hold simple data:

```csharp
using System.Collections.Generic;

public class Product
{
    public int Id { get; }
    public string Name { get; }
    public decimal Price { get; }
    public List<string> Tags { get; }

    public Product(int id, string name, decimal price, List<string> tags)
    {
        Id = id;
        Name = name;
        Price = price;
        Tags = tags ?? new List<string>(); // Null-coalescing for safety
    }
}
```

This class serves its purpose but requires explicit property declarations and a constructor body for assignment. With the advent of primary constructors, this can be dramatically simplified. For instance, the `Product` class can be rewritten as:

```csharp
using System.Collections.Generic;

public class Product(int Id, string Name, decimal Price, List<string> Tags)
{
    public List<string> Tags { get; } = Tags ?? new List<string>();
}
```

This transformation leverages the primary constructor to implicitly declare and initialize the `Id`, `Name`, and `Price` properties. The `Tags` property requires explicit declaration and initialization within the primary constructor body to include the null-coalescing logic, demonstrating a common pattern where primary constructors still need some explicit handling for complex initialization or when interacting with base classes. This concise syntax reduces code volume and enhances readability, directly addressing the tedium of repetitive data-holding class definitions.

A key consideration when adopting primary constructors involves their interaction with inherited constructors and explicit member initialization. While simple POCOs are straightforward, scenarios involving base class constructors, or when a parameter needs to be used for more than just property assignment (e.g., calling a base constructor), require careful attention. The compiler infers property assignments from primary constructor parameters, but when custom logic or base class calls are involved, you'll explicitly use the parameter within the primary constructor's body. Understanding this dynamic is crucial to avoid unexpected behavior.

To experience this reduction in boilerplate firsthand, you can use the `claude` CLI to refactor a simple POCO. Point it to a file like `Models/Customer.cs` and instruct it to transform the class to use C# 12 primary constructors and collection expressions. This hands-on approach allows you to see the immediate impact and explore the resulting code, making the transition to more modern C# constructs smoother and more efficient.
