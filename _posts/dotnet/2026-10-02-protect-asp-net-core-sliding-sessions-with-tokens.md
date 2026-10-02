---
layout: post
title: "Protect ASP.NET Core Sliding Sessions with Tokens"
date: 2026-10-02
type: how-to
summary: "Integrate anti-forgery tokens to secure sliding session cookies in ASP.NET Core applications."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Protect ASP.NET Core Sliding Sessions with Tokens](assets/images/placeholder.jpg)



Managing long-lived user sessions in ASP.NET Core applications while simultaneously guarding against Cross-Site Request Forgery (CSRF) attacks is a common challenge. Sliding expiration for session cookies, where the cookie's validity extends with each authenticated request, offers convenience but amplifies the need for robust CSRF protection, especially for sensitive operations. ASP.NET Core provides built-in, easily configurable mechanisms to address this intersection of security requirements.

The foundation of this protection involves registering both cookie authentication and anti-forgery token services in your `Program.cs` file. For sliding sessions, configure cookie authentication options by setting `SlidingExpiration` to `true` and defining an appropriate `ExpireTimeSpan`. Concurrently, enable anti-forgery token generation and validation, typically achieved by calling `app.UseAntiforgery()`. This ensures that for every subsequent request after the initial authentication, both the cookie and the anti-forgery token must be present and valid.

Here's a typical configuration snippet demonstrating these settings:

```csharp
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.SlidingExpiration = true;
        options.ExpireTimeSpan = TimeSpan.FromMinutes(30); // Example: session lasts up to 30 minutes of inactivity
        options.Cookie.Name = "YourAppCookie";
        options.Events.OnRedirectToLogin = context =>
        {
            // Crucial for APIs: prevent redirects and return 401 for unauthorized AJAX/API requests
            if (context.Request.Path.StartsWithSegments("/api") || context.Request.Headers["X-Requested-With"] == "XMLHttpRequest")
            {
                context.Response.StatusCode = 401;
                return Task.CompletedTask;
            }
            context.Response.Redirect(context.RedirectUri);
            return Task.CompletedTask;
        };
    });

builder.Services.AddAntiforgery(options =>
{
    options.HeaderName = "X-CSRF-TOKEN"; // A common, but configurable, header name for tokens
});

var app = builder.Build();

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.UseAntiforgery(); // This middleware is critical for validating the tokens on incoming requests
```

A significant consideration for developers is how client-side applications interact with these tokens. For traditional server-rendered applications using Razor Pages or MVC, ASP.NET Core's tag helpers can automatically embed the necessary hidden input field for the anti-forgery token within forms. However, in Single Page Applications (SPAs) or when building API endpoints, your JavaScript code must explicitly retrieve the token—often stored in a cookie set by the server or fetched from a dedicated endpoint—and include it in the `X-CSRF-TOKEN` header (or your configured header) for all state-changing requests. Failing to handle the `OnRedirectToLogin` event for AJAX requests is a common pitfall, leading to unexpected HTTP 302 redirects instead of appropriate 401 Unauthorized responses for API calls.
