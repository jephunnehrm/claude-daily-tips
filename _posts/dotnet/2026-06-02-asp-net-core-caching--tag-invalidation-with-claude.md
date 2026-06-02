---
layout: post
title: "ASP.NET Core Caching: Tag Invalidation with Claude Code"
date: 2026-06-02
type: how-to
summary: "Efficiently manage ASP.NET Core output cache invalidation using Claude Code and tag-based strategies."
image: "/claude-daily-tips/assets/images/dotnet-2026-06-02-asp-net-core-caching--tag-invalidation-with-claude.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![ASP.NET Core Caching: Tag Invalidation with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-06-02-asp-net-core-caching--tag-invalidation-with-claude.jpg)



As an ASP.NET Core developer, you're likely familiar with the challenge of keeping cached data fresh. Manually clearing caches after every data modification can lead to stale content or unnecessary application load. While ASP.NET Core's built-in output caching is powerful, its lifecycle management, especially with complex dependencies, demands a strategic approach. Tag-based invalidation offers a flexible and scalable solution by enabling you to group related cache entries and invalidate them collectively, dramatically simplifying cache management.

Leveraging AI tools like Claude Code can significantly streamline the implementation of tag-based output caching. Instead of manually crafting cache keys and invalidation logic for each affected item, Claude Code can generate boilerplate code and suggest optimal patterns. The `claude` CLI, for instance, can analyze your existing caching setup and propose code modifications to integrate tag support. You can prompt Claude Code to add tag generation logic to your data repository methods and then utilize those tags when configuring your output cache profiles.

Consider this foundational example for setting up tag-based output caching. Imagine you're using `Microsoft.Extensions.Caching.Distributed.IDistributedCache` and want to apply tags. While the direct `IDistributedCache` interface doesn't natively expose tag-based invalidation, you can implement a custom `IOutputCacheStore` or middleware that adds tag management. Claude Code can assist in generating the necessary code structure for this. For example, it can help generate methods to associate tags with cache keys, perhaps by storing them as part of the cache entry's metadata or in a separate tag-lookup structure.

