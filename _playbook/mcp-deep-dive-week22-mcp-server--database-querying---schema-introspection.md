---
layout: chapter
title: "MCP Server: Database Querying & Schema Introspection"
date: 2026-05-25
series: "mcp-deep-dive"
series_name: "MCP Deep Dive"
week: 22
summary: "This chapter explores leveraging MCP Server for efficient database querying and robust schema introspection within your .NET and Java applications on Azure. Learn practical implementation patterns and architectural considerations for building intelligent data access layers."
image: "https://image.pollinations.ai/prompt/Abstract%20dark%20tech%20architectural%20diagram%20of%20interconnected%20nodes%20representing%20MCP%20Server%2C%20databases%2C%20and%20AI%20models%20on%20Azure%20cloud%20infrastructure?width=800&height=400&nologo=true&model=flux"
tags:
  - claude-code
  - mcp
  - dotnet
  - azure
  - agents
  - architecture
  - devtools
  - productivity
  - csharp
  - java
---



![MCP Server: Database Querying & Schema Introspection](https://image.pollinations.ai/prompt/Abstract%20dark%20tech%20architectural%20diagram%20of%20interconnected%20nodes%20representing%20MCP%20Server%2C%20databases%2C%20and%20AI%20models%20on%20Azure%20cloud%20infrastructure?width=800&height=400&nologo=true&model=flux)



## TL;DR

*   MCP Server integrates with your existing databases to enable sophisticated, AI-driven querying and schema introspection.
*   Understand how to configure MCP Server to connect to SQL Server, PostgreSQL, and other Azure-hosted databases.
*   Explore architectural patterns for building adaptive data access layers using MCP's schema understanding capabilities.
*   Learn to effectively use the `claude` CLI for schema discovery and initial query generation.
*   Mitigate common pitfalls like over-reliance on AI for critical operations and improper schema caching.

## Introduction to MCP Server for Data Access

As seasoned architects and developers, we're constantly seeking ways to abstract complexity and imbue our applications with intelligence. When it comes to database interaction, the traditional ORM (Object-Relational Mapper) or raw SQL approach, while powerful, can become cumbersome for dynamic querying and understanding evolving schemas. This is where MCP Server, when coupled with Claude Code's capabilities, offers a compelling paradigm shift.

MCP Server acts as an intelligent intermediary between your application and your databases. It leverages its understanding of your database schema, combined with advanced AI models (powered by Claude), to facilitate not only more natural language-based queries but also deep schema introspection. This allows your applications to be more adaptive, discoverable, and capable of handling complex data exploration tasks with greater ease.

This chapter will guide you through the practical and architectural considerations of using MCP Server for database querying and schema introspection, primarily focusing on .NET and Java applications hosted on Azure.

## MCP Server Architecture and Data Flow

At its core, MCP Server operates by maintaining a representation of your database schema. This representation is the bedrock upon which its AI-powered capabilities are built. When you query MCP Server, it doesn't directly execute your natural language request against the database. Instead, it:

1.  **Receives the Query:** This can be a natural language request or a more structured query intended for the MCP API.
2.  **Schema Contextualization:** MCP Server utilizes its cached schema information (or fetches it on demand) to understand the entities, relationships, and data types involved in the query.
3.  **AI Query Generation/Interpretation:** The Claude AI model, informed by the schema context, translates the user's intent into an executable SQL (or other database-specific) query. This is where the "intelligence" truly shines, enabling more abstract and flexible querying.
4.  **Query Execution:** The generated SQL query is then executed against the actual database.
5.  **Result Transformation:** The database results are returned to MCP Server, which may then format them for the client application, potentially enriching them with contextual metadata.

**Schema Introspection:** This process involves MCP Server actively cataloging and understanding your database schema. This can be done upfront during configuration or dynamically. The introspection process populates MCP Server's internal knowledge graph of your database, enabling the AI to reason about your data.

**Azure Integration:** MCP Server is designed to run efficiently within Azure. It can be deployed as an Azure App Service, an Azure Container Instance, or even within an Azure Kubernetes Service (AKS) cluster. Its data sources can be any Azure-managed database service, such as Azure SQL Database, Azure Database for PostgreSQL, Azure Cosmos DB (with appropriate adapters), or even self-hosted SQL Server instances on Azure Virtual Machines.

## Configuring MCP Server for Database Connections

The first step to leveraging MCP Server is to configure its connection to your target databases. This typically involves providing connection strings and specifying the database type.

### .NET Configuration Example (appsettings.json)

For .NET applications, MCP Server's configuration can often be integrated into the application's `appsettings.json`.

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "MCP": {
    "DatabaseConnections": [
      {
        "Name": "PrimaryUserDB",
        "ConnectionString": "Server=tcp:your-azure-sql-server.database.windows.net,1433;Initial Catalog=UserDatabase;Persist Security Info=False;User ID=your_db_user;Password=your_db_password;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;",
        "Type": "SqlServer",
        "SchemaDiscoveryEnabled": true,
        "SchemaRefreshIntervalMinutes": 60
      },
      {
        "Name": "AnalyticsPostgres",
        "ConnectionString": "Host=your-pg-server.postgres.database.azure.com;Database=AnalyticsDB;Username=your_pg_user@your-pg-server;Password=your_pg_password;SslMode=Require;",
        "Type": "PostgreSql",
        "SchemaDiscoveryEnabled": true,
        "SchemaRefreshIntervalMinutes": 120
      }
    ],
    "ClaudeApi": {
      "ApiKey": "YOUR_CLAUDE_API_KEY",
      "Endpoint": "https://api.claude.ai/v1"
    }
  }
}
```

**Explanation:**

*   `DatabaseConnections`: An array defining each database MCP Server needs to connect to.
    *   `Name`: A logical identifier for the connection.
    *   `ConnectionString`: The standard connection string for the database. For Azure services, ensure proper authentication (e.g., SQL authentication, Azure AD authentication).
    *   `Type`: Specifies the database dialect (e.g., `SqlServer`, `PostgreSql`). MCP Server will have adapters for common types.
    *   `SchemaDiscoveryEnabled`: If `true`, MCP Server will attempt to discover and cache the schema upon startup and periodically.
    *   `SchemaRefreshIntervalMinutes`: How often to re-scan the schema for changes if discovery is enabled.
*   `ClaudeApi`: Configuration for accessing the Claude AI model.

### Java Configuration Example (application.properties)

For Java applications using Spring Boot, a similar configuration can be managed in `application.properties`.

```properties
# MCP Server Configuration
mcp.databaseConnections[0].name=PrimaryUserDB
mcp.databaseConnections[0].connectionString=jdbc:sqlserver://your-azure-sql-server.database.windows.net:1433;databaseName=UserDatabase;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;user=your_db_user;password=your_db_password
mcp.databaseConnections[0].type=SqlServer
mcp.databaseConnections[0].schemaDiscoveryEnabled=true
mcp.databaseConnections[0].schemaRefreshIntervalMinutes=60

