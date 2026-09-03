---
layout: post
title: "Untangle Dependent Services with Strategy and Factory"
date: 2026-09-03
type: how-to
summary: "Refactor tightly coupled .NET services into flexible, maintainable code using Claude Code and design patterns."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-03-untangle-dependent-services-with-strategy-and-fact.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
---



![Untangle Dependent Services with Strategy and Factory](/claude-daily-tips/assets/images/dotnet-2026-09-03-untangle-dependent-services-with-strategy-and-fact.jpg)



As a .NET developer, you've undoubtedly faced the challenge of a `NotificationService` class that tries to do too much. When a single service orchestrates diverse operations, like sending emails, SMS, or push notifications through a tangled web of `switch` statements or `if-else` blocks, it becomes a bottleneck for maintenance and testing. This tight coupling makes it difficult to introduce new notification channels or modify existing ones without impacting unrelated logic. Refactoring such monolithic services into more manageable, single-responsibility components is a common, albeit often time-consuming, task. Fortunately, AI-powered developer tools can significantly accelerate this process by intelligently applying established design patterns like Strategy and Factory.

Let's illustrate with a `NotificationService` that currently handles multiple delivery mechanisms within a single method.

```csharp
// Before Refactoring
public class NotificationService
{
    public void SendNotification(string recipient, string message, NotificationType type)
    {
        switch (type)
        {
            case NotificationType.Email:
                // Placeholder for actual email sending logic
                System.Console.WriteLine($"Sending Email to {recipient}: {message}");
                break;
            case NotificationType.Sms:
                // Placeholder for actual SMS sending logic
                System.Console.Console.WriteLine($"Sending SMS to {recipient}: {message}");
                break;
            case NotificationType.Push:
                // Placeholder for actual push notification sending logic
                System.Console.Console.WriteLine($"Sending Push to {recipient}: {message}");
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(type), type, "Unsupported notification type.");
        }
    }
}

public enum NotificationType
{
    Email,
    Sms,
    Push
}
```

The Strategy pattern is ideal for untangling this. It allows us to define a family of algorithms (how to send each notification type), encapsulate each one into a separate class, and make them interchangeable. We'd introduce an `INotificationStrategy` interface with a `Send` method, and then create concrete implementations like `EmailNotificationStrategy`, `SmsNotificationStrategy`, and `PushNotificationStrategy`. The `NotificationService` would then delegate the actual sending to the appropriate strategy object.

A common challenge with the Strategy pattern, especially as your application grows, is managing the instantiation of these many strategy objects. Deciding which concrete strategy to create at runtime can lead back to conditional logic, defeating the purpose of encapsulation. This is precisely where the Factory pattern shines. A `NotificationStrategyFactory` can abstract away the creation of `INotificationStrategy` instances, returning the correct implementation based on a `NotificationType`. This decouples the `NotificationService` (or any other client code) from the concrete strategy implementations, making it trivially easy to add new notification types without modifying existing client code, only the factory. This separation of concerns is key to building maintainable and extensible .NET applications.
