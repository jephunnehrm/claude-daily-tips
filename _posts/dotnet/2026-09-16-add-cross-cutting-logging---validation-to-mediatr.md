---
layout: post
title: "Add Cross-Cutting Logging & Validation to MediatR Requests"
date: 2026-09-16
type: how-to
summary: "Leverage Claude Code to quickly create MediatR IPipelineBehaviors for consistent logging and validation across your ASP.NET Core application."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-16-add-cross-cutting-logging---validation-to-mediatr.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Add Cross-Cutting Logging & Validation to MediatR Requests](/claude-daily-tips/assets/images/dotnet-2026-09-16-add-cross-cutting-logging---validation-to-mediatr.jpg)



As your ASP.NET Core application scales, manually instrumenting every MediatR request handler with cross-cutting concerns like detailed logging and input validation quickly becomes a maintenance nightmare. This repetitive effort leads to code duplication, increases the likelihood of errors, and hinders rapid development. MediatR's `IPipelineBehavior` offers an elegant solution by allowing you to inject logic that executes *before* or *after* your request handlers. While AI tools like Claude Code can accelerate the generation of boilerplate for these behaviors, understanding the underlying principles is key to effective implementation.

Let's address the need for robust logging and a foundational level of validation. We'll craft an `IPipelineBehavior` that captures essential request metadata and performs an initial null check. The prompt for an AI assistant would focus on generating a generic `IPipelineBehavior` that leverages `Microsoft.Extensions.Logging.ILogger` to record the request type, its execution duration, and includes a critical guard clause against null requests. More sophisticated validation, such as using FluentValidation, would typically be integrated as a separate pipeline behavior or within handlers themselves.

```csharp
// Claude Code Generation Input Example:
// Create a C# IPipelineBehavior for MediatR that logs the request name, start time, and end time.
// Also, add a basic check to ensure the request object is not null before proceeding.
// Use the Microsoft.Extensions.Logging.ILogger interface.

using MediatR;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System; // Required for DateTime and Exception

public class LoggingAndValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<LoggingAndValidationBehavior<TRequest, TResponse>> _logger;

    public LoggingAndValidationBehavior(ILogger<LoggingAndValidationBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
    {
        // Foundational validation: Ensure the request object itself is not null.
        // A null request indicates a fundamental issue with how the request was initiated.
        if (request == null)
        {
            _logger.LogError("Received a null request of type {RequestType}", typeof(TRequest).Name);
            // It's crucial to handle null requests explicitly. Throwing an ArgumentNullException
            // provides immediate feedback and prevents further processing of invalid input.
            throw new ArgumentNullException(nameof(request), $"Request of type {typeof(TRequest).Name} cannot be null.");
        }

        var requestName = typeof(TRequest).Name;
        _logger.LogInformation("Handling request {RequestName} at {Time} UTC", requestName, DateTime.UtcNow);
        var stopwatch = Stopwatch.StartNew();

        try
        {
            // The 'await next()' call is the core of the pipeline. It invokes the next behavior
            // in the chain, or the actual request handler if this is the last behavior.
            var response = await next();
            stopwatch.Stop();
            _logger.LogInformation("Successfully handled request {RequestName} in {ElapsedMilliseconds} ms", requestName, stopwatch.ElapsedMilliseconds);
            return response;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            // Log any exceptions that occur during handler execution, along with the elapsed time.
            // Re-throwing the exception ensures that it's propagated up the pipeline for potential
            // higher-level error handling or global exception management.
            _logger.LogError(ex, "Error handling request {RequestName} after {ElapsedMilliseconds} ms", requestName, stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}
```

Integrating this `LoggingAndValidationBehavior` into your ASP.NET Core application is straightforward. Register it within your MediatR configuration in `Program.cs` (or `Startup.cs`). The critical step is ensuring the behavior is added to the pipeline. A common oversight is forgetting to add the behavior using `AddBehavior`, or misplacing it in the registration order if multiple behaviors are present. The `AddMediatR` extension method, when configured to scan assemblies, will automatically discover and register your handlers, but pipeline behaviors require explicit registration.

```bash
dotnet add package MediatR.Extensions.Microsoft.DependencyInjection
```
Then, in `Program.cs`:
```csharp
builder.Services.AddMediatR(cfg => {
    cfg.RegisterServicesFromAssembly(typeof(Program).Assembly);
    // Explicitly add the pipeline behavior to the MediatR pipeline.
    // The generic type arguments <,> tell MediatR to apply this behavior to all request/response types.
    cfg.AddBehavior<LoggingAndValidationBehavior<,>>();
});
```

**Experimentation:** After updating your `Program.cs`, send a request to your API. Observe the console output for log messages detailing the start, duration, and completion (or any errors) of your request processing. This hands-on approach will solidify your understanding of how `IPipelineBehavior` intercepts and enhances request execution, providing a robust foundation for managing cross-cutting concerns without cluttering your core business logic.