mcp.databaseConnections[1].name=AnalyticsPostgres
mcp.databaseConnections[1].connectionString=jdbc:postgresql://your-pg-server.postgres.database.azure.com:5432/AnalyticsDB?sslmode=require
mcp.databaseConnections[1].type=PostgreSql
mcp.databaseConnections[1].schemaDiscoveryEnabled=true
mcp.databaseConnections[1].schemaRefreshIntervalMinutes=120

# Claude API Configuration
mcp.claudeApi.apiKey=YOUR_CLAUDE_API_KEY
mcp.claudeApi.endpoint=https://api.claude.ai/v1
```

**Key Differences for Java:**

*   The connection string format will be JDBC-based.
*   Properties are prefixed with `mcp.`.
*   Arrays are handled using indexed properties (e.g., `[0]`, `[1]`).

## Schema Introspection with Claude Code CLI

Before you even write application code, you can use the `claude` CLI to interact with MCP Server and understand your database schema. This is invaluable for gaining quick insights and kickstarting your development.

The `claude` CLI, when configured to communicate with an MCP Server instance (often via a local development setup or a deployed instance), can perform schema introspection tasks.

**Prerequisites:**

*   MCP Server running locally or accessible remotely.
*   `claude` CLI installed and configured with your Claude API key.
*   MCP Server configured with at least one database connection as described above.

**CLI Command for Schema Discovery:**

First, ensure your MCP Server is running and has a database connection configured. Then, use the `claude` CLI to introspect a specific database.

```bash
# Assuming your MCP Server is running on localhost:5000 (or your configured port)
claude mcp schema introspect --server http://localhost:5000 --db-name PrimaryUserDB --output schema.json
```

**Explanation:**

*   `claude mcp schema introspect`: This is the command to initiate schema introspection for MCP.
*   `--server http://localhost:5000`: Specifies the address of your MCP Server instance.
*   `--db-name PrimaryUserDB`: The logical name of the database connection as defined in your MCP Server configuration.
*   `--output schema.json`: Dumps the discovered schema details into a JSON file for review.

