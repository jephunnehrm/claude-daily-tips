---
layout: post
title: "Custom Assertions for Domain Aggregates with Claude Code"
date: 2026-09-17
type: how-to
summary: "Simplify complex domain object testing by generating custom AssertJ assertions with Claude Code."
image: "/claude-daily-tips/assets/images/java-2026-09-17-custom-assertions-for-domain-aggregates-with-claud.jpg"
tags:
  - java
  - spring
  - junit
  - claude-code
  - productivity
---



![Custom Assertions for Domain Aggregates with Claude Code](/claude-daily-tips/assets/images/java-2026-09-17-custom-assertions-for-domain-aggregates-with-claud.jpg)



Testing domain aggregates in Java often involves verifying the state of multiple related entities. While AssertJ provides excellent fluent assertions, crafting custom ones for frequently tested aggregate patterns can significantly reduce boilerplate and improve readability. Manually writing these custom assertions, especially for complex aggregates with many properties and relationships, can be a tedious and error-prone process. This is where Claude Code can shine, acting as your AI pair programmer to draft these specialized assertions.

Let's consider a simplified `Order` aggregate with a list of `OrderItem`s. Verifying that an order has a specific total price, customer details, and that each order item is correctly represented can lead to verbose tests. We can instruct Claude Code to generate an `OrderAssert` class that encapsulates these common checks.

Here's a command to ask Claude Code to generate a custom AssertJ assertion for a hypothetical `Order` aggregate. You'd typically run this in your terminal within your project directory:

```bash
claude --project-dir . --prompt "Generate a custom AssertJ assertion class named OrderAssert for a Java domain aggregate 'Order' with properties like 'orderId' (String), 'customerId' (String), 'totalAmount' (BigDecimal), and a list of 'OrderItem' objects. The OrderItem has properties 'productId' (String) and 'quantity' (int). The assertions should include checks for orderId, customerId, totalAmount, and verify that the order contains a specific OrderItem by productId and quantity." --output-file src/test/java/com/example/assertions/OrderAssert.java
```

This command leverages Claude Code's ability to understand project context (via `--project-dir`) and translate natural language prompts into code. The generated `OrderAssert.java` would then be integrated into your test suite, allowing you to write assertions like `assertThat(order).hasOrderId("123").hasCustomerId("cust456").containsOrderItem("prod789", 2);`. A gotcha to be aware of is that Claude Code might generate basic assertions, and you'll often need to refine the output, especially for intricate business logic or complex nesting within your aggregate. Always review and test the generated code thoroughly.

**Try it:** Run the `claude` command above in a sample Java project containing `Order` and `OrderItem` classes.
