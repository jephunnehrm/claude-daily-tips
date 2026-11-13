---
layout: post
title: "Implement Soft Deletes in EF Core with Global Filters"
date: 2026-11-13
type: how-to
summary: "Automatically apply soft delete logic to all queries in your EF Core application without modifying individual repository methods."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - productivity
  - devtools
---



![Implement Soft Deletes in EF Core with Global Filters](assets/images/placeholder.jpg)



The common practice of hard deleting records from a database can lead to irreversible data loss, posing significant risks for audit trails, business continuity, and potential recovery scenarios. As .NET developers, we often find ourselves needing to preserve historical data. Manually appending `Where(x => !x.IsDeleted)` to every query is not only verbose but also a breeding ground for subtle bugs. EF Core's global query filters offer an elegant solution, enabling us to consistently enforce soft delete logic across our entire application's data layer.

To implement soft deletes effectively, we'll first introduce a common interface, `ISoftDelete`, which entities intended for soft deletion will implement. This interface defines the essential `IsDeleted` boolean property. Within your `DbContext`, overriding `OnModelCreating` is the key to registering this global filter. We'll leverage EF Core's model building capabilities to iterate through all entity types and apply the filter to any that conform to `ISoftDelete`, ensuring that all subsequent queries automatically exclude records where `IsDeleted` is `true`.

Here's the practical implementation. Define the `ISoftDelete` interface:

```csharp
// Define the interface for entities that support soft deletion
public interface ISoftDelete
{
    bool IsDeleted { get; set; }
}
```

And in your `DbContext`, extend `OnModelCreating` to apply the global filter:

```csharp
using Microsoft.EntityFrameworkCore;
using System.Linq;

public class ApplicationDbContext : DbContext
{
    // Define your DbSets here
    public DbSet<Product> Products { get; set; }
    public DbSet<Order> Orders { get; set; }

    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply the global soft delete filter to all entities implementing ISoftDelete
        modelBuilder.ApplyGlobalSoftDeleteFilter();
    }
}

// Extension method to apply the global query filter
public static class SoftDeleteQueryFilterExtensions
{
    public static void ApplyGlobalSoftDeleteFilter(this ModelBuilder modelBuilder)
    {
        // Iterate over all entity types in the model
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            // Check if the entity type implements the ISoftDelete interface
            if (typeof(ISoftDelete).IsAssignableFrom(entityType.ClrType))
            {
                // Apply the global query filter
                entityType.SetGlobalQueryFilter<ISoftDelete>(
                    entity => !entity.IsDeleted); // Condition to exclude deleted entities
            }
        }
    }
}
```

With this setup, when you query a `DbSet` whose entities implement `ISoftDelete`, EF Core automatically appends the `!entity.IsDeleted` condition. To "delete" an entity, you simply set its `IsDeleted` property to `true` and call `SaveChanges()`. This preserves the record while making it invisible to standard queries, facilitating auditing and recovery.

A critical aspect to understand is that `IgnoreQueryFilters()` is your indispensable tool for bypassing this global filter. This is particularly important for administrative functions or recovery processes where you might need to explicitly retrieve "deleted" records. For example, to fetch all soft-deleted products, you would write `_context.Products.IgnoreQueryFilters().Where(p => p.IsDeleted).ToList();`. Failing to acknowledge this will make accessing deleted data an unexpected hurdle.