**Example `schema.json` Output Snippet:**

```json
{
  "databaseName": "PrimaryUserDB",
  "tables": [
    {
      "tableName": "Users",
      "columns": [
        {"columnName": "UserId", "dataType": "uniqueidentifier", "isPrimaryKey": true, "isNullable": false},
        {"columnName": "Username", "dataType": "nvarchar(100)", "isPrimaryKey": false, "isNullable": false},
        {"columnName": "Email", "dataType": "nvarchar(255)", "isPrimaryKey": false, "isNullable": true},
        {"columnName": "CreationDate", "dataType": "datetime2", "isPrimaryKey": false, "isNullable": false}
      ],
      "relationships": []
    },
    {
      "tableName": "Orders",
      "columns": [
        {"columnName": "OrderId", "dataType": "int", "isPrimaryKey": true, "isNullable": false},
        {"columnName": "UserId", "dataType": "uniqueidentifier", "isPrimaryKey": false, "isNullable": false},
        {"columnName": "OrderDate", "dataType": "datetime2", "isPrimaryKey": false, "isNullable": false},
        {"columnName": "TotalAmount", "dataType": "decimal(18,2)", "isPrimaryKey": false, "isNullable": false}
      ],
      "relationships": [
        {"fromTable": "Orders", "fromColumn": "UserId", "toTable": "Users", "toColumn": "UserId", "relationshipType": "many-to-one"}
      ]
    }
  ]
}
```

This JSON output provides a structured view of your tables, columns, data types, and relationships, which can be fed back into your development process or used by AI models for more informed query generation.

## Practical Querying with MCP Server APIs

Once MCP Server is configured and has a grasp of your schema, your applications can interact with it to perform queries. This can be through a dedicated MCP SDK or via a REST API provided by the MCP Server.

### .NET SDK Example

Assuming you have the `Microsoft.ClaudeCode.MCP.SDK` NuGet package installed:

```csharp
using Microsoft.ClaudeCode.MCP.SDK.Models;
using Microsoft.ClaudeCode.MCP.SDK.Services;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public class DatabaseQueryService
{
    private readonly IMcpQueryService _mcpQueryService;

    public DatabaseQueryService(IMcpQueryService mcpQueryService)
    {
        _mcpQueryService = mcpQueryService ?? throw new ArgumentNullException(nameof(mcpQueryService));
    }

    public async Task<IEnumerable<dynamic>> GetRecentOrdersByUser(string userId)
    {
        // Using natural language query
        var queryRequest = new QueryRequest
        {
            DatabaseName = "PrimaryUserDB",
            Query = $"Show me all orders for user '{userId}' placed in the last 7 days, including the order date and total amount.",
            // Explicitly ask for structured output if needed, otherwise defaults to dynamic
            OutputFormat = OutputFormat.Json
        };

        var result = await _mcpQueryService.ExecuteQueryAsync(queryRequest);

        // The result is typically a collection of dynamic objects or a strongly typed list
        // depending on the OutputFormat and how the SDK deserializes it.
        // For simplicity, we return dynamic here.
        return result.Data as IEnumerable<dynamic>;
    }

    public async Task<IEnumerable<dynamic>> FindUsersByEmailDomain(string domain)
    {
        // Using a more structured natural language query for specific fields
        var queryRequest = new QueryRequest
        {
            DatabaseName = "PrimaryUserDB",
            Query = $"Find all users whose email addresses end with '@{domain}'. Return their username and email.",
            OutputFormat = OutputFormat.Json
        };

        var result = await _mcpQueryService.ExecuteQueryAsync(queryRequest);
        return result.Data as IEnumerable<dynamic>;
    }

    // Example of more direct query if needed, though natural language is preferred
    public async Task<IEnumerable<dynamic>> GetUserById(string userId)
    {
        var queryRequest = new QueryRequest
        {
            DatabaseName = "PrimaryUserDB",
            Query = $"SELECT UserId, Username, Email FROM Users WHERE UserId = '{userId}'", // Direct SQL for specificity
            QueryType = QueryType.Sql // Indicate this is raw SQL
        };

        var result = await _mcpQueryService.ExecuteQueryAsync(queryRequest);
        return result.Data as IEnumerable<dynamic>;
    }
}

// In your ASP.NET Core Startup.cs or Program.cs:
// services.AddScoped<IMcpQueryService, McpQueryService>();
// Make sure McpQueryService is registered correctly with the base URL of your MCP Server.
```

