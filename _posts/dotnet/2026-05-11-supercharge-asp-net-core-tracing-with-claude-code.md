---
layout: post
title: "Supercharge ASP.NET Core Tracing with Claude Code"
date: 2026-05-11
type: how-to
summary: "Effortlessly add OpenTelemetry tracing to your ASP.NET Core apps and inspect distributed calls with AI-powered insights."
image: "/claude-daily-tips/assets/images/dotnet-2026-05-11-supercharge-asp-net-core-tracing-with-claude-code.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - productivity
---



![Supercharge ASP.NET Core Tracing with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-05-11-supercharge-asp-net-core-tracing-with-claude-code.jpg)



Ever found yourself debugging a complex ASP.NET Core application, tracing requests across multiple services, and wishing for a clearer view of the distributed call flow? Manually instrumenting every piece of your application for tracing can be tedious and error-prone, especially in microservice architectures. You might spend hours correlating logs or staring at incomplete traces, trying to pinpoint performance bottlenecks or identify the root cause of errors.

This is where OpenTelemetry and Claude Code come to the rescue. OpenTelemetry provides a vendor-neutral standard for generating, collecting, and exporting telemetry data, making it a powerful tool for understanding your application's behavior. Claude Code, an AI coding assistant, can significantly accelerate the process of integrating and configuring OpenTelemetry, allowing you to focus on building features rather than boilerplate setup.

To get started, ensure you have the necessary OpenTelemetry NuGet packages installed in your ASP.NET Core project. You'll typically need `OpenTelemetry.AspNetCore` and an exporter, such as `OpenTelemetry.Exporter.Console` for local debugging or `OpenTelemetry.Exporter.OpenTelemetryProtocol` for sending data to a collector. Once installed, you can use Claude Code to generate the minimal configuration required. For example, you can ask Claude Code to "Add OpenTelemetry tracing to my ASP.NET Core app and configure it to export to the console."

Here's an example of how you might integrate OpenTelemetry with console exporting in your `Program.cs` file. After asking Claude Code to set this up, you'd typically review and potentially adjust the generated code. The key is that Claude Code can handle the initial setup of the `TracerProvider` and the middleware registration, which are crucial for enabling tracing across your ASP.NET Core application.

```csharp
// Add necessary NuGet packages:
// OpenTelemetry.AspNetCore
// OpenTelemetry.Exporter.Console

using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();

// Configure OpenTelemetry Tracing
builder.Services.AddOpenTelemetry()
    .WithTracing(tracingBuilder =>
    {
        tracingBuilder.AddAspNetCoreInstrumentation()
                      .AddConsoleExporter(); // For local debugging
    });

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
```

**Try it:** Run your ASP.NET Core application after applying this configuration and observe the trace output in your console.

Claude Code can also assist in configuring more advanced scenarios, such as integrating with distributed tracing systems like Jaeger or Zipkin, or setting up sampling strategies. By leveraging AI for the repetitive and sometimes complex setup of observability tools, .NET developers can significantly reduce the time spent on instrumentation and gain deeper insights into their application's performance and behavior more quickly.
