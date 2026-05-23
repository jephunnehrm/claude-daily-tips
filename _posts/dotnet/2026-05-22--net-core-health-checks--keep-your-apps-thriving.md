---
layout: post
title: ".NET Core Health Checks: Keep Your Apps Thriving"
date: 2026-05-22
type: how-to
summary: "Ensure your ASP.NET Core applications are always healthy and responsive with built-in health checks and readiness probes."
image: "/claude-daily-tips/assets/images/dotnet-2026-05-22--net-core-health-checks--keep-your-apps-thriving.jpg"
tags:
  - dotnet
  - csharp
  - devtools
  - azure
---



![.NET Core Health Checks: Keep Your Apps Thriving](/claude-daily-tips/assets/images/dotnet-2026-05-22--net-core-health-checks--keep-your-apps-thriving.jpg)



Ever deployed an ASP.NET Core application only to wonder if it's *really* up and running, or if a downstream dependency has failed silently? Manually checking individual services or relying solely on basic uptime monitoring can leave you in the dark about the true operational state of your application. This is where health checks and readiness probes become indispensable. They provide a standardized way to expose the health status of your application and its dependencies, allowing orchestrators like Kubernetes or Azure App Service to make informed decisions about traffic routing and restarts.

ASP.NET Core offers a robust health check middleware through the `Microsoft.AspNetCore.Diagnostics.HealthChecks` NuGet package. This package allows you to define checks for various aspects of your application, such as database connectivity, external API reachability, or even the status of background tasks. By registering these checks in your `Startup.cs` (or `Program.cs` in .NET 6+), you can expose a dedicated health endpoint that provides a clear, actionable status.

Here's how you can set up a basic health check endpoint and a simple check for a hypothetical service:

```csharp
// In Program.cs (.NET 6+) or Startup.cs
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Threading;
using System.Threading.Tasks;

// Define a custom health check
public class MyCustomHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        // Simulate a check, e.g., checking a service, database, or cache
        bool isHealthy = true; // Replace with your actual check logic

        if (isHealthy)
        {
            return Task.FromResult(HealthCheckResult.Healthy("My custom service is healthy."));
        }
        else
        {
            return Task.FromResult(new HealthCheckResult(context.Registration.FailureStatus, "My custom service is unhealthy."));
        }
    }
}

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddHealthChecks()
    .AddCheck<MyCustomHealthCheck>("MyCustomService"); // Register your custom check

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseHealthChecks("/health"); // Expose the health check endpoint at /health
app.UseHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = (registration) => registration.Tags.Contains("ready"),
    ResponseWriter = async (httpContext, result) =>
    {
        httpContext.Response.ContentType = "application/json";
        var response = new { Status = result.Status.ToString(), Checks = result.Entries.Select(e => new { Key = e.Key, Value = e.Value.Status.ToString() }) };
        await httpContext.Response.WriteAsJsonAsync(response);
    }
}); // Example of a readiness probe with custom output

// ... other middleware and endpoint mappings

app.Run();
```

To make this code work, ensure you have the `Microsoft.AspNetCore.Diagnostics.HealthChecks` NuGet package installed. Then, you can test your health endpoint by making an HTTP GET request to `/health` on your running application. For a readiness probe, you'd typically configure your orchestrator to hit a specific endpoint (e.g., `/health/ready`) and check for a successful HTTP status code (like 200 OK).

**Try it:** Run the provided code snippet and navigate to `http://localhost:<your-port>/health` in your browser. You should see a `Content-Type: text/plain; charset=utf-8` response indicating "Healthy". If you were to simulate an unhealthy state within `MyCustomHealthCheck`, the response would change.

By implementing health checks, you gain visibility into your application's internal state and provide critical signals to deployment and orchestration systems. This proactive approach helps in early detection of issues, automated recovery, and ultimately, a more resilient and reliable application. Readiness probes, in particular, are crucial for ensuring that an application is not only running but also fully initialized and ready to serve traffic before it's exposed to users.
