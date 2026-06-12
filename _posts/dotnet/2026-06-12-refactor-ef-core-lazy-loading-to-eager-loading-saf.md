---
layout: post
title: "Refactor EF Core Lazy Loading to Eager Loading Safely"
date: 2026-06-12
type: how-to
summary: "Migrate from EF Core lazy loading to explicit eager loading to prevent N+1 issues and improve performance."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Refactor EF Core Lazy Loading to Eager Loading Safely](assets/images/placeholder.jpg)



Entity Framework Core's lazy loading offers an appealing initial simplicity, but it's a double-edged sword. As your .NET application scales, the implicit loading of related data can silently degrade performance by introducing the notorious N+1 query problem. This insidious issue arises when you fetch a collection of primary entities, and then, for each individual entity, EF Core executes a separate, subsequent query to fetch its related data. The result? A cascade of database calls that can quickly overwhelm your database and cripple application responsiveness. Transitioning to explicit data loading, particularly eager loading, is a critical optimization strategy for any mature EF Core application.

While manual refactoring can be tedious, tools like Claude Code can significantly streamline this process. By meticulously analyzing your `DbContext` and entity configurations, Claude Code excels at pinpointing where implicit lazy loading is occurring. It then intelligently suggests explicit eager loading patterns, primarily leveraging the `.Include()` and `.ThenInclude()` methods. This proactive identification and suggestion mechanism not only prevents performance regressions but also ensures your application fetches precisely the data required for a given operation in a single, optimized database roundtrip, avoiding the overhead of multiple, unnecessary queries.

Consider a common scenario: retrieving a list of `Orders`, where each `Order` is associated with a `Customer`. Without eager loading, accessing `order.Customer` for each order in a loop would trigger a separate database query for every single customer, leading to an N+1 problem. Claude Code can identify this pattern and generate the necessary `.Include(o => o.Customer)` call to fetch all related customers in the initial query, drastically reducing database roundtrips.

```csharp
// Before (Lazy Loading - potential N+1)
var orders = await _context.Orders.ToListAsync();
foreach (var order in orders)
{
    // This line can trigger a separate query for each order's customer if not already loaded
    Console.WriteLine($"Order {order.Id} for Customer: {order.Customer.Name}");
}

// After (Eager Loading with Claude Code's assistance)
var ordersWithCustomers = await _context.Orders
    .Include(o => o.Customer) // Claude Code helps identify and suggest this crucial inclusion
    .ToListAsync();

foreach (var order in ordersWithCustomers)
{
    // Customer data is now readily available from the initial query
    Console.WriteLine($"Order {order.Id} for Customer: {order.Customer.Name}");
}
```

A key consideration when adopting eager loading is the risk of over-fetching. While it solves the N+1 problem, enthusiastically including too many related entities can lead to excessively large query results, which also impacts performance. It's paramount to critically evaluate what related data is *truly* necessary for the specific operation at hand. Claude Code can foster this deliberative approach by highlighting the implications of various `.Include()` chains, helping you strike the right balance between comprehensive data retrieval and efficient query design, a nuanced understanding often beyond basic documentation.
