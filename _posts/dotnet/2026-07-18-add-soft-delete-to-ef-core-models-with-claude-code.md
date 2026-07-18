---
layout: post
title: "Add Soft Delete to EF Core Models with Claude Code"
date: 2026-07-18
type: how-to
summary: "Easily implement global soft delete filtering in EF Core, keeping your data intact and history accessible."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-18-add-soft-delete-to-ef-core-models-with-claude-code.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Add Soft Delete to EF Core Models with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-07-18-add-soft-delete-to-ef-core-models-with-claude-code.jpg)



As a .NET developer working with Entity Framework Core, you've undoubtedly faced the dilemma of data retention. Simply deleting records can mean losing valuable audit trails, jeopardizing compliance, or hindering potential data recovery. While manual management of an `IsDeleted` flag and its subsequent filtering in every query is a common workaround, it's prone to oversight and leads to boilerplate code. This article demonstrates how to automate this essential soft-delete pattern using EF Core's Global Query Filters, significantly streamlining your development workflow.

The core of this solution lies in two EF Core features: defining a consistent `IsDeleted` property across your entities and applying a global query filter. For any entity you wish to implement soft-delete for, ensure it includes a `bool IsDeleted` property. Then, within your `DbContext`, override the `OnModelCreating` method. This is the central location where you'll configure EF Core to apply the `IsDeleted` filter automatically to all queries involving these entities.

Here’s the C# code to achieve this, utilizing a simple extension method for clarity and reusability:

```csharp
using Microsoft.EntityFrameworkCore;
using System.Linq;
using System.Linq.Expressions; // Added for Expression types

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Apply the soft delete filter to all entities with an IsDeleted property
        modelBuilder.ApplyGlobalSoftDeleteFilter();

        base.OnModelCreating(modelBuilder);
    }
}

// Extension method to apply the soft delete filter globally
public static class SoftDeleteQueryFilter
{
    public static void ApplyGlobalSoftDeleteFilter(this ModelBuilder modelBuilder)
    {
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            // Check if the entity type has an 'IsDeleted' property.
            // Note: This check is case-sensitive for property names.
            var isDeletedProperty = entityType.FindProperty("IsDeleted");
            if (isDeletedProperty != null && isDeletedProperty.ClrType == typeof(bool))
            {
                // Create a parameter expression for the entity type.
                var parameter = Expression.Parameter(entityType.ClrType, "entity");

                // Create an expression to access the 'IsDeleted' property.
                var property = Expression.Property(parameter, isDeletedProperty.Name);

                // Create an expression to compare 'IsDeleted' to false.
                var compareExpression = Expression.Constant(false, typeof(bool));
                var filterExpression = Expression.Equal(property, compareExpression);

                // Create a lambda expression to represent the query filter.
                var lambdaExpression = Expression.Lambda(filterExpression, parameter);

                // Apply the query filter to the entity type.
                entityType.SetQueryFilter(lambdaExpression);
            }
        }
    }
}
```

This global filter ensures that any query attempting to retrieve entities with an `IsDeleted` property will automatically exclude those marked as deleted (`IsDeleted == true`). The `SetQueryFilter` method intrinsically adds a `WHERE` clause to generated SQL, meaning your application code remains clean and unaware of the soft-delete logic. A crucial consideration, or "gotcha," is that this global filter applies universally. If you need to retrieve deleted entities for specific purposes like a "trash" view or a data restoration feature, you must explicitly override the filter for that particular `DbSet` operation using `.IgnoreQueryFilters()`. For instance: `_context.MyEntities.IgnoreQueryFilters().Where(e => e.Id == someId).FirstOrDefaultAsync()`. This approach empowers you to maintain data integrity and auditability without sacrificing code elegance.
