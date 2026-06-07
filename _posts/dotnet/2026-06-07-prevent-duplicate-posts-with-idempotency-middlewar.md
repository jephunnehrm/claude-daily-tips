---
layout: post
title: "Prevent Duplicate POSTs with Idempotency Middleware"
date: 2026-06-07
type: how-to
summary: "Implement a middleware to ensure POST requests are processed only once, preventing unintended side effects."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Prevent Duplicate POSTs with Idempotency Middleware](assets/images/placeholder.jpg)



One common, and frankly, frustrating challenge with public-facing ASP.NET Core APIs, especially those handling financial transactions or critical data, is the specter of duplicate POST requests. Network interruptions, aggressive client-side retries, or even subtle bugs can lead to the same data payload being submitted multiple times. This can result in a cascade of issues, from inconsistent application states to erroneous double charges. Manually bolting on deduplication logic to every POST endpoint is not only tedious but a breeding ground for bugs. Fortunately, ASP.NET Core's middleware pipeline provides an elegant, centralized solution for implementing robust request deduplication.

To address this head-on, we can craft a custom ASP.NET Core middleware. This middleware will intercept incoming POST requests and leverage a unique identifier, typically provided via an `Idempotency-Key` header. Upon receiving a request, the middleware will first check if an `Idempotency-Key` is present. If it is, the middleware queries a persistent store (such as an in-memory cache for simplicity, or a distributed cache like Redis for production environments) to see if this key has been processed recently. If a previous, successful response exists for this key, the middleware will immediately return that cached response, effectively short-circuiting the actual endpoint logic and preventing a duplicate execution. If the key is new, the middleware allows the request to proceed to the controller, captures the response, stores both the key and the response in the cache, and then forwards the original response to the client.

```csharp
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Caching.Memory;
using System;
using System.IO;
using System.Threading.Tasks;

public class IdempotencyMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IMemoryCache _cache;
    private const string IdempotencyKeyHeader = "Idempotency-Key";
    private const string CacheKeyPrefix = "Idempotency_";

    public IdempotencyMiddleware(RequestDelegate next, IMemoryCache cache)
    {
        _next = next ?? throw new ArgumentNullException(nameof(next));
        _cache = cache ?? throw new ArgumentNullException(nameof(cache));
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Only process POST requests
        if (!HttpMethods.IsPost(context.Request.Method))
        {
            await _next(context);
            return;
        }

        // Check for the idempotency key header
        if (!context.Request.Headers.TryGetValue(IdempotencyKeyHeader, out var idempotencyKey) || string.IsNullOrEmpty(idempotencyKey.ToString()))
        {
            // If no key, proceed without deduplication. Consider logging a warning or returning a BadRequest.
            await _next(context);
            return;
        }

        var cacheKey = $"{CacheKeyPrefix}{idempotencyKey}";

        // Try to retrieve a cached response
        if (_cache.TryGetValue(cacheKey, out var cachedResponse))
        {
            // If found, replay the cached response
            context.Response.StatusCode = StatusCodes.Status200OK; // Or a more specific 2xx code like 202 Accepted
            context.Response.ContentType = "application/json"; // Assuming JSON, adjust as needed
            await context.Response.WriteAsync(cachedResponse.ToString());
            return;
        }

        // If no cached response, capture the original response body
        var originalResponseBodyStream = context.Response.Body;
        using var responseBodyStream = new MemoryStream();
        context.Response.Body = responseBodyStream;

        try
        {
            // Execute the rest of the pipeline
            await _next(context);

            // Rewind the stream and read the response body
            responseBodyStream.Seek(0, SeekOrigin.Begin);
            var responseBody = await new StreamReader(responseBodyStream).ReadToEndAsync();

            // Store the response body in the cache
            var cacheEntryOptions = new MemoryCacheEntryOptions()
                .SetAbsoluteExpiration(TimeSpan.FromMinutes(30)); // Cache duration

            _cache.Set(cacheKey, responseBody, cacheEntryOptions);

            // Restore the original response body stream and write the response
            context.Response.Body = originalResponseBodyStream;
            await responseBodyStream.CopyToAsync(originalResponseBodyStream);
        }
        finally
        {
            // Ensure the original stream is restored even if an exception occurs
            if (context.Response.Body == responseBodyStream)
            {
                context.Response.Body = originalResponseBodyStream;
            }
        }
    }
}

// In Program.cs (ASP.NET Core 6+) or Startup.cs:
// builder.Services.AddMemoryCache();
// app.UseMiddleware<IdempotencyMiddleware>();
```

A significant practical consideration is the storage mechanism for these idempotency keys. While `IMemoryCache` is convenient for single-server scenarios, it will not persist across multiple instances of your application without careful configuration or a move to a distributed caching solution like Redis. Furthermore, precisely replicating the *entire* original response, including headers, status codes, and content types, can introduce complexity beyond simply caching the response body. This example, for conciseness, focuses on replaying the response body, but a production-ready solution might need to serialize and deserialize a more comprehensive response object.

To integrate this into your ASP.NET Core application, first ensure you have `Microsoft.Extensions.Caching.Memory` NuGet package installed and register `AddMemoryCache()` in your `Program.cs` or `Startup.cs`. Then, add `app.UseMiddleware<IdempotencyMiddleware>();` to your middleware pipeline, preferably before any middleware that might modify the response body or before your endpoint routing. By sending multiple identical POST requests with the same `Idempotency-Key` header to a test endpoint, you can verify that only the first request triggers your endpoint's actual logic, while subsequent identical requests are served directly from the cache.
