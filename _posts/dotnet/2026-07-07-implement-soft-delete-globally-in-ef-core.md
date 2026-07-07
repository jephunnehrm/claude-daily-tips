---
layout: post
title: "Implement Soft Delete Globally in EF Core"
date: 2026-07-07
type: how-to
summary: "Add a global query filter in EF Core to easily implement soft delete for your entities."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-07-implement-soft-delete-globally-in-ef-core.jpg"
tags:
  - dotnet
  - csharp
  - productivity
  - devtools
---



![Implement Soft Delete Globally in EF Core](/claude-daily-tips/assets/images/dotnet-2026-07-07-implement-soft-delete-globally-in-ef-core.jpg)



Soft deleting entities is a common pattern in .NET applications, aiming to logically remove data without permanently deleting it from the database. Developers often fall into the trap of manually adding `Where(e => !e.IsDeleted)` to nearly every query. This repetitive, error-prone practice clutters your codebase and increases the risk of overlooking a filter, leading to accidental exposure of logically deleted data. Fortunately, Entity Framework Core (EF Core) provides a powerful mechanism to address this: global query filters. These filters enable you to automatically apply conditions, like our soft delete check, to all queries for specific entity types, ensuring consistency and maintainability.

The strategy involves defining a common base class for your entities that includes an `IsDeleted` boolean property, defaulting to `false`. Then, within your `DbContext`'s `OnModelCreating` method, you can configure EF Core to apply a global filter to entities that inherit from this base. This filter will ensure that any entity where `IsDeleted` is `true` is automatically excluded from standard queries. To perform a soft delete, you simply mark the entity as deleted by setting `IsDeleted` to `true` and saving the changes; the record remains in the database but is effectively invisible to regular application logic.

Here’s a practical example using an `AuditableEntity` base class and applying a global filter in `OnModelCreating`:

```csharp
using Microsoft.EntityFrameworkCore;
using System.Linq.Expressions; // Required for Expression.Parameter, Expression.Property, etc.
using System;

public abstract class AuditableEntity // Make it abstract if it's meant to be inherited from
{
    public int Id { get; set; }
    public bool IsDeleted { get; set; } = false;
    // Consider adding CreatedAt, UpdatedAt, etc. here for comprehensive auditing.
}

public class Product : AuditableEntity
{
    public string Name { get; set; }
    public decimal Price { get; set; }
}

public class MyDbContext : DbContext
{
    public DbSet<Product> Products { get; set; }

    public MyDbContext(DbContextOptions<MyDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply the global filter to all entities inheriting from AuditableEntity.
        // This approach scales better than applying to each entity individually.
        var entityMethod = typeof(ModelBuilder).GetMethod(nameof(ModelBuilder.Entity))!;
        var queryFilterMethod = typeof(ModelBuilder).GetMethod(nameof(ModelBuilder.QueryFilter))!; // Access QueryFilter method

        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(AuditableEntity).IsAssignableFrom(entityType.ClrType) && !entityType.IsOwned()) // Exclude owned types if necessary
            {
                // Dynamically construct the lambda expression: entity => !entity.IsDeleted
                var parameter = Expression.Parameter(entityType.ClrType, "entity");
                var property = Expression.Property(parameter, nameof(AuditableEntity.IsDeleted));
                var notOperator = Expression.Not(property);
                var lambda = Expression.Lambda(notOperator, parameter);

                // Apply the filter using the generic Entity method and SetQueryFilter
                var genericEntityMethod = entityMethod.MakeGenericMethod(entityType.ClrType);
                var entityBuilder = genericEntityMethod.Invoke(modelBuilder, null);
                var setQueryFilterMethod = entityBuilder.GetType().GetMethod(nameof(ModelBuilder.QueryFilter))!; // Get QueryFilter method from the entity builder
                setQueryFilterMethod.Invoke(entityBuilder, new object[] { lambda });
            }
        }
    }
}
```

A critical aspect of this pattern is managing exceptions to the global filter. For administrative tasks or recovery scenarios, you might need to retrieve logically deleted records. EF Core handles this gracefully with the `IgnoreQueryFilters()` method, allowing you to temporarily bypass the global filter for specific queries. For example, `_dbContext.Products.IgnoreQueryFilters().FirstOrDefaultAsync(p => p.Id == someId)` will fetch even a deleted product. Be mindful that when performing joins between entities that both utilize soft delete, the filter will be applied to both sides. This can lead to unexpected results if not carefully managed, potentially excluding entire sets of related data if the "parent" is deleted. Always consider the impact of the global filter on your query logic, especially in complex scenarios involving joins or eager loading.
