---
layout: post
title: "Custom AutoFixture Builders for Domain Aggregates"
date: 2026-09-26
type: how-to
summary: "Accelerate domain object testing by having Claude Code create AutoFixture specimen builders."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-26-custom-autofixture-builders-for-domain-aggregates.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Custom AutoFixture Builders for Domain Aggregates](/claude-daily-tips/assets/images/dotnet-2026-09-26-custom-autofixture-builders-for-domain-aggregates.jpg)



Manually configuring complex object graphs for testing domain aggregates can be a significant bottleneck. When your aggregates involve deep hierarchies or intricate interdependencies between entities, writing custom `ISpecimenBuilder` implementations for AutoFixture becomes a time-consuming and error-prone endeavor. This manual process distracts from valuable development time that could be spent on core domain logic. Fortunately, tools like Claude Code can dramatically streamline this process by assisting in the generation of these crucial custom builders, ensuring your test data accurately reflects your domain's intended state. By automating the boilerplate code for builder creation, you can reclaim focus and apply your expertise to the nuances of your domain, rather than wrestling with test data setup.

Consider a common scenario: an `Order` aggregate that comprises `OrderItems`, a `ShippingAddress`, and a `BillingAddress`, each with their own set of complex properties. Manually crafting an `OrderBuilder` to meticulously validate relationships and populate these components accurately is a substantial task. Instead, you can leverage Claude Code to generate the foundational builder for your `Order` class. By providing the class definition and a clear description of desired builder behavior – such as enforcing default values for specific properties or ensuring collections are pre-populated – Claude Code can produce a robust C# class that inherits from `ISpecimenBuilder`. This generated code seamlessly integrates with AutoFixture's `IFixture` instance, significantly accelerating your test setup.

For instance, imagine you have an `Order` class and require a builder that guarantees the `OrderDate` is always set to a sensible default and that the `OrderItems` collection is populated with at least one item. You could achieve this with a prompt like:

```bash
claude create specimen-builder --for Order --with OrderDate=DateTime.UtcNow --with OrderItems=1+
```

This command directs Claude Code to generate an `OrderBuilder` class. The `--with` arguments translate into concrete logic within the builder's `Create` method, ensuring `OrderDate` is assigned `DateTime.UtcNow` and `OrderItems` contains a minimum of one element. This intelligent generation handles the underlying `ISpecimenBuilder` contract and the necessary instantiation logic, leading to cleaner and more maintainable test code.

While Claude Code excels at generating common patterns and fulfilling straightforward requirements, it's crucial to recognize its limitations. For highly complex scenarios involving intricate business rules or recursive dependencies within your aggregates, the generated builders serve as an excellent starting point but may require manual refinement. Claude Code is not a substitute for deep domain understanding. Developers will still need to intervene for scenarios that demand nuanced business logic or specific handling of circular references. Furthermore, ensure your domain objects are designed with accessible constructors or public setters that the generated builder can effectively utilize.

**Try it:** Create a simple `Product` class with a `Price` property, like this:

```csharp
public class Product
{
    public decimal Price { get; set; }
}
```

Then, use the following command to generate a builder:

```bash
claude create specimen-builder --for Product --with Price=19.99
```

Subsequently, integrate this builder into your AutoFixture `IFixture` instance within a test to verify the `Price` is correctly set.
