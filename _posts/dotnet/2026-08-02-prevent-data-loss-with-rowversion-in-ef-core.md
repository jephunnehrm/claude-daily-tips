---
layout: post
title: "Prevent Data Loss with Rowversion in EF Core"
date: 2026-08-02
type: how-to
summary: "Ensure data integrity and prevent lost updates in ASP.NET Core applications using EF Core's rowversion."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-02-prevent-data-loss-with-rowversion-in-ef-core.jpg"
tags:
  - dotnet
  - csharp
  - productivity
---



![Prevent Data Loss with Rowversion in EF Core](/claude-daily-tips/assets/images/dotnet-2026-08-02-prevent-data-loss-with-rowversion-in-ef-core.jpg)



Ever faced the frustrating scenario where two users simultaneously edit the same customer record, and the last save unintentionally overwrites crucial changes made by the other? This common race condition, known as optimistic concurrency, can lead to significant data loss and erode user trust. Entity Framework Core (EF Core) offers a powerful solution to combat this using the `rowversion` data type (or `timestamp` in some databases) as a concurrency token. By automatically tracking changes to a row, `rowversion` allows EF Core to detect when a record has been modified since it was last fetched, enabling graceful conflict resolution.

Implementing this in your EF Core entities is remarkably straightforward. Simply add a `byte[]` property to your entity and decorate it with the `[Timestamp]` attribute. EF Core then orchestrates the magic: on each database update, it automatically assigns a new, unique binary value to this property. When you later attempt to save changes to an entity that has had its `RowVersion` updated in the database by another process, EF Core's internal comparison will fail, triggering a `DbUpdateConcurrencyException`. This exception signals that the data you're trying to modify has changed on the server, preventing an accidental overwrite.

Consider this `Product` entity as a prime example:

```csharp
using System;
using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore;

public class Product
{
    public int ProductId { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; }
}
```

Upon encountering a `DbUpdateConcurrencyException`, your application gains valuable control. The most common and robust strategy is to reload the affected entity from the database to get its latest state. You can then intelligently merge the user's intended changes into this reloaded entity, or at least present the conflict to the user, allowing them to reapply their edits. For less critical scenarios, you might even explore automatic merging of non-conflicting changes.

A critical caveat to be aware of is that `rowversion` is a SQL Server-specific data type. While EF Core's `[Timestamp]` attribute abstracts this for SQL Server, if you're working with other database providers like PostgreSQL, you'll likely need to use an equivalent mechanism such as `xmin` or consult your specific provider's documentation for implementing concurrency tokens. Ensure your `DbContext` is correctly configured with the appropriate database provider for this feature to work seamlessly.
