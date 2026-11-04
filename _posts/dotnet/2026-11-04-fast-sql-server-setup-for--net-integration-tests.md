---
layout: post
title: "Fast SQL Server Setup for .NET Integration Tests"
date: 2026-11-04
type: how-to
summary: "Use Claude Code to quickly configure Testcontainers for SQL Server in your .NET integration tests."
image: "/claude-daily-tips/assets/images/dotnet-2026-11-04-fast-sql-server-setup-for--net-integration-tests.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - automation
---



![Fast SQL Server Setup for .NET Integration Tests](/claude-daily-tips/assets/images/dotnet-2026-11-04-fast-sql-server-setup-for--net-integration-tests.jpg)



One common bottleneck in .NET integration testing is the setup and teardown of external dependencies like databases. Manually managing SQL Server instances for each test run, or relying on shared development databases, can lead to flaky tests and slow feedback loops. Testcontainers offers a powerful solution by spinning up disposable, lightweight Docker containers for your dependencies, effectively isolating your tests and ensuring reproducible environments. However, configuring Testcontainers, especially for specific database versions and configurations, can still involve some boilerplate C# code, diverting attention from core testing logic.

Leveraging AI-powered code generation, like from Claude, can significantly accelerate this process. Instead of manually writing the Testcontainers integration logic for SQL Server, you can prompt Claude to generate the necessary C# code. Claude's understanding of common testing patterns and the Testcontainers APIs allows it to produce setup code that adheres to best practices, enabling you to focus on writing your actual integration tests rather than wrestling with infrastructure setup. This empowers you to quickly spin up isolated SQL Server instances tailored to your test needs.

Here's an example of how you might configure Testcontainers for SQL Server within a typical .NET integration test project using xUnit. Assuming your test project targets `net8.0`, you'll need to include the `Testcontainers.MsSql`, `Microsoft.EntityFrameworkCore.SqlServer`, and your relevant EF Core tools NuGet packages. The following code demonstrates using an `IAsyncLifetime` fixture to manage the container's lifecycle.

```csharp
// In your test setup class (e.g., implementing IAsyncLifetime for a class fixture)
using Testcontainers.MsSql;
using Microsoft.EntityFrameworkCore;
using Xunit;
using System.Threading.Tasks;

public class SqlServerFixture : IAsyncLifetime
{
    // Use a specific, stable version for predictability
    private readonly MsSqlContainer _sqlContainer = new MsSqlBuilder()
        .WithImage("mcr.microsoft.com/mssql/server:2022-CU10")
        .Build();

    public string ConnectionString => _sqlContainer.GetConnectionString();

    public Task InitializeAsync()
    {
        // Start the SQL Server container
        return _sqlContainer.StartAsync();
    }

    public Task DisposeAsync()
    {
        // Gracefully dispose the container after tests complete
        return _sqlContainer.DisposeAsync().AsTask();
    }

    // Consider adding methods here for database seeding or schema creation
    // public async Task SeedDatabaseAsync(YourDbContext context) { ... }
}

// In your test class
public class ProductRepositoryTests : IClassFixture<SqlServerFixture>
{
    private readonly SqlServerFixture _fixture;

    public ProductRepositoryTests(SqlServerFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task GetProductById_ReturnsCorrectProduct()
    {
        // Configure your DbContext to use the container's connection string
        var options = new DbContextOptionsBuilder<YourDbContext>()
            .UseSqlServer(_fixture.ConnectionString)
            .Options;

        using (var context = new YourDbContext(options))
        {
            // Example: Uncomment and adapt for your actual test logic
            // context.Database.EnsureCreated(); // or use migrations
            // await context.Products.AddAsync(new Product { Id = 1, Name = "Test Product" });
            // await context.SaveChangesAsync();

            // var repository = new ProductRepository(context);
            // var product = await repository.GetByIdAsync(1);

            // Assert.NotNull(product);
            // Assert.Equal("Test Product", product.Name);
        }
    }
}
```

A critical consideration with Testcontainers is managing the container lifecycle and potential environmental drift. While `IAsyncLifetime` offers a clean pattern for class fixtures, ensure robust exception handling during container startup and disposal. Furthermore, it's highly recommended to pin Testcontainers images to precise versions (e.g., `mcr.microsoft.com/mssql/server:2022-CU10`) rather than using `:latest` tags. This prevents unexpected test failures caused by minor updates to the base SQL Server image, ensuring consistent behavior across your CI/CD pipeline and development environments.

**Try it:** Use `claude` to ask for C# code to set up `Testcontainers` for `PostgreSQL` in an ASP.NET Core integration test project.