### Java SDK Example (Spring Boot)

Assuming you have the `io.github.claude-code:mcp-spring-boot-starter` Maven dependency:

```java
import io.github.claude_code.mcp.sdk.model.QueryRequest;
import io.github.claude_code.mcp.sdk.model.QueryResponse;
import io.github.claude_code.mcp.sdk.service.McpQueryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class DatabaseQueryService {

    private final McpQueryService mcpQueryService;

    @Autowired
    public DatabaseQueryService(McpQueryService mcpQueryService) {
        this.mcpQueryService = mcpQueryService;
    }

    public List<Map<String, Object>> getRecentOrdersByUser(String userId) {
        // Using natural language query
        QueryRequest queryRequest = QueryRequest.builder()
                .databaseName("PrimaryUserDB")
                .query(String.format("Show me all orders for user '%s' placed in the last 7 days, including the order date and total amount.", userId))
                .outputFormat("json") // Using string for enum compatibility if needed
                .build();

        QueryResponse response = mcpQueryService.executeQuery(queryRequest);

        // The response.data is typically a List of Maps (representing rows)
        return (List<Map<String, Object>>) response.getData();
    }

    public List<Map<String, Object>> findUsersByEmailDomain(String domain) {
        // Using a more structured natural language query for specific fields
        QueryRequest queryRequest = QueryRequest.builder()
                .databaseName("PrimaryUserDB")
                .query(String.format("Find all users whose email addresses end with '@%s'. Return their username and email.", domain))
                .outputFormat("json")
                .build();

        QueryResponse response = mcpQueryService.executeQuery(queryRequest);
        return (List<Map<String, Object>>) response.getData();
    }

    // Example of more direct query if needed
    public List<Map<String, Object>> getUserById(String userId) {
        QueryRequest queryRequest = QueryRequest.builder()
                .databaseName("PrimaryUserDB")
                .query("SELECT UserId, Username, Email FROM Users WHERE UserId = '" + userId + "'")
                .queryType("Sql") // Indicate this is raw SQL
                .build();

        QueryResponse response = mcpQueryService.executeQuery(queryRequest);
        return (List<Map<String, Object>>) response.getData();
    }
}

// In your Spring Boot application:
// The starter dependency will auto-configure McpQueryService bean.
// Ensure your application.properties has the MCP and Claude API configurations.
```

## Architectural Patterns and Considerations

MCP Server is not just a tool; it's a component that can influence your application's architecture.

### Adaptive Data Access Layer

Instead of tightly coupled ORM mappings, you can build a more adaptive data access layer.

*   **Decoupling:** Your business logic doesn't need to know the exact table names or column names. It can query based on intent. For example, "Get customer details" instead of `dbContext.Customers.Find(customerId)`.
*   **Schema Evolution:** When your database schema changes (e.g., a column is renamed, or a new table is added), the impact on applications using MCP Server for natural language queries can be minimized. MCP Server's introspection and AI can adapt, or you can update the natural language prompts to reflect the changes.
*   **Dynamic Reporting:** For systems that require flexible ad-hoc reporting, MCP Server can empower users (or other systems) to query data without pre-defined report templates.

### Abstraction and Composition

MCP Server can act as an abstraction layer not just for a single database, but potentially for multiple data sources.

*   **Multi-Database Federation:** While this chapter focuses on one DB per MCP Server instance for clarity, you could architect a system where multiple MCP Server instances, each connected to different databases (e.g., SQL Server for users, Cosmos DB for product catalogs), are orchestrated. A higher-level orchestrator could then translate complex, cross-database queries.
*   **AI-Assisted Data Integration:** By introspecting multiple schemas, MCP Server can assist in identifying potential join paths or data overlaps between different databases, aiding in data integration efforts.

