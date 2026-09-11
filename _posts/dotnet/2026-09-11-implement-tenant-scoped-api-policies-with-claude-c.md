---
layout: post
title: "Implement Tenant-Scoped API Policies with Claude Code"
date: 2026-09-11
type: how-to
summary: "Leverage Claude Code to rapidly define and implement resource-based authorization policies for multi-tenant SaaS APIs."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-11-implement-tenant-scoped-api-policies-with-claude-c.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - mcp
---



![Implement Tenant-Scoped API Policies with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-09-11-implement-tenant-scoped-api-policies-with-claude-c.jpg)



When building a multi-tenant SaaS API in ASP.NET Core, a common challenge is ensuring that users can only access resources belonging to their specific tenant. This requires a robust authorization strategy that goes beyond simple role-based access and delves into resource ownership. Manually crafting these policies for every resource and tenant can be tedious and error-prone, especially as your API evolves. Claude Code can significantly accelerate this process by generating the necessary authorization logic based on your API structure and tenant context.

Let's consider an example where you have a `TenantService` that resolves the current tenant ID and a `ResourceService` that manages resources, each associated with a tenant. You want to ensure that an `OrderController` can only access orders belonging to the authenticated user's tenant. Claude Code can help you define a dynamic, resource-based policy that checks this tenant association. You'd typically start by instructing Claude Code to understand your existing `TenantService` and `Order` models, and then ask it to generate an `OrderAuthorizationHandler` that checks tenant ownership.

Here's a conceptual example of how Claude Code might assist. Imagine you have an `Order` model like this:

```csharp
public class Order
{
    public int Id { get; set; }
    public string TenantId { get; set; } // Assuming TenantId is a string
    public DateTime OrderDate { get; set; }
    // Other properties...
}
```

You would then prompt Claude Code to create an `AuthorizationHandler` that checks if the `Order.TenantId` matches the current user's tenant. A typical prompt might look like: "Generate an ASP.NET Core `AuthorizationHandler` for the 'TenantOrderOwner' policy. This handler should check if the `Order` resource's `TenantId` property matches the `TenantId` associated with the current authenticated user. Assume a `ITenantResolver` service is available to get the current tenant ID and the resource is passed as a requirement."

Claude Code could then produce something similar to the following C# code, which you'd integrate into your application:

```csharp
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;

public class TenantOrderOwnerRequirement : IAuthorizationRequirement { }

public class TenantOrderOwnerHandler : AuthorizationHandler<TenantOrderOwnerRequirement, Order>
{
    private readonly ITenantResolver _tenantResolver; // Assume this is registered in DI

    public TenantOrderOwnerHandler(ITenantResolver tenantResolver)
    {
        _tenantResolver = tenantResolver;
    }

    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, TenantOrderOwnerRequirement requirement, Order resource)
    {
        var currentTenantId = _tenantResolver.GetTenantId(); // Or get from context.User.FindFirst(ClaimTypes.TenantId)?.Value

        if (resource != null && !string.IsNullOrEmpty(currentTenantId) && resource.TenantId == currentTenantId)
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}

// In Startup.cs or Program.cs:
// services.AddSingleton<ITenantResolver, YourTenantResolverImplementation>();
// services.AddSingleton<IAuthorizationHandler, TenantOrderOwnerHandler>();
// services.AddAuthorization(options =>
// {
//     options.AddPolicy("TenantOrderOwner", policy => policy.AddRequirements(new TenantOrderOwnerRequirement()));
// });
```

A significant gotcha to be aware of is how the `Order` resource is passed to the `AuthorizationHandler`. In the example above, we assume the `Order` object is directly available. For GET requests that fetch a single order by ID, you might need a custom `IAuthorizationService` or a slightly different approach in your `AuthorizationHandler` to first fetch the `Order` based on the ID from the route and *then* perform the tenant check. Claude Code can help refactor these fetching mechanisms if prompted.

**Try it:** Prompt Claude Code to generate an `AuthorizationHandler` for a `Product` resource that checks if the `Product.OwnerTenantId` matches the current tenant.
