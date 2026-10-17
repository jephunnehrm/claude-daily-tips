---
layout: post
title: "Prevent Payment API Outages with Polly Half-Open"
date: 2026-10-17
type: how-to
summary: "Learn to implement a resilient payment API using Polly's circuit breaker with half-open monitoring to minimize downtime."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-17-prevent-payment-api-outages-with-polly-half-open.jpg"
tags:
  - dotnet
  - csharp
  - devtools
---



![Prevent Payment API Outages with Polly Half-Open](/claude-daily-tips/assets/images/dotnet-2026-10-17-prevent-payment-api-outages-with-polly-half-open.jpg)



Ever faced a critical payment API throwing intermittent errors, leaving you wishing you could temporarily pause requests without completely halting your application? This is a classic .NET developer pain point, and Polly's circuit breaker pattern, particularly its "half-open" state, offers an elegant solution. By intercepting calls to a struggling payment gateway, a circuit breaker prevents your application from overwhelming the failing service, thus enhancing overall system stability and user experience. The "half-open" state is the key to gracefully recovering from outages by cautiously reintroducing the service once it might have healed.

To implement this, you'll leverage the Polly NuGet package. Install it with `dotnet add package Polly`. Within your service responsible for payment gateway interactions, define an `AsyncCircuitBreakerPolicy`. The core of the half-open functionality lies in configuring `CircuitBreakerPolicyOptions`. You set `exceptionsAllowedBeforeBreaking` (e.g., to `2`) to define how many consecutive failures trigger the circuit break. `durationOfBreak` then dictates how long the circuit remains open before transitioning to the half-open state. In this state, Polly allows a single request to pass. If this request succeeds, the circuit resets to closed; if it fails, the circuit immediately breaks again, restarting the `durationOfBreak` timer.

Here's a practical example for an ASP.NET Core application interacting with a hypothetical `IPaymentGateway`:

```csharp
using Polly;
using Polly.CircuitBreaker;
using System;
using System.Net.Http;
using System.Threading.Tasks;

public class PaymentService
{
    private readonly HttpClient _httpClient;
    private readonly AsyncCircuitBreakerPolicy _circuitBreakerPolicy;

    public PaymentService(HttpClient httpClient)
    {
        _httpClient = httpClient;

        _circuitBreakerPolicy = Policy
            .Handle<HttpRequestException>() // Target exceptions indicating transient network issues or gateway unavailability
            .CircuitBreakerAsync(
                exceptionsAllowedBeforeBreaking: 2, // Break after 2 consecutive failures
                durationOfBreak: TimeSpan.FromSeconds(30), // Stay broken for 30 seconds
                onBreak: (ex, breakDelay) =>
                {
                    Console.WriteLine($"Circuit breaker tripped for {breakDelay.TotalSeconds}s. Exception: {ex.GetType().Name}");
                    // Implement alerting or detailed logging here for operational awareness
                },
                onReset: () =>
                {
                    Console.WriteLine("Circuit breaker reset to closed state.");
                    // Potentially re-enable specific health checks or notifications
                },
                onHalfOpen: () =>
                {
                    Console.WriteLine("Circuit breaker transitioning to half-open. Testing connectivity.");
                    // Notify monitoring that a test request is imminent
                }
            );
    }

    public async Task<bool> ProcessPaymentAsync(decimal amount, string cardDetails)
    {
        return await _circuitBreakerPolicy.ExecuteAsync(async () =>
        {
            Console.WriteLine("Attempting payment processing...");
            // In a real scenario, this would be your actual HTTP call to the payment gateway.
            // For demonstration, we simulate a failure.
            var random = new Random();
            if (random.Next(0, 5) < 2) // Simulate a ~40% failure rate
            {
                throw new HttpRequestException("Simulated payment gateway unavailable.");
            }

            await Task.Delay(100); // Simulate network latency
            Console.WriteLine("Payment processed successfully.");
            return true;
        });
    }
}
```

A critical "gotcha" with the half-open state is managing the *types* of exceptions your circuit breaker handles. If your payment API can fail for non-transient reasons (e.g., invalid credentials, business rule violations), Polly might incorrectly trip the breaker or repeatedly fail in the half-open state. It's crucial to configure `Handle` to target only exceptions indicative of temporary network problems or service unavailability, allowing persistent errors to be handled differently, perhaps by your application's core error handling. This ensures Polly effectively protects against transient issues and facilitates graceful recovery.
