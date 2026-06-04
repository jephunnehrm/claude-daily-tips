---
layout: post
title: "Prevent Data Loss with EF Core Rowversion and Claude Code"
date: 2026-06-04
type: how-to
summary: "Learn how to implement optimistic concurrency in EF Core using `rowversion` and Claude Code for robust data integrity."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - productivity
---



![Prevent Data Loss with EF Core Rowversion and Claude Code](assets/images/placeholder.jpg)



As a .NET developer building data-driven applications, you've undoubtedly grappled with the dreaded "last save wins" scenario. This race condition, where two users simultaneously attempt to modify the same record, can silently corrupt your data. Entity Framework Core (EF Core) offers a robust solution through optimistic concurrency, and leveraging tools like Claude Code can streamline its implementation.

EF Core's primary mechanism for optimistic concurrency is the `rowversion` data type (known as `timestamp` in SQL Server). By adding a `rowversion` property to your entity, EF Core automatically tracks changes to a row. When an update is attempted, EF Core compares the `rowversion` of the record in the database with the one originally loaded. If they don't match, it signifies that the row has been modified by another process, and EF Core throws a `DbUpdateConcurrencyException`, effectively preventing an unintended overwrite.

Claude Code can significantly accelerate the setup of this crucial feature. For instance, prompting it with "Implement optimistic concurrency control with a `rowversion` property on an EF Core entity named `Product`" will generate code like this:

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; }
}
```
This `[Timestamp]` attribute seamlessly maps to the database's `rowversion` or `timestamp` type.

When performing save operations, it's imperative to gracefully handle the `DbUpdateConcurrencyException`. A common and recommended pattern involves catching this exception, clearly notifying the user of the conflict, and providing options such as re-fetching the latest data and reapplying their changes or discarding their local modifications. A critical consideration for user-facing applications is to *always* present this choice; simply retrying the save without user awareness can lead to unexpected data loss or outdated information being presented. For background services, a more automated retry strategy might be feasible, but this necessitates careful design for idempotency.

To witness this in action, add the `[Timestamp]` attribute and the `byte[] RowVersion` property to an existing EF Core entity. Then, simulate a concurrent update by having two processes attempt to modify the same record, and observe the `DbUpdateConcurrencyException` being thrown.
