---
layout: post
title: "Prevent Stale Data Conflicts with EF Core Rowversion"
date: 2026-09-01
type: how-to
summary: "Implement optimistic concurrency in EF Core using rowversion to automatically detect and handle data modification conflicts."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-01-prevent-stale-data-conflicts-with-ef-core-rowversi.jpg"
tags:
  - dotnet
  - csharp
  - devtools
---



![Prevent Stale Data Conflicts with EF Core Rowversion](/claude-daily-tips/assets/images/dotnet-2026-09-01-prevent-stale-data-conflicts-with-ef-core-rowversi.jpg)



Ever faced the frustrating scenario where two users edit the same record concurrently, and one user's hard-earned changes are silently discarded? This is a classic race condition, often leading to data corruption. Entity Framework Core (EF Core) offers a powerful defense against this with optimistic concurrency, and the `rowversion` data type (known as `timestamp` in SQL Server) is its primary weapon. By incorporating a `rowversion` column into your entity, EF Core can diligently track row modifications. When you attempt to save an entity that's been altered since you last read it, EF Core will detect the discrepancy and prevent the overwrite.

The implementation is straightforward. Add a `byte[]` property to your EF Core entity and decorate it with the `[Timestamp]` attribute. EF Core automatically maps this to the database's native concurrency token type. When a `DbUpdateConcurrencyException` is thrown during a save operation, it signifies that the data you intended to update has been modified by another process. This exception is your signal that a conflict has occurred, and you can no longer proceed with the save as is.

```csharp
using System.ComponentModel.DataAnnotations;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; }
}
```

Upon catching a `DbUpdateConcurrencyException`, you have several strategic options for resolution. You might choose to re-fetch the original entity, attempt to merge the user's changes with the latest data (potentially requiring user intervention to resolve specific conflicts), or even inform the user that their changes cannot be applied due to concurrent modifications. A common and robust pattern involves reloading the current state from the database, merging the user's intended updates, and then re-attempting the save. This approach ensures data integrity and provides a fair opportunity for the user to reconcile any conflicts.

While EF Core abstracts away much of the database-specific implementation, it's crucial to remember that `rowversion` is fundamentally tied to SQL Server's `timestamp` data type. This means that if you're using a different database provider, the underlying mechanism for generating and comparing concurrency tokens might vary, and you may need to adjust your EF Core configuration or use alternative concurrency token strategies. Additionally, for high-contention scenarios where numerous users might edit the same entity simultaneously, a simple retry or manual merge might become insufficient, necessitating more sophisticated conflict resolution logic.
