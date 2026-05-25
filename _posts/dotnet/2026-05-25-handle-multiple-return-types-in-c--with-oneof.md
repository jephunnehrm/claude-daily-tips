---
layout: post
title: "Handle Multiple Return Types in C# with OneOf"
date: 2026-05-25
type: how-to
summary: "Simplify error handling and diverse return scenarios in your .NET code using the OneOf library and Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-05-25-handle-multiple-return-types-in-c--with-oneof.jpg"
tags:
  - dotnet
  - csharp
  - productivity
  - devtools
  - mcp
---



![Handle Multiple Return Types in C# with OneOf](/claude-daily-tips/assets/images/dotnet-2026-05-25-handle-multiple-return-types-in-c--with-oneof.jpg)



As a .NET developer, you've surely wrestled with methods that need to represent success alongside various failure modes, or return data that can take on fundamentally different shapes. The traditional solutions—nested `if/else` chains, out parameters, or even using exceptions for expected control flow—often lead to code that's verbose, difficult to debug, and masks the actual intent. While C# lacks native discriminated unions, the `OneOf` NuGet package offers a robust and type-safe pattern to elegantly manage these scenarios.

`OneOf<T1, T2, ...>` allows you to define a return type that can hold one of the specified generic types. This creates a single, clear contract for your method. Consider an API service that either successfully retrieves a `User` object or returns a specific `ErrorMessage`. With `OneOf<User, ErrorMessage>`, this intent is immediately apparent. The library provides the `Match` method, which acts as a powerful switch statement for the `OneOf` type. `Match` accepts delegates for each possible type, ensuring that you explicitly handle every potential outcome.

Here's a practical example of a `UserService` method returning `OneOf<User, ErrorMessage>` and how to consume it:

```csharp
using OneOf;

public record User(string Name);
public record ErrorMessage(string Message);

public class UserService
{
    public OneOf<User, ErrorMessage> GetUser(int userId)
    {
        if (userId <= 0)
        {
            return new ErrorMessage("User ID must be positive.");
        }
        if (userId == 42)
        {
            return new User("The Answer");
        }
        return new ErrorMessage($"User with ID {userId} not found.");
    }
}

public class ExampleUsage
{
    public void ProcessUser(int id)
    {
        var userService = new UserService();
        var result = userService.GetUser(id);

        result.Match(
            user => Console.WriteLine($"Welcome, {user.Name}!"),
            errorMessage => Console.WriteLine($"Error: {errorMessage.Message}")
        );
    }
}
```
This `Match` pattern is compelling because it forces compile-time exhaustiveness *if* you leverage the `Match` overloads correctly. However, a critical "gotcha" with `OneOf` is that the `Match` method itself doesn't provide compile-time warnings if you omit a case. Forgetting to handle a specific type within `Match` will result in an `InvalidOperationException` at runtime if that type is ever returned. This is where carefully designing your `OneOf` types and consistently using `Match` with all delegates becomes paramount to avoid unexpected crashes.

To solidify your understanding, try installing the `OneOf` NuGet package (`dotnet add package OneOf`). Define a method that returns a `OneOf` type with at least three possibilities (e.g., `OneOf<string, int, bool>`) and then implement a `ProcessResult` method that uses `.Match()` to handle every single one of those potential return types. This exercise will highlight the benefit of explicit handling and the potential pitfall of overlooking a case.
