---
layout: post
title: "Idempotent Payment Webhooks with Claude Code"
date: 2026-09-02
type: how-to
summary: "Write robust payment webhook handlers that avoid duplicate processing using Claude Code."
image: "/claude-daily-tips/assets/images/2026-09-02-idempotent-payment-webhooks-with-claude-code.jpg"
tags:
  - claude-code
  - productivity
  - cli
  - dotnet
  - automation
---



![Idempotent Payment Webhooks with Claude Code](/claude-daily-tips/assets/images/2026-09-02-idempotent-payment-webhooks-with-claude-code.jpg)



Processing payment provider callbacks, particularly webhooks, is a notorious source of operational friction. The most common culprit is duplicate webhook deliveries, often triggered by transient network issues or the payment provider's retry mechanisms. Without a robust idempotency strategy, your endpoint can inadvertently process the same event multiple times, leading to critical problems like double charges, corrupted state, or inaccurate reporting. Manually crafting these checks—tracking unique event identifiers, managing state persistence, and handling race conditions—is time-consuming and inherently prone to errors.

Leveraging AI, specifically Claude Code, can dramatically streamline the development of idempotent webhook handlers. By providing a precise prompt, you can instruct Claude Code to generate the necessary boilerplate, ensuring that each unique webhook event is acted upon only once. The typical implementation involves storing a processed event identifier in a persistent store like a database or cache and performing a lookup *before* executing your core business logic. The generated code should gracefully handle both the initial, legitimate processing and subsequent duplicate requests.

Here's a practical example of how you might prompt Claude Code for an idempotent webhook handler in C# for a hypothetical payment provider. The prompt should explicitly request idempotency and specify the mechanism, such as utilizing a unique `event_id` for database lookups.

```csharp
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using YourApp.Data; // Assuming you have a DbContext
using YourApp.Models; // Assuming you have a WebhookEvent model

[ApiController]
[Route("api/webhooks/payment")]
public class PaymentWebhookController : ControllerBase
{
    private readonly ApplicationDbContext _context;

    public PaymentWebhookController(ApplicationDbContext context)
    {
        _context = context;
    }

    [HttpPost("callback")]
    public async Task<IActionResult> HandlePaymentCallback([FromBody] PaymentWebhookPayload payload)
    {
        if (payload == null || string.IsNullOrEmpty(payload.EventId))
        {
            return BadRequest("Invalid payload or missing EventId.");
        }

        // Crucially, check if this event has already been processed BEFORE any significant work.
        var processedEvent = await _context.ProcessedWebhookEvents
            .FindAsync(payload.EventId);

        if (processedEvent != null)
        {
            // Event already processed, return success to acknowledge receipt and prevent retries.
            return Ok($"Event {payload.EventId} already processed.");
        }

        // **IMPORTANT:** Mark event as processed *immediately* and commit to prevent race conditions.
        // This ensures that if the application crashes *after* this point but *before* core logic,
        // the event won't be re-processed on retry.
        _context.ProcessedWebhookEvents.Add(new ProcessedWebhookEvent { EventId = payload.EventId, Timestamp = DateTime.UtcNow });
        await _context.SaveChangesAsync(); // Commit the idempotency marker

        // *** Core webhook processing logic goes here ***
        // This is now safe to execute, knowing the event is marked as processed.
        try
        {
            await ProcessPaymentEvent(payload);
            return Ok();
        }
        catch (Exception ex)
        {
            // Log the exception, and potentially implement a mechanism to requeue or alert.
            // For idempotency, we've already marked it as processed, so a simple retry won't double-process.
            System.Error.WriteLine($"Error processing event {payload.EventId}: {ex.Message}");
            return StatusCode(500, "Internal server error during processing.");
        }
    }

    private async Task ProcessPaymentEvent(PaymentWebhookPayload payload)
    {
        // Replace with your actual business logic for handling payment events.
        await Task.Delay(100); // Simulate work
        System.Console.WriteLine($"Processing payment event: {payload.EventId}");
    }
}

// Dummy models for demonstration purposes.
// In a real application, these would likely be more complex.
public class PaymentWebhookPayload
{
    public string EventId { get; set; }
    public string Type { get; set; }
    // ... other payment-specific fields relevant to your integration
}

public class ProcessedWebhookEvent
{
    // EventId should be the primary key or have a unique constraint in your database.
    public string EventId { get; set; }
    public DateTime Timestamp { get; set; }
}
```

A critical aspect of this pattern is the transaction handling. The event *must* be marked as processed and committed to the database *before* executing your core business logic. This prevents a race condition where the application might crash after marking the event but before completing its intended action. If a retry occurs, the initial lookup will correctly identify it as processed. Furthermore, ensure your `ProcessedWebhookEvent` table has a unique constraint on `EventId` at the database level, providing an extra layer of defense against simultaneous requests. This approach moves beyond simple code generation; it demonstrates a robust pattern for handling unreliable event streams, a common challenge for senior developers.

To experiment, create a new C# ASP.NET Core project and use Claude Code to generate the `PaymentWebhookController`. Set up a simple `ApplicationDbContext` that includes a `ProcessedWebhookEvents` DbSet. Then, simulate duplicate POST requests to `/api/webhooks/payment/callback` with identical `EventId`s and observe how the handler correctly processes the first request and acknowledges subsequent duplicates.
