---
layout: post
title: "Robust ASP.NET Core API Calls with Polly and Claude Code"
date: 2026-10-26
type: how-to
summary: "Implement resilient HTTP requests in ASP.NET Core using Polly for retries, backoff, jitter, and fallbacks, guided by Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-26-robust-asp-net-core-api-calls-with-polly-and-claud.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Robust ASP.NET Core API Calls with Polly and Claude Code](/claude-daily-tips/assets/images/dotnet-2026-10-26-robust-asp-net-core-api-calls-with-polly-and-claud.jpg)



Transient network errors and flaky API dependencies can severely degrade the reliability of your ASP.NET Core applications, leading to frustrating user experiences. Manually implementing robust retry and fallback logic for every external HTTP call is not only time-consuming but also prone to subtle bugs. The Polly library offers a powerful, expressive, and maintainable solution for handling these resilience patterns. By integrating Polly with `HttpClientFactory`, you can declaratively build sophisticated resilience strategies for your API calls.

This article demonstrates how to configure Polly to implement common resilience patterns: retry with exponential backoff and jitter, and a fallback action. This approach ensures that if an API call fails, we don't overwhelm the service with immediate retries. Instead, we introduce a progressively increasing delay between attempts, along with a touch of randomness (jitter) to prevent synchronized retries from multiple clients, which can exacerbate load issues. If all retry attempts are exhausted, a fallback action provides a graceful degradation of service, preventing a complete application failure.

First, ensure you have the necessary Polly NuGet packages installed:
```bash
dotnet add package Polly
dotnet add package Polly.Extensions.Http
```
Within your `Program.cs` or a dedicated configuration class, you can set up an `HttpClient` with resilient policies using `HttpClientFactory`:

```csharp
using Microsoft.Extensions.DependencyInjection;
using Polly;
using Polly.Extensions.Http; // For HttpPolicyExtensions
using System;
using System.Net.Http;
using System.Threading.Tasks; // Ensure Task is available

// ...

var services = new ServiceCollection();

// Configure the HttpClient with Polly policies
services.AddHttpClient("MyApiClient")
    .AddPolicyHandler(HttpPolicyExtensions
        .HandleTransientHttpError() // Covers common transient errors like 5xx, timeouts
        .WaitAndRetryAsync(3, // Number of retries
            retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)), // Exponential backoff: 1s, 2s, 4s
            onRetry: (exception, timespan, retryCount, context) =>
            {
                Console.WriteLine($"\nOrdered retry {retryCount}: Delaying for {timespan}. Exception: {exception.Message}");
            }
        ))
    .AddPolicyHandler(Policy.Handle<HttpRequestException>()
        .CircuitBreakerAsync(
            exceptionsAllowedBeforeBreaking: 2, // Number of exceptions before breaking
            durationOfBreak: TimeSpan.FromSeconds(30), // Duration of the break
            onBreak: (exception, breakDelay) =>
            {
                Console.WriteLine($"\nCircuit broken. Delaying for {breakDelay}. Exception: {exception.Message}");
            },
            onReset: () =>
            {
                Console.WriteLine("\nCircuit reset.");
            },
            onHalfOpen: () =>
            {
                Console.WriteLine("\nCircuit half-open: Next call is a test.");
            }
        )
    )
    .AddPolicyHandler(Policy.Handle<Exception>() // Catch-all for any remaining exceptions
        .FallbackAsync(async (context, cancellationToken) =>
        {
            Console.WriteLine("All retries failed. Executing fallback logic.");
            // Your fallback logic here. This should return a valid HttpResponseMessage
            // even if it indicates an error or provides cached data.
            return new HttpResponseMessage(System.Net.HttpStatusCode.ServiceUnavailable)
            {
                Content = new StringContent("Service is temporarily unavailable. Please try again later.")
            };
        })
    );

// To use this HttpClient, inject IHttpClientFactory and create an instance.
// var httpClientFactory = services.BuildServiceProvider().GetRequiredService<IHttpClientFactory>();
// var httpClient = httpClientFactory.CreateClient("MyApiClient");
```

A significant gotcha to be aware of when using `HttpClientFactory` with Polly is the order of policy application. Policies added earlier are executed first. For instance, `AddPolicyHandler` for `WaitAndRetryAsync` should typically precede a `CircuitBreakerAsync` to allow retries before breaking the circuit. Furthermore, while `HttpPolicyExtensions.HandleTransientHttpError()` is convenient, it might not cover all error scenarios. You may need to explicitly define `Policy.Handle<SomeSpecificException>()` for custom error types or non-HTTP-related issues. The fallback action is your last line of defense; it must gracefully handle the failure, perhaps by returning cached data, a default response, or a specific error message to the user, rather than letting the application crash.

To test this, you can configure an HTTP endpoint in your application that you can intentionally make fail (e.g., a local service that returns 503 errors intermittently or a mocked endpoint). Observe the console output to see the retry messages, the delays between attempts, and the final fallback execution when all retries are exhausted. This practical application will solidify your understanding of how Polly enhances the resilience of your ASP.NET Core API interactions.
