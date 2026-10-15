---
layout: post
title: "Graceful Shutdown for .NET Background Workers"
date: 2026-10-15
type: how-to
summary: "Ensure your .NET background services clean up properly during shutdown with Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-15-graceful-shutdown-for--net-background-workers.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Graceful Shutdown for .NET Background Workers](/claude-daily-tips/assets/images/dotnet-2026-10-15-graceful-shutdown-for--net-background-workers.jpg)



Ensuring your .NET background workers terminate cleanly, rather than being abruptly killed, is essential for data integrity and service stability. This common pain point arises when long-running operations are interrupted mid-execution, potentially leaving transactions incomplete or resources locked. While ASP.NET Core's `IHostedService` provides the framework, achieving a truly graceful shutdown requires understanding how to leverage cancellation tokens to signal ongoing work to finish its current task and release resources before exiting.

The `BackgroundService` base class, derived from `IHostedService`, significantly simplifies this pattern. It automatically manages a `CancellationToken` named `StoppingToken` that is signaled when the application is instructed to shut down. The critical step for implementing graceful shutdown is to actively check and propagate this `stoppingToken` throughout your background worker's asynchronous operations. By passing this token to methods like `Task.Delay`, `HttpClient.SendAsync`, or any other cancellable operation, you empower your worker to respond to shutdown requests promptly.

Here's a foundational example demonstrating how to integrate `StoppingToken` into a `BackgroundService`:

```csharp
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;

public class MyGracefulWorker : BackgroundService
{
    private readonly ILogger<MyGracefulWorker> _logger;

    public MyGracefulWorker(ILogger<MyGracefulWorker> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("GracefulWorker started at: {time}", DateTimeOffset.Now);
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                _logger.LogInformation("GracefulWorker performing work at: {time}", DateTimeOffset.Now);
                // Simulate a long-running operation, passing the stoppingToken
                await Task.Delay(5000, stoppingToken);
            }
            catch (TaskCanceledException)
            {
                _logger.LogWarning("GracefulWorker task was cancelled.");
                // The loop will naturally exit when stoppingToken.IsCancellationRequested is true
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An unexpected error occurred in GracefulWorker.");
                // Depending on the error, you might want to break or implement retry logic
                break;
            }
        }
        _logger.LogInformation("GracefulWorker stopping at: {time}", DateTimeOffset.Now);
        // Add any final cleanup here: saving state, closing connections, etc.
    }

    public override Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("GracefulWorker StopAsync called.");
        // The base implementation ensures the ExecuteAsync's stoppingToken is signaled.
        // We simply await its completion which is driven by the stoppingToken.
        return base.StopAsync(cancellationToken);
    }
}
```

A common oversight that prevents graceful shutdown is neglecting to pass the `stoppingToken` to asynchronous operations. For instance, if you use `Task.Delay(5000)` without the token, the delay will complete regardless of shutdown requests. The `BackgroundService`'s `StoppingToken` is designed to be the single source of truth for cancellation. By consistently passing it to all cancellable operations, you ensure that your worker can detect shutdown signals and break out of its work loop gracefully. Always verify that any third-party libraries you integrate also support `CancellationToken` for their long-running or potentially blocking operations.

To experiment with this pattern, add the `MyGracefulWorker` class to a .NET Worker project and register it in `Program.cs` with `builder.Services.AddHostedService<MyGracefulWorker>();`. When the application is running, pressing `Ctrl+C` will trigger the shutdown sequence, allowing you to observe the "stopping" messages in the logs, confirming that your worker is exiting cleanly.
