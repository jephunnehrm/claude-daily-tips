---
layout: post
title: "Robust Payment API Calls with Polly Half-Open State"
date: 2026-07-28
type: how-to
summary: "Implement Polly circuit breaker with half-open monitoring to gracefully handle payment API failures and improve system resilience."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-28-robust-payment-api-calls-with-polly-half-open-stat.jpg"
tags:
  - dotnet
  - csharp
  - productivity
  - devtools
---



![Robust Payment API Calls with Polly Half-Open State](/claude-daily-tips/assets/images/dotnet-2026-07-28-robust-payment-api-calls-with-polly-half-open-stat.jpg)



When integrating with external payment APIs, network glitches or temporary service outages can lead to cascading failures in your application. You've likely experienced the frustration of watching user requests pile up and fail repeatedly when a downstream service is unavailable. Manually implementing retry logic and circuit breaking can be complex and error-prone. This is where Polly, a popular resilience library for .NET, shines, especially when we leverage its half-open state to intelligently test recovery.

Polly allows you to define policies for retries, timeouts, and circuit breakers. For a critical payment API, a circuit breaker is essential. The basic circuit breaker transitions to "Open" after a certain number of failures, preventing further calls to the unhealthy dependency. However, simply staying "Open" indefinitely can delay recovery. Polly's "Half-Open" state is crucial here: after a configured duration in the "Open" state, the circuit breaker enters "Half-Open," allowing a limited number of test requests. If these test requests succeed, the circuit breaker resets to "Closed," resuming normal operation.

Here's how you can implement a circuit breaker with a half-open state for your payment API calls. We'll assume you have an `IPaymentApiClient` interface and a `CreatePaymentAsync` method. You'll need to install the `Polly` NuGet package:

```bash
dotnet add package Polly
```

And then configure your Polly policy:

```csharp
using Polly;
using Polly.CircuitBreaker;
using System;
using System.Net.Http;
using System.Threading.Tasks;

public interface IPaymentApiClient
{
    Task<bool> CreatePaymentAsync(PaymentRequest request);
}

public class PaymentRequest { /* ... */ }

public class PaymentService
{
    private readonly AsyncCircuitBreakerPolicy _circuitBreakerPolicy;
    private readonly IPaymentApiClient _paymentApiClient;

    public PaymentService(IPaymentApiClient paymentApiClient)
    {
        _paymentApiClient = paymentApiClient;

        // Configure the circuit breaker policy
        _circuitBreakerPolicy = Policy
            .Handle<HttpRequestException>() // Or more specific exceptions from your API client
            .CircuitBreakerAsync(
                exceptionsAllowedBeforeBreaking: 3,      // Number of failures before opening the circuit
                durationOfBreak: TimeSpan.FromSeconds(30), // Duration to stay open before moving to half-open
                onBreak: (ex, breakDelay) =>
                {
                    Console.WriteLine($"Circuit broken. Waiting for {breakDelay.TotalSeconds} seconds before half-open. Exception: {ex.Message}");
                },
                onReset: (_) =>
                {
                    Console.WriteLine("Circuit reset. Closed.");
                },
                onHalfOpen: () =>
                {
                    Console.WriteLine("Circuit half-open: next call is a test.");
                }
            );
    }

    public async Task<bool> ProcessPaymentAsync(PaymentRequest request)
    {
        // Wrap the payment API call with the circuit breaker policy
        return await _circuitBreakerPolicy.ExecuteAsync(async () =>
        {
            // Your actual call to the payment API client
            return await _paymentApiClient.CreatePaymentAsync(request);
        });
    }
}
```

A key consideration is the `exceptionsAllowedBeforeBreaking` count and `durationOfBreak`. If your payment API occasionally experiences transient errors that resolve quickly, you might set `exceptionsAllowedBeforeBreaking` higher and `durationOfBreak` shorter to avoid unnecessarily opening the circuit. Conversely, for more severe issues, you'd want these values to be more conservative. The "gotcha" here is that the `onHalfOpen` action is executed *before* the test call, not after a successful test call. Polly itself doesn't provide a direct callback for *successful* half-open calls, you'd typically observe the circuit breaker state change back to "Closed" to infer success.

**Try it:** Integrate the `PaymentService` into your ASP.NET Core application and inject `IPaymentApiClient`. Then, call `ProcessPaymentAsync` multiple times, simulating failures in `CreatePaymentAsync` (e.g., by throwing `HttpRequestException`) to observe the circuit breaker transitions.
