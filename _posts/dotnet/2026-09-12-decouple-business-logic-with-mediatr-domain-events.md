---
layout: post
title: "Decouple Business Logic with MediatR Domain Events"
date: 2026-09-12
type: how-to
summary: "Learn how to use MediatR to implement domain events, cleanly decoupling business logic in ASP.NET Core applications."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-12-decouple-business-logic-with-mediatr-domain-events.jpg"
tags:
  - dotnet
  - csharp
  - productivity
---



![Decouple Business Logic with MediatR Domain Events](/claude-daily-tips/assets/images/dotnet-2026-09-12-decouple-business-logic-with-mediatr-domain-events.jpg)



Many ASP.NET Core applications, particularly those embracing Domain-Driven Design (DDD) principles, wrestle with the insidious problem of tightly coupled business logic. When a pivotal domain event occurs, such as an `OrderPlaced` event, numerous disparate parts of the system often need to react: sending confirmation emails, updating inventory levels, or triggering user notifications. Manually orchestrating these diverse reactions directly within the same service or controller inevitably leads to convoluted codebases, making them brittle, arduous to maintain, challenging to test, and difficult to extend.

MediatR, a widely adopted .NET library, provides an elegant solution by implementing the mediator pattern. When paired with the concept of domain events, it empowers us to construct highly decoupled systems. A domain event fundamentally represents a notification that a significant occurrence has transpired within the domain. Instead of the originating component directly invoking other services or functionalities, the aggregate root (or whichever component is responsible for the domain event) simply publishes the event. Handlers that are interested in this event, and have been registered with MediatR, subsequently receive and process it, either asynchronously or synchronously.

To implement this, begin by ensuring you have the necessary MediatR packages installed: `MediatR` and `MediatR.Extensions.Microsoft.DependencyInjection`. Next, you'll define your domain event and its corresponding handler. For instance, consider an `OrderPlaced` event:

```csharp
// Domain Event Definition
public record OrderPlaced(int OrderId, DateTime OrderDate, decimal TotalAmount) : INotification;

// Domain Event Handler
public class OrderPlacedEmailHandler : INotificationHandler<OrderPlaced>
{
    private readonly IEmailService _emailService; // Assume IEmailService is a registered dependency

    public OrderPlacedEmailHandler(IEmailService emailService)
    {
        _emailService = emailService;
    }

    public async Task Handle(OrderPlaced notification, CancellationToken cancellationToken)
    {
        // This handler is responsible for sending an order confirmation email.
        await _emailService.SendOrderConfirmationAsync(notification.OrderId, notification.TotalAmount);
    }
}
```
In your application's bootstrapping code (e.g., `Program.cs` in modern .NET Core applications), register MediatR and configure it to discover your handlers:

```csharp
// In Program.cs
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));
// Ensure IEmailService and other necessary services are also registered.
```
When your domain logic dictates that an order has been placed, you would inject `IMediator` and publish the event:

```csharp
public class OrderService
{
    private readonly IMediator _mediator;

    public OrderService(IMediator mediator)
    {
        _mediator = mediator;
    }

    public async Task PlaceOrderAsync(Order order) // Assume 'Order' is a domain entity
    {
        // ... core business logic for placing an order ...

        // Publish the domain event, notifying interested parties.
        await _mediator.Publish(new OrderPlaced(order.Id, order.OrderDate, order.TotalAmount));
    }
}
```
A significant consideration with MediatR's `INotification` is that all registered handlers for a given notification type will execute sequentially in the order they are discovered by MediatR. While this behavior is acceptable for simple scenarios, it can become a bottleneck and obscure execution flow for complex event processing. For robust asynchronous processing, including features like retries and dead-lettering, it's advisable to integrate with dedicated message queuing systems like Azure Service Bus or RabbitMQ. In such architectures, MediatR can act as the initial publisher, seamlessly forwarding messages to the queue for further processing.

**Challenge:** Implement a `ProductCreated` domain event. Create a handler for this event that logs the event's details to the console. This exercise will solidify your understanding of defining events and handlers, and observing their execution.
