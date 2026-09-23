---
layout: post
title: "Eliminate Repetitive DTO Mapping Code"
date: 2026-09-23
type: how-to
summary: "Reduce boilerplate DTO mapping code by having Claude Code generate a Roslyn source generator."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-23-eliminate-repetitive-dto-mapping-code.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Eliminate Repetitive DTO Mapping Code](/claude-daily-tips/assets/images/dotnet-2026-09-23-eliminate-repetitive-dto-mapping-code.jpg)



As a .NET developer, you've undoubtedly wrestled with the repetitive chore of mapping data between your domain models and Data Transfer Objects (DTOs). This manual mapping is a significant source of boilerplate code, increasing development time and the potential for subtle errors. While established libraries like AutoMapper excel at this, there are scenarios where a more integrated, compile-time enforced solution is desirable. This is precisely where Roslyn source generators, amplified by tools like Claude Code, offer a powerful automation path.

Source generators operate by injecting custom code directly into the compilation pipeline. This means your project's effective codebase can be augmented *before* runtime, without you manually writing the additional code. Imagine defining your source and target DTOs, and then leveraging Claude Code to *generate* the Roslyn source generator responsible for automatically producing the mapping logic. The core value proposition here is not the generation of the DTOs themselves, but rather the intricate mapping code *between* them. This leads to a more maintainable codebase, drastically reduces the likelihood of mapping oversights, and liberates developers from monotonous boilerplate.

To embark on this, you can instruct Claude Code to bootstrap a C# project designed as a Roslyn analyzer and code generator. A prompt like: "Create a Roslyn source generator that identifies classes adorned with a specific attribute, for instance `[MapWith(typeof(TargetDto))]`, and then programmatically fabricates mapping methods between the source and target classes. The generation should be driven by identical property names and compatible types." Claude Code can then lay the groundwork, including the necessary `IncrementalGenerator` infrastructure and the logic for analyzing syntax nodes.

Consider a conceptual illustration: you'd define your DTOs and a custom attribute like `[MapWith]`. Claude Code would then generate the `IMetadataReferenceProvider` and `ISourceGenerator` implementations. A critical limitation to anticipate is that complex mapping requirements—such as conditional assignments, value transformations beyond simple type casts, or mapping between properties with deeply nested object graphs—will necessitate more granular prompting or post-generation manual refinement.

```csharp
// Example Source DTO
public class Order
{
    public Guid OrderId { get; init; }
    public DateTime OrderDate { get; init; }
    public int CustomerId { get; init; }
    public List<OrderItem> Items { get; init; } = new();
}

// Example Target DTO
public class OrderDto
{
    public Guid Id { get; set; }
    public DateTime Date { get; set; }
    public int CustId { get; set; }
    public List<OrderItemDto> LineItems { get; set; } = new();
}

// You'd prompt Claude Code to create a generator understanding
// how to map Order to OrderDto, e.g.:
// "Generate a Roslyn source generator for mapping between Order and OrderDto,
// using the [MapWith] attribute. It should create static extension methods
// 'ToOrderDto(this Order order)' and 'ToOrder(this OrderDto dto)',
// handling property name differences like OrderId -> Id and CustomerId -> CustId,
// and recursively mapping nested objects like OrderItem to OrderItemDto."
```

Give it a try: Ask Claude Code to "Create a Roslyn source generator that generates extension methods for mapping between two C# classes with different property names, using a custom attribute to define the mapping."
