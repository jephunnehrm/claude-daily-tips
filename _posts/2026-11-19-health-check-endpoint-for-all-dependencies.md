---
layout: post
title: "Health Check Endpoint for All Dependencies"
date: 2026-11-19
type: how-to
summary: "Write a comprehensive health check endpoint that validates all downstream services and databases with Claude Code."
image: "/claude-daily-tips/assets/images/2026-11-19-health-check-endpoint-for-all-dependencies.jpg"
tags:
  - claude-code
  - productivity
  - cli
  - dotnet
  - automation
---



![Health Check Endpoint for All Dependencies](/claude-daily-tips/assets/images/2026-11-19-health-check-endpoint-for-all-dependencies.jpg)



Deploying microservices introduces complexity beyond just knowing if your application is running. A truly robust health check must go deeper, verifying the connectivity and responsiveness of all critical downstream dependencies—databases, message queues, external APIs, and other internal services. Manually crafting and maintaining these checks for every component in a growing system is a significant source of toil and a breeding ground for subtle bugs. Leveraging AI, like Claude Code, can dramatically streamline this, enabling efficient definition and implementation of these vital checks.

The core of a comprehensive health check lies in an API endpoint that systematically probes essential services. This is where Claude Code's contextual understanding and code generation capabilities shine. You can define a dedicated endpoint (e.g., `/health`) that, upon invocation, iterates through a predefined list of dependencies. For each dependency, it executes a minimal, quick operation: a simple PING, a lightweight query, or a basic API call. Crucially, if any check falters, the endpoint must signal failure with a non-200 status code and clearly indicate which dependency is at fault.

Consider this foundational structure for a C# ASP.NET Core health check endpoint, a common scenario where Claude Code excels. A prompt like "Generate a .NET 7 ASP.NET Core health check endpoint to verify connectivity with a SQL Server, an Azure Redis Cache, and an external `/api/v1/status` endpoint. The endpoint should return detailed diagnostics on any failing checks" would guide Claude Code to produce the necessary controller, interfaces for dependency checkers, and the underlying logic.

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    private readonly IEnumerable<IHealthCheck> _healthChecks;

    public HealthController(IEnumerable<IHealthCheck> healthChecks)
    {
        _healthChecks = healthChecks;
    }

    [HttpGet]
    public async Task<IActionResult> GetAsync()
    {
        var results = new Dictionary<string, HealthReportEntry>();
        var executionTasks = _healthChecks.Select(async check =>
        {
            var report = await check.CheckHealthAsync(new System.Threading.CancellationToken());
            results.Add(check.GetType().Name, new HealthReportEntry(report.Status, report.Description, report.Data, report.Exception));
        });

        await Task.WhenAll(executionTasks);

        bool allHealthy = results.Values.All(entry => entry.Status == HealthStatus.Healthy);

        if (allHealthy)
        {
            return Ok(results);
        }
        else
        {
            return StatusCode(503, results); // Service Unavailable
        }
    }
}
```

A critical pitfall is ensuring your health check operations remain truly lightweight. Avoid complex queries or actions that could themselves become performance bottlenecks or fail under heavy load. The objective is to rapidly ascertain *availability* and basic *responsiveness*, not deep operational capacity. Furthermore, differentiate between critical and optional dependencies. Your health check should reflect this, perhaps by returning different status codes or providing granular detail in the response to accurately represent system health. For instance, ask Claude Code: "Write a `PostgreSqlHealthCheck` implementation using Npgsql in C# that checks a database connection."
