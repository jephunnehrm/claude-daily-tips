---
layout: post
title: "Imperative Loops to LINQ with Claude Code"
date: 2026-10-09
type: how-to
summary: "Convert nested loops to efficient LINQ expressions using Claude Code for cleaner C# code."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Imperative Loops to LINQ with Claude Code](assets/images/placeholder.jpg)



The maintainability nightmare of deeply nested imperative loops is a familiar foe for many .NET developers. When faced with complex data transformations and filtering, these constructs quickly degrade into unreadable, undebuggable, and unrefactorable code. While the allure of declarative programming with LINQ is strong, manually translating intricate imperative logic into elegant LINQ queries can be a painstaking and error-prone endeavor. This is precisely where AI-powered coding assistants like Claude Code can offer a transformative solution, significantly enhancing developer productivity.

Claude Code's `claude` CLI is adept at analyzing existing imperative code and proposing functional, LINQ-based equivalents. Consider the common task of extracting distinct product names from orders within a specific time frame. An imperative solution often involves multiple nested `foreach` loops, `if` statements, and auxiliary collections to manage uniqueness. Claude Code can streamline this by generating a concise LINQ expression.

Let's illustrate with a concrete example: processing a `List<Order>`, where each `Order` contains a `List<OrderItem>`, and each `OrderItem` has a `ProductName`. To retrieve all distinct product names from orders placed in the last 30 days:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class OrderItem
{
    public string ProductName { get; set; }
}

public class Order
{
    public DateTime OrderDate { get; set; }
    public List<OrderItem> OrderItems { get; set; }
}

public class Example
{
    public static void ProcessOrders(List<Order> orders)
    {
        var distinctProductNames = new HashSet<string>();

        // Imperative approach
        var recentOrders = orders.Where(o => o.OrderDate >= DateTime.Today.AddDays(-30));

        foreach (var order in recentOrders)
        {
            foreach (var item in order.OrderItems)
            {
                distinctProductNames.Add(item.ProductName);
            }
        }
        // distinctProductNames now holds the desired result.
    }
}
```

When you leverage `claude` for refactoring, targeting patterns like "nested loops to LINQ," it intelligently suggests a LINQ-based transformation. The AI understands that `SelectMany` is crucial for flattening the nested collections of `OrderItem`s, followed by `Select` to extract `ProductName`s, `Distinct` for uniqueness, and finally `ToList()` (or `ToHashSet()`) to materialize the result. The resulting LINQ expression would look something like this:

```csharp
var distinctProductNamesLinq = orders
    .Where(o => o.OrderDate >= DateTime.Today.AddDays(-30))
    .SelectMany(o => o.OrderItems)
    .Select(oi => oi.ProductName)
    .Distinct()
    .ToList(); // Or ToHashSet() depending on preference
```

A critical aspect to remember when using Claude Code for such transformations is that while it excels at syntactic conversion, the generated LINQ might not always be the most performant. For highly optimized or exceptionally large datasets, an AI-generated query could potentially create unnecessary intermediate collections or miss subtle performance tuning opportunities. Therefore, a senior developer must always review the generated LINQ for both clarity and efficiency. It's crucial to understand *why* `SelectMany` is used here to flatten the hierarchy and *why* `Distinct()` is placed after the selection of product names to ensure correctness and efficiency. Manual adjustments might be necessary to chain operations optimally or to judiciously employ `ToList()` to avoid excessive memory allocation.

To experience this firsthand, place the provided imperative C# code into a `.cs` file and execute `claude --refactor --target-language csharp --target-pattern "nested loops to linq"`. Analyze the suggested LINQ expression and compare its conciseness and readability to the original imperative code.