### Security and Access Control

When using MCP Server, consider how you manage access to your databases.

*   **Service Account Best Practices:** The connection strings used by MCP Server should employ service accounts with the principle of least privilege. Avoid using highly privileged accounts.
*   **Azure AD Integration:** If your Azure SQL Database or Azure PostgreSQL supports Azure AD authentication, leverage it for MCP Server connections. This integrates with Azure's identity management.
*   **Network Security:** Deploy MCP Server within a Virtual Network (VNet) and use Azure Network Security Groups (NSGs) to restrict access to only authorized application servers.
*   **API Gateway:** For external access to MCP Server's API, consider an Azure API Management instance to handle authentication, rate limiting, and authorization.

### Performance Tuning and Caching

*   **Schema Caching:** MCP Server's schema caching is critical for performance. Ensure `SchemaRefreshIntervalMinutes` is set appropriately. Too frequent refreshes add overhead; too infrequent may miss schema changes.
*   **Query Caching:** Explore if MCP Server or the underlying SDK offers query result caching for frequently executed, non-volatile queries.
*   **AI Model Latency:** Be mindful of the latency introduced by the AI model when generating queries. For high-throughput, low-latency scenarios, consider when direct SQL queries via MCP (with `QueryType.Sql`) might be more appropriate.

## Common Pitfalls and How to Avoid Them

### Anti-patterns

*   **Over-reliance on AI for Critical Operations:** Using natural language queries for highly sensitive, strict data operations (e.g., financial transactions, critical system updates) can be risky. The AI might misinterpret intent, especially with ambiguous phrasing.
    *   **Why it's wrong:** AI is probabilistic. For operations where exactness is paramount and the cost of error is high, deterministic methods (like strongly typed ORM queries or precise SQL) are superior.
    *   **How to avoid:** Reserve natural language querying for data exploration, reporting, and less critical data retrieval. For critical operations, use explicit, well-tested code.
*   **Ignoring Schema Drift:** Disabling `SchemaDiscoveryEnabled` or setting `SchemaRefreshIntervalMinutes` to extremely long values (or `0` without manual re-triggering) when the schema is dynamic.
    *   **Why it's wrong:** MCP Server's AI relies on an accurate schema representation. If the schema drifts significantly, its query generation capabilities will degrade, leading to incorrect queries or errors.
    *   **How to avoid:** Implement a strategy for schema monitoring and automated refreshes. If your schema changes frequently due to CI/CD, schedule schema refreshes in MCP Server after deployments.
*   **Exposing Raw Connection Strings in Client Code:** Embedding sensitive database credentials directly in client-side application code or insecure configuration files accessible to the client.
    *   **Why it's wrong:** This is a major security vulnerability. Connection strings often contain usernames, passwords, and server details that, if compromised, give attackers direct access to your database.
    *   **How to avoid:** Always use secure configuration management for MCP Server. For Azure, leverage Azure Key Vault to store secrets. Ensure MCP Server itself runs with appropriate credentials and that client applications communicate with MCP Server's API securely (e.g., via HTTPS and authentication).

### Performance Bottlenecks

*   **Complex Natural Language Queries:** While powerful, extremely verbose or ambiguous natural language queries can lead to longer processing times by the AI model and potentially inefficient SQL generation.
    *   **How to avoid:** Encourage users and developers to be as specific as possible in their natural language prompts. If a query is consistently problematic, consider refining the prompt or using a more structured query approach if necessary.
*   **Frequent Schema Scans:** Setting `SchemaRefreshIntervalMinutes` too low for databases that are rarely modified can introduce unnecessary load on MCP Server and the database.
    *   **How to avoid:** Tune the refresh interval based on the actual rate of schema changes in your databases.

## Conclusion

MCP Server, integrated with Claude Code, offers a transformative approach to database interaction. By enabling sophisticated AI-driven querying and providing robust schema introspection, it empowers developers to build more intelligent, adaptive, and user-friendly data-centric applications. By understanding its architecture, configuring it correctly, and being mindful of common pitfalls, you can effectively leverage MCP Server to elevate your .NET and Java applications on Azure.
