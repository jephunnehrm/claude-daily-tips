---
layout: post
title: "Cache ASP.NET Core Responses with Tag Invalidation"
date: 2026-07-04
type: how-to
summary: "Implement dynamic output caching in ASP.NET Core using Claude Code and tag-based invalidation for efficient data freshness."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-04-cache-asp-net-core-responses-with-tag-invalidation.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Cache ASP.NET Core Responses with Tag Invalidation](/claude-daily-tips/assets/images/dotnet-2026-07-04-cache-asp-net-core-responses-with-tag-invalidation.jpg)



Serving dynamic content quickly while ensuring it's up-to-date is a common hurdle for .NET developers. Manually managing cache expiration, especially when multiple data sources contribute to a single response, can quickly become a tangled mess. While ASP.NET Core's output caching is a powerful tool, its true value hinges on effective invalidation. This article demonstrates how to implement output caching with a tag-based invalidation strategy in ASP.NET Core 7+, enabling you to invalidate specific cached items based on logical tags, ensuring faster and more accurate data retrieval.

To begin, ensure you have the necessary NuGet packages installed: `Microsoft.AspNetCore.OutputCaching.StackExchangeRedis` for Redis-backed caching and `Microsoft.AspNetCore.OutputCaching`. Configure the output caching middleware and a distributed cache provider in your `Program.cs`. For Redis, this typically involves adding services like:

```csharp
builder.Services.AddStackExchangeRedisOutputCache(options =>
{
    options.InstanceName = "MyProjectCache";
    options.Configuration = builder.Configuration.GetConnectionString("RedisConnection");
});
builder.Services.AddOutputCache();
```

Next, apply the `[OutputCache]` attribute to your controller actions. The key to tag-based invalidation lies in the `VaryByTag` parameter, which allows you to associate cached responses with logical tags. For instance, if your action retrieves product data, you can tag it with `"products"`. When a product is updated, you can then selectively invalidate all cached entries tagged with `"products"` without impacting unrelated cached data. This granular control is crucial for maintaining data freshness without unnecessary cache purges.

```csharp
[ApiController]
[Route("[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IOutputCacheStore _cacheStore;

    public ProductsController(IOutputCacheStore cacheStore)
    {
        _cacheStore = cacheStore;
    }

    [HttpGet("{id}")]
    [OutputCache(Duration = 60, VaryByTag = "products")] // Cache for 60 seconds, tagged 'products'
    public async Task<IActionResult> GetProduct(int id)
    {
        // Simulate fetching product from a database or other source
        var product = await FetchProductFromDatabaseAsync(id);
        return Ok(product);
    }

    [HttpPost]
    public async Task<IActionResult> UpdateProduct([FromBody] Product product)
    {
        // Simulate updating product in a database
        await UpdateProductInDatabaseAsync(product);

        // Invalidate cache entries tagged 'products'
        await _cacheStore.EvictAsync("products");

        return Ok();
    }

    // Placeholder for actual data fetching
    private async Task<Product> FetchProductFromDatabaseAsync(int id) => await Task.FromResult(new Product { Id = id, Name = $"Product {id}" });
    private async Task UpdateProductInDatabaseAsync(Product product) => await Task.Delay(100); // Simulate database operation
}

public class Product { public int Id { get; set; } public string Name { get; set; } }
```

A significant gotcha with tag-based invalidation, especially in distributed systems, is ensuring consistency. If your invalidation logic is complex or distributed across multiple services, you may encounter race conditions. This can occur if a cache entry is updated after being invalidated but before the invalidation is fully propagated across all cache instances. For robust solutions in such scenarios, consider integrating a reliable message queue to signal cache invalidation events, ensuring a more consistent approach to data freshness.

Test this by adding the `[OutputCache(Duration = 30, VaryByTag = "items")]` attribute to a controller action and verifying that repeated requests within 30 seconds return cached results. Subsequently, create another endpoint to call `_cacheStore.EvictAsync("items")` and confirm that subsequent requests retrieve fresh data, demonstrating the power of targeted cache invalidation.
