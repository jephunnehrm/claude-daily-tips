---
layout: chapter
title: "Duende IdentityServer Patterns with Claude Code"
date: 2026-09-14
series: "dotnet-and-claude"
series_name: ".NET and Claude Code"
week: 38
summary: "This chapter explores advanced Duende IdentityServer patterns and OAuth 2.0 flows, demonstrating how to integrate them with Claude Code for enhanced development workflows. Learn practical implementation strategies and architectural considerations for securing your .NET applications."
image: "/claude-daily-tips/assets/images/chapter-dotnet-and-claude-week38.jpg"
tags:
  - claude-code
  - mcp
  - dotnet
  - azure
  - identity
  - architecture
---



![Duende IdentityServer Patterns with Claude Code](/claude-daily-tips/assets/images/chapter-dotnet-and-claude-week38.jpg)



## Duende IdentityServer Patterns and OAuth 2.0 Flows with Claude Code

As .NET developers, we frequently encounter the need for robust and secure identity management. Duende IdentityServer (formerly IdentityServer4) is the de facto standard for implementing OAuth 2.0 and OpenID Connect in .NET applications. This chapter delves into advanced patterns for leveraging Duende IdentityServer, specifically demonstrating how to integrate with Claude Code (accessed via the `claude` CLI) to accelerate development, automate configuration, and ensure best practices are followed. We'll move beyond basic setup to explore real-world architectural considerations and common pitfalls.

### TL;DR

*   Understand how to leverage Duende IdentityServer's extensibility for custom flows and resource ownership.
*   Learn to use Claude Code to generate and validate IdentityServer configurations, and scaffold common OAuth 2.0 scenarios.
*   Explore architectural patterns for integrating IdentityServer with microservices and client applications.
*   Identify and avoid common pitfalls related to token management, scope validation, and extensibility.

### Advanced Duende IdentityServer Flows and Patterns

Duende IdentityServer provides a highly extensible framework. Understanding its core flows and how to extend them is crucial for building secure and scalable applications.

#### Resource Owner Password Credentials Flow (ROP) - When and How

The Resource Owner Password Credentials (ROP) flow is often misunderstood and misused. It allows a client to directly request an access token using the user's username and password. While convenient for specific scenarios (like legacy applications or trusted first-party clients where the user has no direct UI access), it bypasses the user's browser and is **generally discouraged** due to security implications (clients handle user credentials).

**Architectural Consideration:** Use ROP only when absolutely necessary, for example, in server-to-server communication where the "resource owner" is an automated service, not a human user. For human users, prefer the Authorization Code flow with PKCE.

**Claude Code for ROP Scaffolding:**

You can use `claude` to generate boilerplate for an ROP client.

```bash
claude generate .NET API client for ROP flow --client-id "my-rop-client" --client-secret "secret" --identityserver-url "https://my.identityserver.com" --scope "api1 offline_access"
```

This command would (conceptually) generate C# code for a client application that can initiate the ROP flow. This code would typically involve:
1.  Configuring an `HttpClient` to talk to the IdentityServer.
2.  Making a POST request to the `/connect/token` endpoint with `grant_type=password`, `username`, `password`, `client_id`, `client_secret`, and `scope`.

