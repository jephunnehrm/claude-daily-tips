---
layout: post
title: "Integrate SQL Server in .NET Tests with Testcontainers"
date: 2026-10-13
type: how-to
summary: "Quickly set up a SQL Server instance for .NET integration tests using Testcontainers and Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - productivity
---



![Integrate SQL Server in .NET Tests with Testcontainers](assets/images/placeholder.jpg)



Integrating SQL Server into .NET integration tests often presents a significant hurdle for developers. Manually provisioning and cleaning up database instances for each test run is not only time-consuming but also inherently prone to inconsistencies, leading to unreliable tests that may not accurately reflect production environments. Testcontainers provides a robust solution by enabling the dynamic spin-up of real SQL Server instances within isolated Docker containers, ensuring a consistent and predictable testing environment.

To leverage Testcontainers for SQL Server, begin by adding the `Testcontainers.MsSql` NuGet package to your integration test project. This package exposes essential abstractions for orchestrating SQL Server containers. The typical workflow involves configuring and starting the container as part of your test setup. A crucial aspect is retrieving the dynamically assigned connection string from the running container, which you'll then use to configure your application's `DbContext` or data access layer for the duration of the test.

```csharp
using Testcontainers.MsSql;
using Xunit;

public class SqlServerIntegrationTest : IAsyncLifetime
{
    // Initialize the SQL Server container.
    // The WithImage specifies the SQL Server Docker image to use.
    // Replace "YourStrongPassword123!" with a secure password for production scenarios.
    private readonly MsSqlContainer _sqlServerContainer = new MsSqlContainer("mcr.microsoft.com/mssql/server:2022-latest")
        .WithPassword("YourStrongPassword123!");

    // Start the container before tests run.
    public async Task InitializeAsync()
    {
        await _sqlServerContainer.StartAsync();
    }

    // Stop the container after tests complete.
    public Task DisposeAsync()
    {
        return _sqlServerContainer.StopAsync();
    }

    [Fact]
    public async Task CanConnectToSqlServer()
    {
        // Arrange: Retrieve the connection string from the running container.
        var connectionString = _sqlServerContainer.GetConnectionString();

        // In a real scenario, you would now configure your DbContext:
        // using var dbContext = new YourDbContext(new DbContextOptionsBuilder<YourDbContext>().UseSqlServer(connectionString).Options);
        // await dbContext.Database.EnsureCreatedAsync(); // Example: ensure the database is created.

        // Act & Assert: Perform actual database operations and assertions.
        // For demonstration, we'll just verify we got a connection string.
        Assert.NotNull(connectionString);
        Assert.Contains("Server=", connectionString);
        Assert.Contains("Database=", connectionString);
        Assert.Contains("User ID=", connectionString);
        Assert.Contains("Password=", connectionString);
    }
}
```

A common pitfall when working with Testcontainers, especially for database integrations, is managing the container's lifecycle. The idiomatic approach in xUnit is to implement `IAsyncLifetime`, ensuring the container is reliably started before your tests execute and cleanly stopped afterward. A key consideration is password management; hardcoding credentials directly within the builder is generally discouraged for production environments. Instead, explore more secure mechanisms like environment variables or dedicated secrets management solutions to inject sensitive information. This ensures your integration tests not only mimic production but also adhere to security best practices.

This approach offers significant advantages over traditional database integration testing. By running a genuine SQL Server instance within a Docker container, you eliminate the unpredictability associated with in-memory databases or mocked services, ensuring your tests accurately reflect real-world interactions. The isolation provided by containers prevents test contamination and simplifies environment setup, making your CI/CD pipelines more robust and your development workflow more efficient.
