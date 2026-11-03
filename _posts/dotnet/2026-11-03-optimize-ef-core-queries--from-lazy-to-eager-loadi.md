---
layout: post
title: "Optimize EF Core Queries: From Lazy to Eager Loading"
date: 2026-11-03
type: how-to
summary: "Transition EF Core queries from potentially slow lazy loading to efficient eager loading using Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-11-03-optimize-ef-core-queries--from-lazy-to-eager-loadi.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Optimize EF Core Queries: From Lazy to Eager Loading](/claude-daily-tips/assets/images/dotnet-2026-11-03-optimize-ef-core-queries--from-lazy-to-eager-loadi.jpg)



When building .NET applications with Entity Framework Core (EF Core), a common performance pitfall for senior developers is the unintended consequence of lazy loading. This often manifests as the dreaded "N+1" query problem: a single query for a collection of entities, followed by an additional query for each related entity accessed, leading to excessive database round trips and significant performance degradation in production. While lazy loading can simplify initial development, it's crucial to proactively manage data retrieval for efficiency. This article explores how to transition from lazy to explicit eager loading, significantly improving your application's responsiveness.

The root cause lies in EF Core's default behavior for navigation properties. When configured for lazy loading, related data is fetched from the database only upon the first access of that navigation property. To overcome this, EF Core provides powerful eager loading mechanisms, primarily through the `Include()` and `ThenInclude()` extension methods. These methods allow you to specify related entities that should be fetched in the *same* initial database query, dramatically reducing the number of network round trips. Consider a typical scenario where you retrieve `Order` entities:

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;

// Assuming Order and OrderItem are defined EF Core entities
// and _context is an instance of your DbContext

public class OrderRepository
{
    private readonly YourDbContext _context;

    public OrderRepository(YourDbContext context)
    {
        _context = context;
    }

    public async Task<List<Order>> GetOrdersWithItemsAsync()
    {
        // Without Include, accessing order.OrderItems here would trigger N+1 queries
        return await _context.Orders.ToListAsync();
    }
}
```

To resolve the N+1 issue here, we would refactor the `GetOrdersWithItemsAsync` method to explicitly include `OrderItems`:

```csharp
public async Task<List<Order>> GetOrdersWithItemsEagerlyAsync()
{
    return await _context.Orders
                         .Include(o => o.OrderItems) // Eagerly load OrderItems for each Order
                         .ToListAsync();
}
```

This explicit inclusion ensures that all `OrderItems` associated with the retrieved `Orders` are fetched in a single database query. The "why" is simple: by telling EF Core exactly what related data you need upfront, you eliminate the need for EF Core to dynamically generate and execute separate queries for each related entity as it's accessed. This predictable data retrieval pattern is fundamental to building performant data access layers.

However, eager loading isn't without its own considerations. A common "gotcha" is the risk of over-fetching data. Including too many related collections or deeply nested relationships can result in a massive, inefficient SQL query that strains network bandwidth and consumes excessive memory on the client. It's vital to exercise judiciousness with `Include()` and `ThenInclude()`, only fetching the data that is strictly necessary for the current operation. For instance, if you only need to display the order count and not the individual items, then an `Include` would be unwarranted. Thinking critically about the data contract for each query is key.

By understanding these patterns and judiciously applying `Include()` and `ThenInclude()`, senior .NET developers can move beyond the performance pitfalls of lazy loading. This proactive approach leads to more robust, scalable, and responsive applications, ensuring a better user experience and more efficient use of database resources.
