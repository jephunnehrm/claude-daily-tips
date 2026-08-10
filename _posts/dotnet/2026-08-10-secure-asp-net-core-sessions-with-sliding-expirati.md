---
layout: post
title: "Secure ASP.NET Core Sessions with Sliding Expiration & Tokens"
date: 2026-08-10
type: how-to
summary: "Configure ASP.NET Core to use sliding session expiration and anti-forgery tokens with Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-10-secure-asp-net-core-sessions-with-sliding-expirati.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
---



![Secure ASP.NET Core Sessions with Sliding Expiration & Tokens](/claude-daily-tips/assets/images/dotnet-2026-08-10-secure-asp-net-core-sessions-with-sliding-expirati.jpg)



Securing user sessions in ASP.NET Core while balancing user experience and security is a common challenge. Developers often struggle to ensure sessions remain active only during genuine user interaction, preventing indefinite persistence, while simultaneously defending against Cross-Site Request Forgery (CSRF). Manually implementing and verifying both sliding expiration logic and robust anti-forgery token validation across an application can be error-prone and time-consuming.

ASP.NET Core provides built-in middleware to handle session state and CSRF protection effectively. By configuring session options with a sliding expiration and integrating the anti-forgery system, you can automatically extend a user's session as long as they are actively engaging with the application and ensure that incoming requests are legitimate. This approach leverages the framework's capabilities to simplify security management.

The core of this solution lies in two primary configuration areas: `AddSession` and `AddAntiforgery`. For `AddSession`, setting `IdleTimeout` defines the server-side session duration after inactivity. Crucially, the session middleware itself will reset the session cookie on each valid request, effectively creating a sliding window. For enhanced security, configure the cookie with `HttpOnly = true`, `SecurePolicy = CookieSecurePolicy.Always` (for HTTPS), and `SameSite = SameSiteMode.Lax` to mitigate CSRF risks. For anti-forgery, `AddAntiforgery` sets up the necessary services, and applying `[ValidateAntiForgeryToken]` attributes to action methods or globally via `options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute())` ensures that all state-changing requests are validated.

```csharp
// In Program.cs (for .NET 6+)
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddSession(options =>
{
    // Session data persists for 30 minutes after the last activity.
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.IsEssential = true;
    options.Cookie.HttpOnly = true;
    // Ensures the cookie is only sent over HTTPS.
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    // Mitigates CSRF by restricting cookie sending for cross-site requests.
    options.Cookie.SameSite = SameSiteMode.Lax;
    options.Cookie.Name = ".AspNetCore.Session.Sliding";
    // While MaxAge can be set, the session middleware's activity-based
    // cookie renewal effectively provides the sliding expiration.
    // Setting it to a value close to IdleTimeout is common for clarity.
    options.Cookie.MaxAge = TimeSpan.FromMinutes(30);
});

// Configures the services for anti-forgery token generation and validation.
builder.Services.AddAntiforgery(options =>
{
    options.HeaderName = "X-CSRF-TOKEN"; // The header where the token will be sent.
});

builder.Services.AddControllersWithViews(options =>
{
    // Automatically validates anti-forgery tokens for all non-GET requests.
    options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute());
});

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

// Essential: Ensure session middleware runs before authorization
// if your authorization logic depends on session state.
app.UseSession();

// If using Identity, authentication and authorization typically follow.
// app.UseAuthentication();
// app.UseAuthorization();

app.MapRazorPages();
app.MapControllers();

app.Run();
```

A key point of confusion can arise between the session's `IdleTimeout` and the cookie's `MaxAge`. The `IdleTimeout` governs server-side session data persistence, while the session middleware's operation is what truly provides the sliding effect by sending a refreshed cookie with each valid request. This means the browser will receive a new cookie expiration date as long as the user remains active. It's also critical to call `app.UseSession()` *before* `app.UseAuthorization()` if your authorization checks rely on session data.