```csharp
// Example of how to add tags and invalidate using a custom IOutputCacheStore.
// This demonstrates a pattern that Claude Code can help generate.

using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Distributed; // For IDistributedCache
using System.Text.Json;
using System.Text;

// A hypothetical custom store that adds tag support over IDistributedCache
public class TaggingDistributedCacheOutputCache : IDistributedCache
{
    private readonly IDistributedCache _innerCache;
    private const string TagPrefix = "__tag:";
    private const string EntryTagSeparator = ";"; // To store multiple tags

    public TaggingDistributedCacheOutputCache(IDistributedCache innerCache)
    {
        _innerCache = innerCache;
    }

    public byte[] Get(string key)
    {
        return _innerCache.Get(key);
    }

    public async Task<byte[]> GetAsync(string key, CancellationToken token = default)
    {
        return await _innerCache.GetAsync(key, token);
    }

    public void Refresh(string key)
    {
        _innerCache.Refresh(key);
    }

    public async Task RefreshAsync(string key, CancellationToken token = default)
    {
        await _innerCache.RefreshAsync(key, token);
    }

    public void Remove(string key)
    {
        // Invalidate associated tags before removing the entry
        var tagsEntry = _innerCache.GetString($"{key}_tags");
        if (!string.IsNullOrEmpty(tagsEntry))
        {
            var tags = tagsEntry.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries);
            foreach (var tag in tags)
            {
                InvalidateTag(tag);
            }
            _innerCache.Remove($"{key}_tags");
        }

        _innerCache.Remove(key);
    }

    public async Task RemoveAsync(string key, CancellationToken token = default)
    {
        var tagsEntry = await _innerCache.GetStringAsync($"{key}_tags", token);
        if (!string.IsNullOrEmpty(tagsEntry))
        {
            var tags = tagsEntry.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries);
            foreach (var tag in tags)
            {
                InvalidateTag(tag);
            }
            await _innerCache.RemoveAsync($"{key}_tags", token);
        }

        await _innerCache.RemoveAsync(key, token);
    }

    public void Set(string key, byte[] value, DistributedCacheEntryOptions options)
    {
        // When setting, we also need to associate tags.
        // This would typically be passed via options or context.
        // For simplicity, let's assume tags are derived from key for this example.
        // In a real scenario, tags would be passed explicitly.

        var tags = new List<string>();
        if (key.StartsWith("products_"))
        {
            tags.Add("all_products");
            if (int.TryParse(key.Substring("products_".Length), out var productId))
            {
                tags.Add($"product_{productId}");
            }
        }

        SetTags(key, tags.ToArray());
        _innerCache.Set(key, value, options);
    }

    public async Task SetAsync(string key, byte[] value, DistributedCacheEntryOptions options, CancellationToken token = default)
    {
        var tags = new List<string>();
        if (key.StartsWith("products_"))
        {
            tags.Add("all_products");
            if (int.TryParse(key.Substring("products_".Length), out var productId))
            {
                tags.Add($"product_{productId}");
            }
        }

        await SetTagsAsync(key, tags.ToArray(), token);
        await _innerCache.SetAsync(key, value, options, token);
    }

    // Custom methods for tag management
    public void SetTags(string key, params string[] tags)
    {
        var tagKeys = tags.Select(t => TagPrefix + t).ToArray();
        foreach (var tagKey in tagKeys)
        {
            var taggedKeysEntry = _innerCache.GetString(tagKey);
            var taggedKeys = taggedKeysEntry?.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries).ToList() ?? new List<string>();
            if (!taggedKeys.Contains(key))
            {
                taggedKeys.Add(key);
                _innerCache.SetString(tagKey, string.Join(EntryTagSeparator, taggedKeys), new DistributedCacheEntryOptions { SlidingExpiration = TimeSpan.FromDays(7) }); // Example expiration
            }
        }

        // Store the tags associated with this specific cache entry
        var currentTagsEntry = _innerCache.GetString($"{key}_tags");
        var currentTags = currentTagsEntry?.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries).ToList() ?? new List<string>();
        foreach(var tag in tags)
        {
            if(!currentTags.Contains(tag))
            {
                currentTags.Add(tag);
            }
        }
        _innerCache.SetString($"{key}_tags", string.Join(EntryTagSeparator, currentTags), new DistributedCacheEntryOptions { SlidingExpiration = TimeSpan.FromDays(7) });
    }

    public async Task SetTagsAsync(string key, params string[] tags, CancellationToken token = default)
    {
        var tagKeys = tags.Select(t => TagPrefix + t).ToArray();
        foreach (var tagKey in tagKeys)
        {
            var taggedKeysEntry = await _innerCache.GetStringAsync(tagKey, token);
            var taggedKeys = taggedKeysEntry?.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries).ToList() ?? new List<string>();
            if (!taggedKeys.Contains(key))
            {
                taggedKeys.Add(key);
                await _innerCache.SetStringAsync(tagKey, string.Join(EntryTagSeparator, taggedKeys), new DistributedCacheEntryOptions { SlidingExpiration = TimeSpan.FromDays(7) }, token);
            }
        }

        var currentTagsEntry = await _innerCache.GetStringAsync($"{key}_tags", token);
        var currentTags = currentTagsEntry?.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries).ToList() ?? new List<string>();
        foreach(var tag in tags)
        {
            if(!currentTags.Contains(tag))
            {
                currentTags.Add(tag);
            }
        }
        await _innerCache.SetStringAsync($"{key}_tags", string.Join(EntryTagSeparator, currentTags), new DistributedCacheEntryOptions { SlidingExpiration = TimeSpan.FromDays(7) }, token);
    }

    public void InvalidateTag(string tag)
    {
        var tagKey = TagPrefix + tag;
        var taggedKeysEntry = _innerCache.GetString(tagKey);
        if (!string.IsNullOrEmpty(taggedKeysEntry))
        {
            var keysToRemove = taggedKeysEntry.Split(EntryTagSeparator, StringSplitOptions.RemoveEmptyEntries);
            foreach (var key in keysToRemove)
            {
                _innerCache.Remove(key); // This also removes the associated _tags entry
            }
            _innerCache.Remove(tagKey); // Remove the tag lookup entry
        }
    }

    // Note: In a real app, you might need a separate InvalidateTagAsync.
    // For simplicity, we are reusing the sync version here.
    public void InvalidateByTag(string tag)
    {
        InvalidateTag(tag);
    }
}

[ApiController]
[Route("api/[controller]")]
public class ProductController : Controller
{
    private readonly IDistributedCache _cache; // Injected to demonstrate the underlying cache

    public ProductController(IDistributedCache cache)
    {
        _cache = cache;
    }

    [HttpGet("{id}")]
    // You would configure your custom cache store in DI and use it here.
    // For this example, we'll assume it's registered and used.
    [OutputCache(Duration = 60, VaryByQueryKeys = new[] { "*" })]
    public async Task<IActionResult> GetProduct(int id)
    {
        var cacheKey = $"products_{id}";
        var cachedProduct = await _cache.GetStringAsync(cacheKey);

        if (cachedProduct != null)
        {
            return Ok(JsonSerializer.Deserialize<Product>(cachedProduct));
        }

        // Simulate fetching from a database
        await Task.Delay(100); // Simulate latency
        var product = new Product { Id = id, Name = $"Sample Product {id}" };

        // Using the custom store's tag functionality (conceptually)
        // This would be handled by the custom IOutputCacheStore implementation
        // when it wraps the IDistributedCache.
        // The OutputCache attribute itself would interact with the configured IOutputCacheStore.
        // For demonstration, we simulate setting tags here via the custom store's methods.
        if (_cache is TaggingDistributedCacheOutputCache taggingCache)
        {
             await taggingCache.SetTagsAsync(cacheKey, $"product_{id}", "all_products");
        }
        else
        {
            // Fallback or error if not using the custom store.
            // In a real scenario, DI ensures the correct store is used.
        }

        await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(product), new DistributedCacheEntryOptions { SlidingExpiration = TimeSpan.FromMinutes(5) });

        return Ok(product);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> InvalidateProduct(int id)
    {
        var cacheKey = $"products_{id}";
        var tagToInvalidate = $"product_{id}";
        var generalTag = "all_products";

        // Invalidate specific product cache and general product list cache.
        // Again, assuming interaction with a custom store.
        if (_cache is TaggingDistributedCacheOutputCache taggingCache)
        {
            taggingCache.InvalidateByTag(tagToInvalidate);
            taggingCache.InvalidateByTag(generalTag);
            // It's also good practice to remove the specific entry if it still exists for any reason
            await _cache.RemoveAsync(cacheKey);
        }
        else
        {
            // Fallback or error
            await _cache.RemoveAsync(cacheKey); // Simple removal without tags
        }


        return Ok($"Cache for product {id} and general product tags invalidated.");
    }
}

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
}
```

A crucial "gotcha" is that the default `Microsoft.Extensions.Caching.Output.DistributedCacheOutputCache` doesn't inherently support tag-based invalidation. To achieve this, you'll need to implement a custom `IOutputCacheStore` or middleware that wraps a distributed cache like Redis. This custom implementation must handle the logic of associating tags with cache keys and providing methods to query and invalidate entries based on those tags. Claude Code can be instrumental in generating the structure for such custom solutions, saving you considerable development time. The provided example illustrates a pattern for this custom implementation.

This approach works by decoupling cache invalidation from specific data items. Instead of thinking "when product X changes, invalidate cache for product X," you think "when product X changes, invalidate all items tagged 'product_X' and 'all_products'." This makes your caching strategy more robust and easier to manage, especially as your application scales. Claude Code can help you move beyond basic caching to implement more sophisticated strategies like this, providing concrete code generation for custom extensions that aren't directly available in the standard library, offering value beyond simply reading documentation.
