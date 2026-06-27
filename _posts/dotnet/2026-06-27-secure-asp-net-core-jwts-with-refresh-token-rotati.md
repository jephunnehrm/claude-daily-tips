---
layout: post
title: "Secure ASP.NET Core JWTs with Refresh Token Rotation"
date: 2026-06-27
type: how-to
summary: "Implement robust JWT refresh token rotation in ASP.NET Core using Claude Code for silent renewals."
image: "/claude-daily-tips/assets/images/dotnet-2026-06-27-secure-asp-net-core-jwts-with-refresh-token-rotati.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
---



![Secure ASP.NET Core JWTs with Refresh Token Rotation](/claude-daily-tips/assets/images/dotnet-2026-06-27-secure-asp-net-core-jwts-with-refresh-token-rotati.jpg)



As a .NET developer building modern web applications, managing JWT authentication can present challenges, especially when it comes to maintaining security and user experience. A common pain point is handling token expiration gracefully without forcing users to re-authenticate constantly. Refresh token rotation is a best practice that significantly enhances security by invalidating older tokens and issuing new ones automatically, while silent renewal ensures a seamless experience for the end-user.

Claude Code can be a powerful ally in implementing this pattern. By leveraging Claude's code generation capabilities, you can quickly set up the necessary services and logic for managing refresh tokens. This involves creating a mechanism to store refresh tokens securely (e.g., in a database), generating new access and refresh tokens upon a valid refresh token request, and importantly, invalidating the old refresh token after it's been used.

Here's a starting point for implementing refresh token rotation in ASP.NET Core. You'll typically use a JWT library like `Microsoft.AspNetCore.Authentication.JwtBearer` and a database or distributed cache for storing refresh tokens. The core logic involves an endpoint that accepts a refresh token, validates it, generates new tokens, and invalidates the old one. Claude Code can help draft the boilerplate for this endpoint and the associated token service.

```csharp
// Example Service Interface
public interface ITokenService
{
    string GenerateAccessToken(string userId);
    string GenerateRefreshToken(string userId);
    bool ValidateRefreshToken(string refreshToken, string userId);
    void InvalidateRefreshToken(string refreshToken, string userId);
}

// Example Controller Snippet
[Route("api/[controller]")]
[ApiController]
public class AuthController : ControllerBase
{
    private readonly ITokenService _tokenService;
    private readonly IUserService _userService; // Assuming a user service

    public AuthController(ITokenService tokenService, IUserService userService)
    {
        _tokenService = tokenService;
        _userService = userService;
    }

    [HttpPost("refresh")]
    public IActionResult RefreshToken([FromBody] RefreshTokenRequest request)
    {
        if (!_tokenService.ValidateRefreshToken(request.RefreshToken, request.UserId))
        {
            return BadRequest("Invalid refresh token.");
        }

        var user = _userService.GetUserById(request.UserId); // Fetch user details
        if (user == null)
        {
            return BadRequest("User not found.");
        }

        _tokenService.InvalidateRefreshToken(request.RefreshToken, request.UserId);

        var newAccessToken = _tokenService.GenerateAccessToken(request.UserId);
        var newRefreshToken = _tokenService.GenerateRefreshToken(request.UserId);

        // Store new refresh token securely and return both
        // ...
        return Ok(new { AccessToken = newAccessToken, RefreshToken = newRefreshToken });
    }
}

public class RefreshTokenRequest
{
    public string UserId { get; set; }
    public string RefreshToken { get; set; }
}
```

A crucial gotcha to be aware of is the secure storage of refresh tokens. Never store them in client-side storage like `localStorage`. A robust solution involves a dedicated database table or a secure, distributed cache, linked to the user and marked with an expiration. Additionally, consider implementing mechanisms to detect and revoke compromised refresh tokens, such as when a user logs out from all devices.

**Try it:** Use `claude generate ASP.NET Core C# ITokenService` to get a starting point for your token service interface and abstract away some of the initial code generation.
