---
layout: post
title: "Simplify Aggregate Object Testing with Custom Assertions"
date: 2026-09-09
type: how-to
summary: "Reduce repetitive AssertJ code for domain aggregates by generating custom assertions with Claude Code."
image: "/claude-daily-tips/assets/images/java-2026-09-09-simplify-aggregate-object-testing-with-custom-asse.jpg"
tags:
  - java
  - spring
  - junit
  - claude-code
  - productivity
---



![Simplify Aggregate Object Testing with Custom Assertions](/claude-daily-tips/assets/images/java-2026-09-09-simplify-aggregate-object-testing-with-custom-asse.jpg)



You're deep in the weeds of a new feature, and your domain aggregates are becoming more complex. Testing these aggregates often involves writing the same boilerplate assertions repeatedly for each entity within them. For instance, asserting that a `Customer` aggregate contains a specific `Address` with certain properties, or that an `Order` has the correct line items, can lead to verbose and fragile test code. This is a prime candidate for improving your testing efficiency.

AssertJ's fluent API is fantastic, but when dealing with deeply nested aggregate structures, the `assertThat(customer.getAddress()).isEqualTo(...)` pattern can become cumbersome. What if you could write `assertThat(customer).hasAddress(addressDetails)`? Leveraging AI-powered code generation, specifically through the `claude` CLI, can help you generate these custom, domain-specific assertions, making your tests more readable and robust against minor domain model refactors. By inspecting your aggregate's structure, these tools can generate tailored `Assertion` classes that reflect the intent of your domain, not just the direct exposure of its properties.

To get started, ensure you have the `claude` CLI installed. Then, you can point it at your aggregate class and ask it to generate an AssertJ assertion extension. For example, if you have a `Customer` aggregate with a `firstName` property and an `email` property, you might use a command like this to generate a `CustomerAssert` class:

```bash
claude generate assertj-assertion --class com.example.domain.Customer --output-dir src/test/java/com/example/assertions
```

This command will analyze the `com.example.domain.Customer` class and create a `CustomerAssert` file within the specified output directory, potentially providing methods like `hasFirstName(String)` or `hasEmail(String)`. A potential gotcha is that AI code generation's analysis might not always capture the full nuance of your aggregate's internal state if it relies heavily on private methods or complex relationships not directly exposed by public getters. You might need to manually refine the generated assertions to account for these cases, especially when dealing with collections within the aggregate or when the assertion needs to capture a specific business invariant rather than just a direct property match.

**Try it:** Run the `claude` CLI command above, adapting the class name and output directory to match your project's structure and a sample aggregate. Then, refactor an existing test to use your newly generated custom assertion. By abstracting complex nested assertions into a single, intention-revealing method, you reduce the cognitive load during test reading and make your tests more resilient to changes in how your aggregate's internal state is accessed, as long as the overall observable behavior remains consistent.
