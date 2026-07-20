---
layout: post
title: "Robust API Calls with Polly & Claude Code"
date: 2026-07-20
type: how-to
summary: "Implement resilient HTTP requests in ASP.NET Core using Polly's retry policies with exponential backoff, jitter, and fallback, guided by Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-20-robust-api-calls-with-polly---claude-code.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Robust API Calls with Polly & Claude Code](/claude-daily-tips/assets/images/dotnet-2026-07-20-robust-api-calls-with-polly---claude-code.jpg)



Calling external APIs from ASP.NET Core applications is a common source of unreliability. Network interruptions, transient service outages, and API rate limits can lead to abrupt failures, degrading the user experience and potentially compromising data integrity. While implementing robust retry mechanisms with strategies like exponential backoff, jitter, and fallbacks is a well-established pattern, manually coding these can be verbose, error-prone, and time-consuming. This is where leveraging developer tools like Claude Code can significantly accelerate the creation of resilient API integrations.

The Polly library is the go-to solution for resilience in .NET, offering a fluent API to define policies for retries, circuit breakers, timeouts, and fallbacks. For making robust HTTP requests with `HttpClientFactory` in ASP.NET Core, you can combine Polly with your `HttpClient` configuration. Claude Code can generate the C# code for a comprehensive retry policy that incorporates exponential backoff for increasing delays between retries, jitter to distribute load and prevent thundering herd issues, and a fallback action to execute when all retry attempts are exhausted.

Here’s how you might leverage Claude Code to generate this resilient HTTP client setup. After running the command, Claude can produce C# code similar to the following, often in the form of an extension method for `HttpClientBuilder`, ready to be integrated into your application's startup logic.

```csharp
using Polly;
using Polly.Retry;
using System;
using System.Net.Http;
using System.Net.Http.Extensions.Polly; // Assuming this extension exists or you adapt it

public static class HttpClientBuilderExtensions
{
    public static IHttpClientBuilder AddResilientHttpClient(this IHttpClientBuilder builder, string serviceName)
    {
        // Define the retry policy with exponential backoff and jitter
        var retryPolicy = Policy
            .Handle<HttpRequestException>() // Can also add specific HttpStatusCode handling here
            .WaitAndRetryAsync(
                5, // Maximum number of retries
                retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)) + TimeSpan.FromMilliseconds(new Random().Next(0, 100)), // Exponential backoff with jitter
                onRetry: (exception, timeSpan, retryCount, context) =>
                {
                    Console.WriteLine($"[{serviceName}] Retrying attempt {retryCount} after {timeSpan.TotalSeconds:F2}s due to {exception.Message}");
                });

        // Define the fallback policy for when retries are exhausted
        var fallbackPolicy = Policy
            .Handle<HttpRequestException>()
            .FallbackAsync(async (context, cancellationToken) =>
            {
                Console.WriteLine($"[{serviceName}] Fallback action executed. All retries failed.");
                // Implement fallback logic: e.g., return cached data, a default response, or throw a specific exception
                return new HttpResponseMessage(System.Net.HttpStatusCode.ServiceUnavailable)
                {
                    Content = new StringContent($"The {serviceName} service is currently unavailable. Please try again later.")
                };
            });

        // Combine the policies. Order matters: Retry then Fallback
        return builder.AddPolicyHandler(retryPolicy)
                      .AddPolicyHandler(fallbackPolicy);
    }
}
```

A crucial consideration when implementing fallbacks is to avoid blocking your application’s threads. If your fallback logic involves complex or synchronous operations, it can negate the benefits of asynchronous resilience. Ensure your fallback mechanism is non-blocking and efficiently provides an alternative or graceful degradation. Furthermore, Polly can be configured to retry on specific HTTP status codes (e.g., `5xx` errors) by adding `.OrResult(response => !response.IsSuccessStatusCode)` to your `Handle` clause, offering more granular control over when retries are appropriate. This approach, while leveraging a code generation tool, provides a deeper understanding of how Polly orchestrates resilience beyond basic retry loops, especially in complex distributed systems.
