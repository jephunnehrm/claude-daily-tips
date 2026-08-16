---
layout: post
title: "Prevent Data Races in EF Core with Row Versioning"
date: 2026-08-16
type: how-to
summary: "Safeguard against concurrent data modifications in your ASP.NET Core application by implementing optimistic concurrency with EF Core's `rowversion`."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-16-prevent-data-races-in-ef-core-with-row-versioning.jpg"
tags:
  - dotnet
  - csharp
  - productivity
---



![Prevent Data Races in EF Core with Row Versioning](/claude-daily-tips/assets/images/dotnet-2026-08-16-prevent-data-races-in-ef-core-with-row-versioning.jpg)



Ever grappled with simultaneous edits in your ASP.NET Core application, where one user's save tragically overwrites another's? This common data race scenario, a classic concurrency problem, can lead to frustrating data loss. While pessimistic locking offers strict control, it often introduces significant overhead. A more agile and efficient solution for many applications lies in optimistic concurrency, powered by a mechanism like database row versioning. Entity Framework Core seamlessly integrates this approach, making it surprisingly straightforward to implement.

The core of optimistic concurrency with row versioning in EF Core involves a special database column, often managed by a `byte[]` property in your C# entity. Marked with the `[Timestamp]` attribute, this property signals to EF Core that it's responsible for concurrency checks. Upon saving, EF Core transparently compares the `RowVersion` of the entity in memory with the `RowVersion` stored in the database. If these values diverge—indicating that another process has modified the data since it was loaded—an `DbUpdateConcurrencyException` is thrown. This exception acts as a safeguard, preventing the last-write-wins scenario and preserving data integrity.

Here’s how you’d integrate this into your EF Core model and `DbContext`:

```csharp
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }

    // This byte array property will be automatically managed by EF Core
    // for concurrency checks, incrementing with each database update.
    [Timestamp]
    public byte[] RowVersion { get; set; }
}

public class MyDbContext : DbContext
{
    public DbSet<Product> Products { get; set; }

    public MyDbContext(DbContextOptions<MyDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Product>()
            // Explicitly marking this property as a row version
            // ensures EF Core uses it for concurrency control.
            .Property(p => p.RowVersion)
            .IsRowVersion();
    }
}
```

The primary limitation of this optimistic approach is its reliance on the application to resolve conflicts. If your application experiences extremely high contention or requires absolute, immediate consistency for every operation, a more robust strategy like pessimistic locking might be necessary. It's also important to note that while `.IsRowVersion()` in `OnModelCreating` is best practice for clarity and explicit configuration, the `[Timestamp]` attribute on the `byte[]` property is the fundamental trigger for EF Core's automatic management of this concurrency token.

When an `DbUpdateConcurrencyException` occurs, your application logic should gracefully handle it. The typical pattern involves informing the user about the conflict and presenting them with a choice: either reload the most recent data and reapply their modifications, or discard their changes and accept the database's current state. This user-centric resolution strategy is the hallmark of an effective optimistic concurrency implementation, empowering users to manage potential data conflicts directly.
