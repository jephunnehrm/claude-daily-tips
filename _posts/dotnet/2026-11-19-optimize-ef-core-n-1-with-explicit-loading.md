---
layout: post
title: "Optimize EF Core N+1 with Explicit Loading"
date: 2026-11-19
type: how-to
summary: "Eliminate common N+1 query problems in EF Core by switching from lazy to explicit eager loading."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - devtools
---



![Optimize EF Core N+1 with Explicit Loading](assets/images/placeholder.jpg)



It's a familiar sting for .NET developers: fetching a list of parent entities, only to witness a cascade of SQL queries flooding your logs as you access their related child collections. This "N+1 query problem," often a silent performance killer, is a common consequence of Entity Framework Core's default lazy loading. Fortunately, you can reclaim control and dramatically optimize these scenarios by explicitly instructing EF Core on how to load related data.

The core of the solution lies in leveraging the `Include` and `ThenInclude` extension methods directly on your `IQueryable` within your `DbContext`. Instead of letting navigation properties trigger individual database requests on demand, you're telling EF Core precisely which related entities to fetch *upfront* as part of the initial query. This transforms a series of inefficient, individual queries into a single, optimized SQL statement, drastically minimizing database round trips and their associated latency.

Consider a common scenario: fetching `Blog` entities and their associated `Post` collections. Without explicit loading, accessing `blog.Posts` for each blog would trigger a separate query for each blog. Here's how to address this using `Include`:

```csharp
public async Task<IEnumerable<Blog>> GetBlogsWithPostsEagerlyAsync(MyDbContext context)
{
    // Explicitly instruct EF Core to load all Posts for each Blog in a single query.
    return await context.Blogs
        .Include(b => b.Posts)
        .ToListAsync();
}
```

If your relationships extend further, for instance, if `Post` entities have a collection of `Comment` entities, you can chain `ThenInclude` to construct even more comprehensive queries:

```csharp
public async Task<IEnumerable<Blog>> GetBlogsWithPostsAndCommentsEagerlyAsync(MyDbContext context)
{
    // Eagerly load Posts and then the Comments for each Post.
    return await context.Blogs
        .Include(b => b.Posts)
            .ThenInclude(p => p.Comments)
        .ToListAsync();
}
```

While this eager loading strategy significantly boosts performance by reducing database hits, a crucial "gotcha" to be mindful of is potential memory overhead. Loading excessively large or deeply nested related collections can consume substantial amounts of RAM, potentially negating the performance gains. It's imperative to profile your queries and, when you only need a subset of related data, consider using projections instead. For scenarios where you need to load a specific related entity for *a single* parent item *after* fetching the parent, the `Load` or `LoadAsync` methods from `Microsoft.EntityFrameworkCore.Abstractions` offer a more targeted approach.
