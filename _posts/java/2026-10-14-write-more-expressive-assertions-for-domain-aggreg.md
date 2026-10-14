---
layout: post
title: "Write More Expressive Assertions for Domain Aggregates"
date: 2026-10-14
type: how-to
summary: "Quickly create custom AssertJ assertions for complex domain objects to make tests clearer."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - junit
  - claude-code
  - productivity
---



![Write More Expressive Assertions for Domain Aggregates](assets/images/placeholder.jpg)



Testing complex domain aggregates in Java applications, particularly those built with Spring Boot, often leads to repetitive and fragile assertion logic. Verifying the state of an aggregate, which can comprise multiple related entities and value objects, can result in verbose test methods that are difficult to maintain. Custom AssertJ assertions offer a powerful solution by encapsulating this logic into expressive, readable methods. However, crafting these custom assertions from scratch can be a time-consuming and error-prone endeavor.

To streamline the creation of these domain-specific assertions, Claude Code can be a significant accelerator. By providing Claude Code with a clear description of your domain aggregate and the specific validations you require, it can generate the boilerplate code for an `AbstractAssert` subclass. Consider an `Order` aggregate with an `OrderLines` collection. A common requirement is to assert the presence of an order line associated with a specific product ID. Claude Code can assist in generating an `OrderAssert` class with a dedicated method like `hasOrderLineWithProductId(String productId)`.

Here's an example of how you might instruct Claude Code. Given an `Order` class and an `OrderLine` class within the `com.example.domain` package, and aiming to create an `OrderAssert`:

```bash
claude generate --type assertj --class com.example.domain.Order --output-dir src/test/java --description "Generate an AssertJ assertion for the Order aggregate. Include a method to check if an order line with a specific product ID exists."
```

This command directs Claude Code to produce an AssertJ assertion (`--type assertj`) for the `com.example.domain.Order` class, specifying an output location. The `--description` flag is crucial; it guides Claude Code to generate a basic `OrderAssert` class, potentially pre-populating it with the requested `hasOrderLineWithProductId` method, thereby reducing initial development effort. This approach leverages the power of code generation to scaffold the repetitive parts of custom assertion writing.

A critical consideration is that Claude Code's generation is contingent on the clarity and completeness of your input. It may not automatically infer intricate domain relationships or edge cases within your aggregate. For instance, if an `OrderLine` contains multiple product identifiers (e.g., SKU, UPC), you will need to refine the generated code or guide Claude Code to target the correct field. Consequently, you must always review, adapt, and thoroughly test the generated assertions to ensure they accurately reflect your domain's behavior and cover all necessary scenarios, a step that goes beyond standard Spring documentation examples.

**Try it:** Execute the `claude` command above, substituting `com.example.domain.Order` with the fully qualified name of one of your domain aggregate roots.
