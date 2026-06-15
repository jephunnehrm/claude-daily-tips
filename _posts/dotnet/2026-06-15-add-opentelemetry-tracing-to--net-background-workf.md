---
layout: post
title: "Add OpenTelemetry Tracing to .NET Background Workflows"
date: 2026-06-15
type: how-to
summary: "Enhance visibility into distributed .NET background tasks by automatically generating OpenTelemetry activity spans."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
---



![Add OpenTelemetry Tracing to .NET Background Workflows](assets/images/placeholder.jpg)



Manually instrumenting complex, asynchronous background workflows in .NET for distributed tracing can be a significant undertaking. Identifying every critical step, defining appropriate `Activity` spans, and ensuring consistent naming across potentially disparate services is time-consuming and prone to error, especially in event-driven architectures. This manual overhead often leads to incomplete or fragmented traces, hindering effective debugging and performance analysis.

The OpenTelemetry SDK for .NET provides the building blocks for comprehensive tracing, but generating the necessary boilerplate code for `ActivitySource` and `Activity` creation can still be tedious. This is where AI-assisted code generation can offer a powerful advantage. By understanding the context of your `BackgroundService` or other `IHostedService` implementations, AI can intelligently suggest and generate the OpenTelemetry instrumentation. This allows you to focus on the business logic while ensuring that key operations like message consumption, processing, and sub-tasks are automatically captured as traceable spans with appropriate metadata.

Consider a common scenario: a `BackgroundService` that dequeues messages from a queue. You need to trace the entire message processing lifecycle, from dequeueing to the internal operations within `ProcessMessageAsync`.

```csharp
using OpenTelemetry;
using OpenTelemetry.Trace;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Diagnostics;

public class QueuedBackgroundService : BackgroundService
{
    private readonly ILogger<QueuedBackgroundService> _logger;
    private readonly IMessageQueue _messageQueue;
    // Consistent naming is key for trace correlation
    private static readonly ActivitySource _activitySource = new ActivitySource("MyApp.BackgroundServices.Queued");

    public QueuedBackgroundService(ILogger<QueuedBackgroundService> logger, IMessageQueue messageQueue)
    {
        _logger = logger;
        _messageQueue = messageQueue;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var message = await _messageQueue.DequeueAsync(stoppingToken);
            if (message == null) continue;

            // AI can generate this span for message consumption
            using (var activity = _activitySource.StartActivity("ProcessMessage", ActivityKind.Consumer))
            {
                activity?.SetTag("message.id", message.Id);
                activity?.SetTag("message.type", message.Type);

                try
                {
                    _logger.LogInformation("Processing message {MessageId}...", message.Id);
                    await ProcessMessageAsync(message, stoppingToken);
                    _logger.LogInformation("Message {MessageId} processed successfully.", message.Id);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing message {MessageId}.", message.Id);
                    // AI can suggest this for robust error handling within spans
                    activity?.RecordException(ex);
                    throw;
                }
            }
        }
    }

    private Task ProcessMessageAsync(Message message, CancellationToken stoppingToken)
    {
        // AI can instrument nested operations for deeper insights
        using (var subActivity = _activitySource.StartActivity("ParseMessagePayload", ActivityKind.Internal))
        {
            subActivity?.SetTag("payload.size", message.Payload.Length);
            // ... complex parsing logic ...
        }
        // ... other processing steps ...
        return Task.CompletedTask;
    }
}

// Mock interfaces for compilation
public interface IMessageQueue { Task<Message?> DequeueAsync(CancellationToken cancellationToken); }
public class Message { public Guid Id { get; set; } public string Type { get; set; } = ""; public byte[] Payload { get; set; } = Array.Empty<byte>(); }
```

A critical gotcha is ensuring your `ActivitySource` name is consistent and descriptive across your entire application. Using generic names or duplicating `ActivitySource` instances with the same name can lead to fragmented traces and make it difficult to correlate events across different parts of your system. Remember that OpenTelemetry tracing is most effective when configured end-to-end, so properly setting up your SDK provider and exporters (e.g., `OpenTelemetry.Exporter.Console` or `OpenTelemetry.Exporter.OpenTelemetryProtocol`) in `Program.cs` is essential for visualizing your generated spans.

The "why" behind this approach lies in the inherent design of OpenTelemetry: creating `Activity` spans allows you to construct a directed acyclic graph (DAG) of operations. Each span represents a unit of work, and by linking them via parent-child relationships or causal dependencies, you build a narrative of your application's execution. AI assists by automating the creation of these spans and their associated metadata, providing the structured data necessary for distributed tracing systems to visualize, analyze, and debug your background workflows, a level of detail that goes beyond basic logging.
