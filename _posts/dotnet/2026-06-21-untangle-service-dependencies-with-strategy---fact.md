---
layout: post
title: "Untangle Service Dependencies with Strategy & Factory"
date: 2026-06-21
type: how-to
summary: "Refactor tightly coupled C# services into flexible, interchangeable components using Strategy and Factory patterns with Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-06-21-untangle-service-dependencies-with-strategy---fact.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Untangle Service Dependencies with Strategy & Factory](/claude-daily-tips/assets/images/dotnet-2026-06-21-untangle-service-dependencies-with-strategy---fact.jpg)



As a .NET developer, you've likely experienced the frustration of modifying one service and inadvertently breaking another – a telltale sign of tight coupling. This often stems from a single class taking on too many distinct responsibilities. Instead of resorting to "patch and pray," we can leverage established design patterns to untangle these dependencies. The Strategy pattern is invaluable for defining a family of algorithms, encapsulating each as a separate object, and making them interchangeable. Complementing this, the Factory pattern provides a clean way to abstract the instantiation of these interchangeable strategies.

Consider a common scenario: an `OrderProcessor` that needs to handle various payment methods like Credit Card, PayPal, and Bank Transfer. If the specific logic for each payment type is hardcoded directly within the `OrderProcessor`, introducing a new payment method necessitates modifying the `OrderProcessor` itself, directly violating the Open/Closed Principle. By extracting these payment-specific behaviors into distinct `IPaymentStrategy` implementations and using a factory to manage their creation, we can achieve a much more flexible and maintainable design.

To accelerate this refactoring process, you can leverage tools like the `claude` CLI. Imagine you have a `PaymentProcessor.cs` file with interleaved logic for different payment types. A command like the following can initiate the refactoring:

```csharp
// Initial, tightly coupled example (simplified for illustration)
public class OrderProcessor
{
    public void ProcessOrder(Order order, PaymentDetails paymentDetails)
    {
        if (paymentDetails.Type == PaymentType.CreditCard)
        {
            // Credit card logic
        }
        else if (paymentDetails.Type == PaymentType.PayPal)
        {
            // PayPal logic
        }
        // ... and so on
    }
}
```

You could then prompt the `claude` CLI:

```bash
claude refactor --pattern strategy --pattern factory --input PaymentProcessor.cs --output PaymentRefactoring
```

This command instructs `claude` to analyze your `PaymentProcessor.cs`, apply the Strategy and Factory patterns, and place the refactored code into a new directory named `PaymentRefactoring`. It will identify common behaviors, propose `IPaymentStrategy` interface definitions, generate concrete strategy classes (e.g., `CreditCardPaymentStrategy`), and create a `PaymentStrategyFactory` to abstract their instantiation, leading to a more maintainable and extensible codebase.

A critical point to remember with this approach is ensuring the factory accurately determines and instantiates the correct strategy based on runtime context – for example, by inspecting a `PaymentType` enum. If the factory's lookup mechanism is flawed, it can lead to runtime errors where the wrong payment processing logic is executed. Furthermore, while powerful, over-applying these patterns to very simple scenarios can introduce unnecessary complexity and indirection, making the code harder to follow.

**Try it:** Identify a service in your .NET project that currently handles multiple distinct but related operations. Use the `claude refactor` command to explore refactoring it into Strategy and Factory patterns and observe how the resulting code promotes better separation of concerns and extensibility.
