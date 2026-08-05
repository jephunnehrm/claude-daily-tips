---
layout: post
title: "Enhance JWT with Custom Database Claims in ASP.NET Core"
date: 2026-08-05
type: how-to
summary: "Add dynamic user data from your database to JWTs with a custom claims transformation."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-05-enhance-jwt-with-custom-database-claims-in-asp-net.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
---



![Enhance JWT with Custom Database Claims in ASP.NET Core](/claude-daily-tips/assets/images/dotnet-2026-08-05-enhance-jwt-with-custom-database-claims-in-asp-net.jpg)



When building secure ASP.NET Core applications, you'll frequently find that the default JWT identity claims, like username and ID, aren't enough. You often need to embed richer, dynamically managed user attributes—think roles, granular permissions, or subscription tiers—that reside in your application's database. Repeatedly fetching this data after authentication, perhaps on every API request, quickly becomes a performance bottleneck and a code smell. ASP.NET Core offers a clean, centralized solution: custom claims transformation.

The `IClaimsTransformation` interface within ASP.NET Core's authentication middleware is designed precisely for this. By implementing this interface and registering your custom transformation in the service collection, you can hook into the authentication pipeline. The `TransformAsync` method of your implementation receives the `ClaimsPrincipal` as it's being built by the authentication handlers. Inside this method, you can asynchronously query your database, retrieve the necessary user profile data, and then judiciously add new `Claim` objects to the `ClaimsIdentity`. These newly added claims are then serialized into the JWT, making them readily available throughout your application without further database roundtrips for each access.

Consider this example utilizing a hypothetical `UserProfileService` to enrich the principal:

```csharp
using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;

public class DatabaseClaimsTransformation : IClaimsTransformation
{
    private readonly IUserProfileService _userProfileService;

    public DatabaseClaimsTransformation(IUserProfileService userProfileService)
    {
        _userProfileService = userProfileService;
    }

    public async Task<ClaimsPrincipal> TransformAsync(ClaimsPrincipal principal)
    {
        // Ensure the principal is authenticated and has an identity.
        if (principal.Identity is ClaimsIdentity identity && identity.IsAuthenticated)
        {
            // Retrieve the user's unique identifier. This often comes from ClaimTypes.NameIdentifier
            // or a custom claim if your authentication provider sets it differently.
            var userIdClaim = principal.FindFirst(ClaimTypes.NameIdentifier);

            if (userIdClaim != null && Guid.TryParse(userIdClaim.Value, out Guid userId))
            {
                // Fetch additional user data from the database.
                var userProfile = await _userProfileService.GetUserProfileAsync(userId);

                if (userProfile != null)
                {
                    // Add custom claims based on fetched user data.
                    identity.AddClaim(new Claim("user_role", userProfile.Role ?? "Guest"));
                    identity.AddClaim(new Claim("subscription_tier", userProfile.SubscriptionLevel ?? "Basic"));
                    // Add other relevant claims as needed.
                }
            }
        }
        return principal;
    }
}

// Placeholder for your actual database service and UserProfile model.
public interface IUserProfileService
{
    Task<UserProfile?> GetUserProfileAsync(Guid userId);
}

public class UserProfile
{
    public Guid Id { get; set; }
    public string? Role { get; set; }
    public string? SubscriptionLevel { get; set; }
}
```

To integrate this, register your service and the transformation in your application's service collection:

```csharp
// In Program.cs or Startup.cs's ConfigureServices method
builder.Services.AddScoped<IUserProfileService, YourActualUserProfileService>(); // Replace with your database implementation
builder.Services.AddSingleton<IClaimsTransformation, DatabaseClaimsTransformation>();
```

A critical consideration is performance. Executing complex or slow database queries within `TransformAsync` can introduce latency to every authentication event. Optimize your data retrieval—ensure efficient indexing and consider leveraging caching mechanisms for frequently accessed, less volatile data. Furthermore, exercise caution regarding the *type* of data you embed. For highly sensitive information, it's often safer to include only a reference (like a user ID) and fetch the details on demand via a secure API endpoint, rather than exposing it directly in the JWT.
