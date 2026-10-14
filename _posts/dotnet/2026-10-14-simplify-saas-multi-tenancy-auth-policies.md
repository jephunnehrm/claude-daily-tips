---
layout: post
title: "Simplify SaaS Multi-Tenancy Auth Policies"
date: 2026-10-14
type: how-to
summary: "Leverage Claude Code to quickly define resource-based authorization policies for multi-tenant ASP.NET Core APIs."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-14-simplify-saas-multi-tenancy-auth-policies.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - azure
---



![Simplify SaaS Multi-Tenancy Auth Policies](/claude-daily-tips/assets/images/dotnet-2026-10-14-simplify-saas-multi-tenancy-auth-policies.jpg)



Building robust multi-tenant SaaS applications in .NET often leads to complex authorization logic. A common pain point for developers is ensuring that users within a specific tenant can only access *their own* data and resources, a challenge that quickly escalates with custom policies for various resources and operations. Manually crafting these fine-grained, resource-based authorization rules can be tedious, error-prone, and difficult to maintain as your application scales.

Leveraging ASP.NET Core's authorization system, particularly with custom `IAuthorizationPolicyProvider` implementations, offers a more dynamic and maintainable approach. The goal is to define policies that are evaluated at runtime, taking into account the current tenant's context and the ownership of the resource being accessed. This allows you to abstract away much of the boilerplate logic and focus on the declarative definition of authorization rules.

Consider a scenario where you need to enforce that a user can only operate on a resource if their tenant owns it. You can create a custom authorization requirement, such as `TenantResourceRequirement`, and an associated handler, `TenantResourceHandler`, to perform this check.

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.Abstractions;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Extensions.DependencyInjection;
using System.Security.Claims;

public class TenantResourcePolicyProvider : IAuthorizationPolicyProvider
{
    private readonly DefaultAuthorizationPolicyProvider _fallbackPolicyProvider;

    public TenantResourcePolicyProvider(IOptions<AuthorizationOptions> options)
    {
        _fallbackPolicyProvider = new DefaultAuthorizationPolicyProvider(options);
    }

    public Task<AuthorizationPolicy> GetPolicyAsync(string policyName)
    {
        if (policyName.StartsWith("TenantResourceOwner"))
        {
            // Policy name example: "TenantResourceOwner:ProductId"
            // The part after the colon could represent the resource type or identifier.
            // This example focuses on a general tenant ownership check.
            var policy = new AuthorizationPolicyBuilder()
                .AddRequirements(new TenantResourceRequirement())
                .Build();
            return Task.FromResult(policy);
        }

        return _fallbackPolicyProvider.GetPolicyAsync(policyName);
    }

    public Task<AuthorizationPolicy> GetDefaultPolicyAsync() =>
        _fallbackPolicyProvider.GetDefaultPolicyAsync();
}

public class TenantResourceRequirement : IAuthorizationRequirement { }

public class TenantResourceHandler : AuthorizationHandler<TenantResourceRequirement>
{
    protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, TenantResourceRequirement requirement)
    {
        // 1. Get TenantId from user claims.
        var tenantId = context.User.FindFirstValue("tenant_id"); // Assumes 'tenant_id' claim exists.

        if (string.IsNullOrEmpty(tenantId))
        {
            return; // User is not authenticated or tenant claim is missing.
        }

        // 2. Get ResourceId from the request context.
        // This is the critical part where you need to access the request.
        // The 'context.Resource' might be an 'Endpoint' or an 'ActionContext'.
        // Extracting the ID depends on how your API is structured (e.g., route parameters, query string).
        // For example, if using route parameters like '/products/{productId}':
        var routeData = (context.Resource as DefaultHttpContext)?.GetRouteData(); // If using DefaultHttpContext directly
        string resourceId = null;
        if (routeData?.Values.TryGetValue("productId", out var productIdValue)) // Replace "productId" with your parameter name
        {
            resourceId = productIdValue?.ToString();
        }
        // Add logic here to extract resourceId from other sources if needed (e.g., query string, body).

        if (string.IsNullOrEmpty(resourceId))
        {
            return; // Resource ID not found in context.
        }

        // 3. Query your data store to verify ownership.
        // This requires injecting a service that can access your database.
        // Example:
        // var resourceOwnershipService = context.GetService<IResourceOwnershipService>();
        // var isOwned = await resourceOwnershipService.CheckTenantOwnershipAsync(tenantId, resourceId);
        // if (isOwned)
        // {
        //     context.Succeed(requirement);
        // }

        // Placeholder for demonstration: Assuming ownership is proven.
        // In a real app, this would be a database lookup.
        context.Succeed(requirement);
    }
}
```

A key challenge is reliably extracting the `ResourceId` from the ASP.NET Core request context. Unlike `TenantId`, which is typically found in user claims, `ResourceId` often resides in route parameters, query strings, or request bodies. This necessitates careful integration with `IHttpContextAccessor` or passing request context information through MVC/API controllers to the authorization handler, which can be a subtle but crucial detail for successful implementation. This approach empowers developers to define explicit, tenant-aware authorization policies that significantly reduce the complexity and potential for errors in multi-tenant applications.