**Example (Conceptual C# Client Snippet):**

```csharp
using IdentityModel.Client;
using System;
using System.Net.Http;
using System.Threading.Tasks;

public class RopClient
{
    private readonly HttpClient _httpClient;
    private readonly string _identityServerUrl;
    private readonly string _clientId;
    private readonly string _clientSecret;

    public RopClient(string identityServerUrl, string clientId, string clientSecret)
    {
        _identityServerUrl = identityServerUrl;
        _clientId = clientId;
        _clientSecret = clientSecret;
        _httpClient = new HttpClient();
    }

    public async Task<TokenResponse> GetTokenAsync(string username, string password, string scope)
    {
        var tokenResponse = await _httpClient.RequestPasswordTokenAsync(new PasswordTokenRequest
        {
            Address = $"{_identityServerUrl}/connect/token",
            ClientId = _clientId,
            ClientSecret = _clientSecret,
            UserName = username,
            Password = password,
            Scope = scope
        });

        if (tokenResponse.IsError)
        {
            throw new Exception($"Error getting token: {tokenResponse.ErrorDescription}");
        }

        return tokenResponse;
    }

    public static async Task Main(string[] args)
    {
        var identityServerUrl = "https://localhost:5001"; // Replace with your IdentityServer URL
        var clientId = "my-rop-client";
        var clientSecret = "secret"; // In a real app, use a secure secret management solution
        var username = "testuser";
        var password = "password123";
        var scope = "api1 offline_access";

        var ropClient = new RopClient(identityServerUrl, clientId, clientSecret);

        try
        {
            var token = await ropClient.GetTokenAsync(username, password, scope);
            Console.WriteLine($"Access Token: {token.AccessToken}");
            Console.WriteLine($"Refresh Token: {token.RefreshToken}");
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
        }
    }
}
```

#### Customizing Token Signatures and Encryption

Duende IdentityServer allows you to configure custom signing credentials, including using hardware security modules (HSMs) or managed key services (like Azure Key Vault). This is critical for production environments.

**Architectural Consideration:** Do not use development keys (like the default development signing key) in production. Integrate with a secure key management system. For maximum security, consider asymmetric signing algorithms (RS256, PS256) over symmetric ones (HS256).

**Claude Code for Key Management Integration:**

You can ask `claude` to generate configuration snippets for integrating with Azure Key Vault.

```bash
claude generate Azure Key Vault integration for Duende IdentityServer signing credentials --key-vault-name "my-identityserver-kv" --secret-name "ids-signing-key"
```

This would output configuration code similar to this (within `Program.cs` or equivalent):

```csharp
// Example using Azure.Identity and Azure.Security.KeyVault.Secrets
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using System.Security.Cryptography.X509Certificates;

// ... in your Program.cs or Startup.cs Configure method

public static IHostBuilder CreateHostBuilder(string[] args) =>
    Host.CreateDefaultBuilder(args)
        .ConfigureWebHostDefaults(webBuilder =>
        {
            webBuilder.UseStartup<Startup>();
        })
        .ConfigureAppConfiguration((context, config) =>
        {
            var hostingEnvironment = context.HostingEnvironment;

            // Add Azure Key Vault configuration provider
            config.AddAzureKeyVault(
                new Uri($"https://{hostingEnvironment.EnvironmentName}-ids-kv.vault.azure.net/"), // Adjust URL based on env
                new DefaultAzureCredential()); // Assumes environment is configured for Azure auth

            // Load other configurations (appsettings.json, etc.)
            config.SetBasePath(hostingEnvironment.ContentRootPath)
                  .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                  .AddJsonFile($"appsettings.{hostingEnvironment.EnvironmentName}.json", optional: true, reloadOnChange: true);
        });

// ... in your Startup.cs ConfigureServices method
public void ConfigureServices(IServiceCollection services)
{
    var builder = services.AddIdentityServer(options =>
    {
        // ... other options
    });

    // Load signing credentials from Azure Key Vault
    var configuration = services.BuildServiceProvider().GetService<IConfiguration>();
    var keyVaultName = configuration["KeyVaultName"]; // e.g., "my-identityserver-kv"
    var secretName = configuration["SigningSecretName"]; // e.g., "ids-signing-key"

    // Use Azure.Identity to authenticate and Azure.Security.KeyVault.Secrets to retrieve the secret
    var kvClient = new SecretClient(new Uri($"https://{keyVaultName}.vault.azure.net/"), new DefaultAzureCredential());
    KeyVaultSecret secret = kvClient.GetSecret(secretName);
    var certBytes = Convert.FromBase64String(secret.Value);
    var signingCertificate = new X509Certificate2(certBytes);

    builder.AddSigningCredential(signingCertificate);

    // ... rest of ConfigureServices
}
```

**Note:** The `DefaultAzureCredential` will attempt to authenticate using various methods, including environment variables, managed identity, Azure CLI, etc. Ensure your deployment environment is correctly configured.

### Integrating Duende IdentityServer with Microservices and Client Applications

A common architectural pattern is to have a dedicated IdentityServer as a central authority, with resource servers (microservices) validating tokens.

#### API Gateway as Token Validator

An API Gateway can be an ideal place to centralize token validation. Clients send their access token to the gateway, which then validates it before forwarding requests to downstream microservices. This reduces the burden on each individual microservice.

**Architectural Consideration:** The API Gateway needs to trust the IdentityServer. It can achieve this by:
1.  **Introspection Endpoint:** The gateway calls the IdentityServer's introspection endpoint to validate the token. This requires the gateway to have a client ID and secret registered with IdentityServer.
2.  **Public Key Validation:** The gateway downloads the IdentityServer's public signing keys (JWKS endpoint) and validates JWT signatures locally. This is generally more performant.

**Claude Code for API Gateway Configuration:**

You can ask `claude` to help configure an API Gateway (e.g., Ocelot) for token validation.

```bash
claude generate Ocelot API Gateway configuration for JWT validation --identityserver-jwks-url "https://my.identityserver.com/.well-known/openid-configuration/jwks" --api-key "my-gateway-client-id"
```

This command would output a `ocelot.json` snippet like this:

```json
{
  "ReRoutes": [
    {
      "DownstreamPathTemplate": "/{everything}",
      "DownstreamScheme": "https",
      "DownstreamHostAndPorts": [
        {
          "Host": "my.microservice.com",
          "Port": 443
        }
      ],
      "UpstreamPathTemplate": "/api/{everything}",
      "UpstreamHttpMethod": [ "Get", "Post", "Put", "Delete" ],
      "AuthenticationOptions": {
        "AuthenticationProviderKey": "IdentityServerJwt",
        "AllowedScopes": [ "api1" ]
      }
    }
  ],
  "GlobalConfiguration": {
    "ServiceDiscoveryProvider": {
      "Scheme": "https",
      "Host": "localhost",
      "Port": 8500 // Example for Consul
    },
    "ApiKeys": [
        {
            "ReRouteKey": "AuthenticationProviderKey", // Maps to the AuthenticationProviderKey in ReRoutes
            "ApiKey": "my-gateway-client-id" // Secret for the gateway itself, not for token validation
        }
    ],
    "IdentityServerJwt": { // This section is handled by the Ocelot JWT middleware
      "Authority": "https://my.identityserver.com",
      "RequireHttpsMetadata": true,
      "ValidateIssuer": true,
      "ValidateAudience": true,
      "Audience": "api1" // The audience the gateway expects for the tokens
    }
  }
}
```

**Explanation:**
*   `AuthenticationProviderKey`: Links the re-route to the JWT middleware configuration.
*   `AllowedScopes`: Specifies the scopes that must be present in the token for this re-route to be accessible.
*   `IdentityServerJwt` (within `GlobalConfiguration` for certain Ocelot setups or configured via middleware): This is where you'd configure the Authority, JWKS URL (implicitly handled if `Authority` is provided and `RequireHttpsMetadata` is true), and validation parameters.

#### Resource Ownership and Custom Scopes

When building APIs, you often need to represent resources. IdentityServer uses scopes to grant access to these resources. Customizing scopes is key to granular authorization.

**Architectural Consideration:** Design your scopes to map logically to the resources or operations your API provides. Avoid overly broad scopes. Consider using custom claims to pass additional authorization information.

**Claude Code for Custom Scope Definition:**

You can ask `claude` to generate the C# configuration for defining custom scopes and API resources.

```bash
claude generate Duende IdentityServer API resource with custom scopes --api-resource-name "MyCompany.Services.Catalog" --scopes "read:products,write:products,read:categories" --display-name "Catalog API"
```

This would produce C# code similar to this:

```csharp
using Duende.IdentityServer.Models;
using System.Collections.Generic;

public static class Config
{
    public static IEnumerable<IdentityResource> IdentityResources =>
        new IdentityResource[]
        {
            new IdentityResources.OpenId(),
            new IdentityResources.Profile(),
        };

    public static IEnumerable<ApiScope> ApiScopes =>
        new ApiScope[]
        {
            new ApiScope("read:products", "Read access to products"),
            new ApiScope("write:products", "Write access to products"),
            new ApiScope("read:categories", "Read access to categories"),
        };

    public static IEnumerable<ApiResource> ApiResources =>
        new ApiResource[]
        {
            new ApiResource("MyCompany.Services.Catalog", "Catalog API", new[] { "role" }) // Add custom claims here
            {
                Scopes = { "read:products", "write:products", "read:categories" }
            }
        };

    // Clients would also be defined here
}
```

You would then register these in your IdentityServer's `Config.cs` and ensure your client applications request these scopes.

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Over-reliance on Implicit Flow

The Implicit flow, while simpler for SPAs, returns tokens directly in the URL fragment. This is less secure than the Authorization Code flow with PKCE, especially for public clients (SPAs, mobile apps).

**Avoidance:** Always use the **Authorization Code flow with PKCE** for public clients. Duende IdentityServer and libraries like `oidc-client-ts` (for JavaScript) and `IdentityModel` (for .NET) fully support this.

#### Pitfall 2: Insecure Handling of Refresh Tokens

Refresh tokens grant long-lived access. If a refresh token is compromised, an attacker can obtain new access tokens without user interaction.

**Avoidance:**
*   **Use sliding expiration:** Configure refresh tokens to be re-issued with a new expiration date each time they are used.
*   **Use refresh token rotation:** Issue a new refresh token and invalidate the old one with each use. This helps detect token theft.
*   **Store refresh tokens securely:** Encrypt them at rest in your database, and restrict access.
*   **Consider `offline_access` scope carefully:** Only grant it when necessary.

**Claude Code for Refresh Token Configuration:**

```bash
claude generate Duende IdentityServer refresh token sliding expiration --days 30
```

This would generate C# configuration similar to:

```csharp
// In IdentityServerOptions configuration
options.UserInteraction.LoginReturnUrlParameter = "returnUrl"; // Example of other options

// Configure Token Consumption
options.Caching.SlidingExpiration = TimeSpan.FromDays(30); // Example for caching, related to refresh tokens
options.RefreshTokenUsage = TokenUsage.Reclaim; // or TokenUsage.OneTime
options.RefreshTokenExpiration = TokenExpiration.Sliding; // or TokenExpiration.Absolute
options.AbsoluteRefreshTokenLifetime = TimeSpan.FromDays(90);
options.SlidingRefreshTokenLifetime = TimeSpan.FromDays(30);
```

#### Pitfall 3: Improper Scope Validation in Resource Servers

Resource servers (your APIs) must rigorously validate the scopes present in the access token. Simply trusting the token's existence is insufficient.

**Avoidance:** When validating tokens in your API, explicitly check for the required scopes using the `scope` claim in the JWT.

**Example (ASP.NET Core API Controller):**

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Linq;

[ApiController]
[Route("api/[controller]")]
[Authorize("Bearer")] // Requires a valid Bearer token
public class ProductsController : ControllerBase
{
    [HttpGet]
    [Authorize(Policy = "ReadProductsPolicy")] // Custom authorization policy
    public IActionResult GetProducts()
    {
        // Access the user's claims
        var userId = User.FindFirst("sub")?.Value;
        var scopes = User.Claims.Where(c => c.Type == "scope").Select(c => c.Value);

        // In a real scenario, you'd check if "read:products" is in the scopes collection.
        // The Authorize attribute with a policy is the more idiomatic way.

        return Ok(new[] { "Product A", "Product B" });
    }
}

// In Startup.cs ConfigureServices:
services.AddAuthorization(options =>
{
    options.AddPolicy("ReadProductsPolicy", policy =>
    {
        policy.RequireAuthenticatedUser();
        policy.RequireClaim("scope", "read:products"); // Explicitly require the scope
    });
});
```

By understanding these patterns, leveraging tools like Claude Code for scaffolding and configuration, and being mindful of common pitfalls, you can build highly secure and well-architected identity solutions with Duende IdentityServer.
