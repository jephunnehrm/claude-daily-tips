---
layout: post
title: "Implement JWT Refresh Token Rotation in ASP.NET Core"
date: 2026-10-01
type: how-to
summary: "Learn how to use Claude Code to build a robust JWT refresh token rotation system for enhanced security in ASP.NET Core."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
---



![Implement JWT Refresh Token Rotation in ASP.NET Core](assets/images/placeholder.jpg)



Implementing robust JWT authentication in ASP.NET Core often involves managing access token lifecycles effectively. While access tokens are short-lived for security, requiring users to re-authenticate every time their access token expires can lead to a poor user experience. Refresh token rotation is a key security pattern that addresses this by allowing users to obtain new access tokens without full re-authentication, while simultaneously mitigating the risk of a compromised refresh token by invalidating previous ones. This involves issuing a new refresh token each time an existing one is used, ensuring that a leaked token's validity is limited to its most recent usage.

The core of this pattern in ASP.NET Core necessitates careful management of token issuance and validation, typically involving custom middleware and persistent storage for refresh tokens. A common approach is to store refresh tokens in a database, linked to a user ID and an expiry date. When a client presents a refresh token, the server validates it against the stored record. If valid, it issues a new access token and a new refresh token, then invalidates the original refresh token in the database. This rotation significantly enhances security by limiting the window of opportunity for an attacker if a refresh token is intercepted.

A critical "gotcha" in this implementation is ensuring secure storage and revocation of refresh tokens. Refresh tokens should **never** be stored in plain text and must be associated with user sessions. Furthermore, robust mechanisms for revoking refresh tokens upon user logout, password reset, or detected compromise are essential. This revocation process requires careful state management, often involving distributed caching or database transactions to ensure that an invalidated token cannot be used to generate new access tokens. The persistence layer plays a vital role here, acting as the single source of truth for valid refresh tokens.

Consider this simplified conceptual C# code snippet demonstrating the issuance of a new refresh token. In a production scenario, `Guid.NewGuid().ToString()` should be replaced with a cryptographically secure pseudo-random number generator, and the `expiryDate` should be configurable and managed according to your application's security policies.

```csharp
using System;
using System.Threading.Tasks;
using YourApp.Data.Entities; // Assuming a RefreshToken entity exists
using YourApp.Services.Interfaces; // Assuming an IRefreshTokenRepository interface

public class RefreshTokenService
{
    private readonly IRefreshTokenRepository _refreshTokenRepository;
    private readonly TimeSpan _refreshTokenLifetime = TimeSpan.FromDays(7);

    public RefreshTokenService(IRefreshTokenRepository refreshTokenRepository)
    {
        _refreshTokenRepository = refreshTokenRepository ?? throw new ArgumentNullException(nameof(refreshTokenRepository));
    }

    public async Task<string> IssueNewRefreshTokenAsync(string userId)
    {
        // Generate a new, cryptographically secure token (replace Guid.NewGuid() in production)
        string newToken = Guid.NewGuid().ToString(); // In production, use RngCryptoServiceProvider or similar

        var expiryDate = DateTime.UtcNow.Add(_refreshTokenLifetime);

        // Add the new token to the repository and invalidate any previous tokens for this user
        await _refreshTokenRepository.AddNewRefreshTokenAsync(userId, newToken, expiryDate);

        return newToken;
    }

    // Example of a method to validate and rotate a refresh token (omitted for brevity, but crucial)
    // public async Task<(bool isValid, string userId)> ValidateAndRotateRefreshTokenAsync(string token) { ... }
}
```
