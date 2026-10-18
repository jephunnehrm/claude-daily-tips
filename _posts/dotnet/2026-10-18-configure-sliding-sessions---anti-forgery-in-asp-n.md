---
layout: post
title: "Configure Sliding Sessions & Anti-Forgery in ASP.NET Core"
date: 2026-10-18
type: how-to
summary: "Secure your ASP.NET Core app with configurable sliding sessions and robust anti-forgery token validation using Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-18-configure-sliding-sessions---anti-forgery-in-asp-n.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
---



![Configure Sliding Sessions & Anti-Forgery in ASP.NET Core](/claude-daily-tips/assets/images/dotnet-2026-10-18-configure-sliding-sessions---anti-forgery-in-asp-n.jpg)



Ensuring user sessions in ASP.NET Core applications gracefully expire after inactivity, while simultaneously hardening against cross-site request forgery (CSRF) attacks, presents a common development challenge. Manually piecing together these security configurations can often lead to verbose code and introduce subtle errors, especially as projects scale. Fortunately, ASP.NET Core provides robust, built-in mechanisms to address both sliding session expiration and anti-forgery token validation efficiently.

The core of enabling these features lies in leveraging the `AddSession()` and `AddAntiforgery()` services within your application's startup. For sliding sessions, this translates to configuring the session cookie's expiration policy to reset upon each user interaction. ASP.NET Core's MVC and Razor Pages frameworks, by default, automatically handle the generation and validation of anti-forgery tokens for forms submitted through their views, abstracting much of the complexity.

Here's how you can configure session state with sliding expiration and ensure anti-forgery protection is active. The `AddSession()` method is configured with `IdleTimeout` to define the period of inactivity after which the session will expire. Crucially, setting `options.Cookie.IsEssential = true` is recommended to ensure the session cookie is treated as essential by the browser, and `options.Cookie.Name` allows for a custom, recognizable cookie name. While `AddAntiforgery()` can be called explicitly for granular control over token names or storage, its core functionality for MVC/Razor Pages is often implicitly enabled by default.

```csharp
// Program.cs (or Startup.cs)
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews(); // Enables MVC and implicitly adds anti-forgery services

// Configure Session State with sliding expiration
builder.Services.AddSession(options =>
{
    // Set a sliding expiration time (e.g., 20 minutes)
    options.IdleTimeout = TimeSpan.FromMinutes(20);
    // Make the session cookie sliding by ensuring it's treated as essential
    options.Cookie.IsEssential = true;
    options.Cookie.Name = ".MyAspNetCoreApp.Session"; // Custom cookie name
});

// Explicitly configuring anti-forgery is often unnecessary for MVC/Razor Pages
// as AddControllersWithViews() typically handles this.
// Uncomment if you need custom header names or advanced configuration:
// builder.Services.AddAntiforgery(options =>
// {
//     options.HeaderName = "X-CSRF-TOKEN"; // Example of custom header name
// });

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

// Session middleware must be added *after* UseRouting and *before* UseEndpoints.
// This ensures session state is available for routing and endpoint execution.
app.UseSession();

// Anti-forgery middleware is usually not explicitly needed when using MVC/Razor Pages
// as the framework handles token validation during form submissions.
// app.UseAntiforgery(); // Only needed for explicit configuration or custom scenarios

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
```

A critical nuance to remember is that `options.IdleTimeout` solely governs the session cookie. If your application employs authentication cookies (e.g., from ASP.NET Core Identity's `AddAuthentication`), these have their *own* independent expiration settings. To achieve a consistent sliding expiration across both session and authentication, you'll need to configure authentication cookie expiration separately, often by implementing custom logic within the `OnValidatePrincipal` event handler of your authentication scheme. This ensures that both the user's session state and their authenticated status are continuously renewed.
