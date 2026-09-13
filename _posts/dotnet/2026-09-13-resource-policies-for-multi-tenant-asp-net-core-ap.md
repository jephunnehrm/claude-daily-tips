---
layout: post
title: "Resource Policies for Multi-Tenant ASP.NET Core APIs"
date: 2026-09-13
type: how-to
summary: "Leverage Claude Code to define and enforce granular, resource-based authorization policies in your multi-tenant SaaS APIs."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-13-resource-policies-for-multi-tenant-asp-net-core-ap.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Resource Policies for Multi-Tenant ASP.NET Core APIs](/claude-daily-tips/assets/images/dotnet-2026-09-13-resource-policies-for-multi-tenant-asp-net-core-ap.jpg)



When building multi-tenant SaaS applications with ASP.NET Core, efficiently managing authorization across tenants and their associated resources presents a significant challenge. Developers often find themselves writing repetitive and complex authorization logic directly within controllers, leading to maintainability issues and potential security vulnerabilities. This manual approach becomes unwieldy as applications scale, often resulting in either overly permissive access or intricate, error-prone checks.

A more robust and scalable solution lies in adopting resource-based authorization. Instead of solely focusing on the user's identity, resource-based policies consider the relationship between the user and the specific resource they are attempting to access. For multi-tenant applications, this means ensuring a user from tenant A can only interact with resources belonging to tenant A. ASP.NET Core's authorization system, particularly with custom `IAuthorizationHandler` implementations, provides the framework to achieve this. By defining policies that encapsulate these resource-specific rules, you centralize authorization logic, making it cleaner and easier to manage.

Consider a scenario with `Product` resources, each assigned to a specific `TenantId`. To enforce that only users within the product's tenant can edit or delete it, we can create a custom authorization policy. This policy would leverage an `IAuthorizationHandler` that inspects the `Product` resource and compares its `TenantId` with the authenticated user's `TenantId`, typically retrieved from claims. This handler can be configured to work seamlessly with the `[Authorize]` attribute in your API controllers.

Here's how this might look in practice:

```csharp
// Program.cs or Startup.cs
services.AddAuthorization(options =>
{
    options.AddPolicy("CanEditProduct", policy =>
        policy.Requirements.Add(new ProductOwnershipRequirement()));
});

// Register the handler. Depending on your setup, this might be scoped or transient.
services.AddScoped<IAuthorizationHandler, ProductOwnershipHandler>();

// ProductOwnershipRequirement.cs
// A simple marker requirement
public class ProductOwnershipRequirement : IAuthorizationRequirement { }

// ProductOwnershipHandler.cs
public class ProductOwnershipHandler : AuthorizationHandler<ProductOwnershipRequirement>
{
    private readonly IProductService _productService; // Service to fetch the product
    private readonly ITenantAccessor _tenantAccessor; // Service to get current tenant ID

    // Inject necessary services
    public ProductOwnershipHandler(IProductService productService, ITenantAccessor tenantAccessor)
    {
        _productService = productService;
        _tenantAccessor = tenantAccessor;
    }

    protected override async Task HandleRequirementAsync(AuthorizationHandlerContext context, ProductOwnershipRequirement requirement)
    {
        if (!context.User.Identity.IsAuthenticated)
        {
            context.Fail();
            return;
        }

        // This is a common scenario: authorization is requested for an action,
        // and the resource isn't directly passed, but we might have an ID in the route.
        // We'll look for an `productId` in the route values.
        if (context.Resource is Microsoft.AspNetCore.Mvc.Controllers.ControllerActionDescriptor controllerActionDescriptor)
        {
            var productId = controllerActionDescriptor.RouteValues.TryGetValue("productId", out var id) ? int.Parse(id.ToString()) : (int?)null;

            if (productId.HasValue)
            {
                var product = await _productService.GetProductByIdAsync(productId.Value);
                if (product != null)
                {
                    var currentUserTenantId = _tenantAccessor.GetTenantId(); // Assumes this method exists
                    if (product.TenantId == currentUserTenantId)
                    {
                        context.Succeed(requirement);
                        return;
                    }
                }
            }
        }
        // Alternative: If the resource IS passed directly (e.g., from a previous authorization filter)
        else if (context.Resource is Product product)
        {
            var currentUserTenantId = _tenantAccessor.GetTenantId();
            if (product.TenantId == currentUserTenantId)
            {
                context.Succeed(requirement);
                return;
            }
        }

        context.Fail();
    }
}

// Example Controller Usage
[ApiController]
[Route("api/[controller]")]
[Authorize] // General authentication required
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;

    public ProductsController(IProductService productService)
    {
        _productService = productService;
    }

    [HttpDelete("{productId}")]
    [Authorize(Policy = "CanEditProduct")] // Specific policy for editing products
    public async Task<IActionResult> DeleteProduct(int productId)
    {
        // Authorization is handled by the [Authorize] attribute and the handler.
        // The handler will fetch the product by productId and check tenant ownership.
        await _productService.DeleteProductAsync(productId);
        return NoContent();
    }
}

// Dummy interfaces/classes for compilation
public interface IProductService { Task<Product> GetProductByIdAsync(int id); Task DeleteProductAsync(int id); }
public interface ITenantAccessor { string GetTenantId(); }
public class Product { public int Id { get; set; } public string Name { get; set; } public string TenantId { get; set; } }
```

A critical consideration is that `context.Resource` in an `AuthorizationHandler` might not always be the domain model directly. Often, especially when authorization is triggered by a route parameter like `productId`, you'll need to inject services into your handler (e.g., an `IProductService`) to fetch the actual resource based on its ID. This allows the handler to perform the necessary ownership or policy checks. This approach provides a robust, centralized, and testable authorization mechanism that scales with your multi-tenant application, offering significant advantages over ad-hoc controller-level checks.
