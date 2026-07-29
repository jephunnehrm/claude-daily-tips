---
layout: post
title: "Test ASP.NET Core APIs with WebApplicationFactory"
date: 2026-07-29
type: how-to
summary: "Integrate API testing into your ASP.NET Core workflow using WebApplicationFactory."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-29-test-asp-net-core-apis-with-webapplicationfactory.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
---



![Test ASP.NET Core APIs with WebApplicationFactory](/claude-daily-tips/assets/images/dotnet-2026-07-29-test-asp-net-core-apis-with-webapplicationfactory.jpg)



Integrating ASP.NET Core APIs often involves the tedious setup of testing environments, forcing developers to choose between slow, full deployments or brittle unit tests that don't reflect real-world behavior. The `WebApplicationFactory<TStartup>` from the `Microsoft.AspNetCore.Mvc.Testing` NuGet package offers a compelling solution by providing a lightweight, in-memory host for your ASP.NET Core application. This enables you to create `HttpClient` instances that target your application's pipeline directly, bypassing the network stack and offering fast, reliable, and isolated integration tests.

The fundamental principle is to instantiate `WebApplicationFactory` with your application's startup class (`TStartup`). Subsequently, the `CreateClient()` method yields an `HttpClient` instance capable of interacting with your application's middleware, routing, and controllers as if it were a live HTTP request. This allows you to perform standard HTTP operations (GET, POST, PUT, DELETE) and assert on the resulting status codes, headers, and response bodies, mirroring how external clients would interact with your API.

A crucial aspect of leveraging `WebApplicationFactory` is customizing the `IWebHostBuilder` through overriding the `ConfigureWebHost` method. This is indispensable for replacing dependencies registered in your `Startup.cs` with test-specific implementations, such as substituting a production database context with an in-memory provider or injecting mock services for external dependencies. A common pitfall to be aware of is managing the lifetime of these overridden scoped or transient services; the factory needs to correctly manage their lifecycle to prevent unexpected behavior or `NullReferenceException`s during test execution.

For instance, imagine you need to test an endpoint that relies on a scoped database context. When overriding services, you must ensure that the factory is aware of the intended scope. This can be achieved by obtaining the scoped service from the factory's `Services` collection within the test itself, rather than relying on a globally scoped instance.

```csharp
// Example Test in xUnit demonstrating scoped service override
public class ProductIntegrationTests : IClassFixture<WebApplicationFactory<MyProject.Startup>>
{
    private readonly WebApplicationFactory<MyProject.Startup> _factory;

    public ProductIntegrationTests(WebApplicationFactory<MyProject.Startup> factory)
    {
        // ConfigureWebHost is often implicitly called by the factory,
        // but you can explicitly override it for service replacement.
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace actual DbContext with an in-memory provider
                var descriptor = services.SingleOrDefault(d =>
                    d.ServiceType == typeof(DbContextOptions<MyDbContext>));

                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                services.AddDbContext<MyDbContext>(options =>
                    options.UseInMemoryDatabase("InMemoryDbForTesting"));
            });
        });
    }

    [Fact]
    public async Task Get_Product_ReturnsSuccessAndCorrectData()
    {
        var client = _factory.CreateClient();

        // Seed the in-memory database with some test data
        using (var scope = _factory.Services.CreateScope())
        {
            var dbContext = scope.ServiceProvider.GetRequiredService<MyDbContext>();
            dbContext.Products.Add(new Product { Id = 1, Name = "Test Product" });
            await dbContext.SaveChangesAsync();
        }

        var response = await client.GetAsync("/api/products/1");

        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        // Assert on content here, e.g., using Newtonsoft.Json or System.Text.Json
        Assert.Contains("\"name\":\"Test Product\"", content);
    }
}
```
