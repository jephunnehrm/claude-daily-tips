---
layout: post
title: "ASP.NET Core Integration Tests with WebApplicationFactory"
date: 2026-07-21
type: how-to
summary: "Write reliable ASP.NET Core integration tests using WebApplicationFactory and Claude Code for faster feedback."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-21-asp-net-core-integration-tests-with-webapplication.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![ASP.NET Core Integration Tests with WebApplicationFactory](/claude-daily-tips/assets/images/dotnet-2026-07-21-asp-net-core-integration-tests-with-webapplication.jpg)



When building ASP.NET Core applications, ensuring your API endpoints behave as expected is crucial. Manually testing each endpoint can be tedious and error-prone, especially as your application grows. Integration tests offer a robust solution, allowing you to test your application's components working together, including the web layer. ASP.NET Core provides `WebApplicationFactory<TStartup>`, a powerful tool for creating in-memory test servers for your application without needing to run IIS or Kestrel explicitly. This significantly speeds up test execution and simplifies setup.

Integrating Claude Code with your integration tests can further enhance productivity. Claude Code can help generate boilerplate test code, suggest assertions based on API responses, and even assist in crafting complex request bodies. For example, imagine you're testing an endpoint that expects a specific JSON payload. Claude Code can help you quickly define that structure and populate it with valid data, saving you manual typing and potential syntax errors. The `WebApplicationFactory` creates an instance of your application's `Startup` class and configures it for testing.

Here’s a basic example of how you might set up an integration test using `WebApplicationFactory` in a .NET test project. You’ll typically use a testing framework like xUnit or MSTest. This example assumes you have a simple API endpoint for retrieving a product by ID.

```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;
using System.Net.Http;
using System.Threading.Tasks;
using MyWebApp; // Replace with your application's namespace

public class ProductsIntegrationTests : IClassFixture<WebApplicationFactory<Startup>>
{
    private readonly WebApplicationFactory<Startup> _factory;

    public ProductsIntegrationTests(WebApplicationFactory<Startup> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task GetProduct_ReturnsSuccessAndCorrectContent()
    {
        // Arrange
        var client = _factory.CreateClient();
        var productId = 1;

        // Act
        var response = await client.GetAsync($"/api/products/{productId}");

        // Assert
        response.EnsureSuccessStatusCode(); // Status Code 200-299
        var product = await System.Text.Json.JsonSerializer.DeserializeAsync<Product>(
            await response.Content.ReadAsStreamAsync(),
            new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

        Assert.NotNull(product);
        Assert.Equal(productId, product.Id);
        // Add more assertions for product properties
    }
}

// Dummy Product class for example purposes
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    // ... other properties
}
```

A common gotcha when using `WebApplicationFactory` is managing dependencies. By default, it uses your application's dependency injection container. If your tests require different configurations for certain services (e.g., mocking a database service), you'll need to use the `WithWebHostBuilder` method to override registrations in the `ConfigureTestServices` method of your `WebApplicationFactory` or a custom test factory. Furthermore, ensure that your test project references the main ASP.NET Core application project.

**Try it:** Create a new xUnit test project, add a reference to your ASP.NET Core project, and implement a basic `WebApplicationFactory` test for one of your API endpoints. Explore how Claude Code can help you generate the test method structure or suggest assertions.
