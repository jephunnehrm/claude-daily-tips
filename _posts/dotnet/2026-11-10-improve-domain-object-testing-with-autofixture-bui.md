---
layout: post
title: "Improve Domain Object Testing with AutoFixture Builders"
date: 2026-11-10
type: how-to
summary: "Leverage Claude Code to quickly create custom AutoFixture builders for complex domain aggregate objects, enhancing test data generation."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Improve Domain Object Testing with AutoFixture Builders](assets/images/placeholder.jpg)



Manually creating diverse and realistic test data for complex domain aggregate objects in ASP.NET Core applications is a time-consuming bottleneck. Repeatedly instantiating aggregates, along with their intricate networks of related entities and value objects, leads to verbose test code that is fragile and difficult to maintain. While AutoFixture excels at generating test data, effectively guiding its generation for domain aggregates with strict business rules or complex relationships often necessitates custom `ISpecimenBuilder` implementations.

Claude Code acts as a powerful accelerator for developing these custom AutoFixture builders. Instead of wrestling with the boilerplate of builder implementation, you can describe your domain aggregate and its specific customization requirements to Claude Code, which can then generate a well-structured `ISpecimenBuilder`. This empowers you to concentrate on the critical business logic and constraints that truly matter for your test data, rather than the intricacies of the builder's construction. For instance, consider an `Order` aggregate containing a list of `OrderItem` entities, each linked to a `Product` with a `Price`. You might need to ensure the order's total price is accurate or that specific product types receive predefined discounts.

To illustrate, imagine an `Order` aggregate with a `CustomerId` property and a `List<OrderItem>`, where each `OrderItem` includes a `ProductId` and an `Quantity`. To generate valid `Order` objects with AutoFixture, you might want to control the `CustomerId` or enforce that `Quantity` is always positive. You can prompt Claude Code with a clear request like: "Generate an AutoFixture `ISpecimenBuilder` in C# for a .NET domain aggregate named 'Order'. The 'Order' class has a `Guid CustomerId` and a `List<OrderItem>`. The `OrderItem` class has an `int Quantity`. Ensure the generated 'Order' has a valid `CustomerId` and all `OrderItem` quantities are greater than 0."

```csharp
using AutoFixture;
using AutoFixture.Kernel;
using System;
using System.Collections.Generic;
using System.Linq;

public class Order
{
    public Guid CustomerId { get; set; }
    public List<OrderItem> OrderItems { get; set; } = new List<OrderItem>(); // Initialize to avoid null reference
}

public class OrderItem
{
    public Guid ProductId { get; set; } // Added for completeness
    public int Quantity { get; set; }
}

public class OrderCustomization : ISpecimenBuilder
{
    public object Create(object request, ISpecimenContext context)
    {
        if (request is Type type && type == typeof(Order))
        {
            var order = new Order
            {
                CustomerId = Guid.NewGuid(),
            };

            var fixture = context as IFixture; // Access the underlying fixture for further customization
            if (fixture == null)
            {
                return new NoSpecimen(); // Fallback if context is not a fixture
            }

            // Generate a reasonable number of OrderItems
            var numberOfItems = fixture.Create<int>() % 5 + 1; // Ensure at least one item
            for (int i = 0; i < numberOfItems; i++)
            {
                var item = fixture.Build<OrderItem>()
                                  .With(oi => oi.Quantity, Math.Max(1, fixture.Create<int>())) // Enforce quantity >= 1
                                  .Create();
                order.OrderItems.Add(item);
            }
            return order;
        }
        return new NoSpecimen();
    }
}
```

A crucial consideration arises when domain aggregates exhibit complex interdependencies or require nuanced validation logic that a general prompt might not fully capture. In such scenarios, you'll need to meticulously review and refine the generated code or provide more explicit instructions to Claude Code to guarantee that all business rules are accurately reflected in the resulting builder. Always validate the generated builder thoroughly within your test suite to confirm it precisely meets your testing objectives.
