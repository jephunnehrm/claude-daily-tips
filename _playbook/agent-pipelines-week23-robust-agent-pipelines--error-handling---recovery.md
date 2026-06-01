---
layout: chapter
title: "Robust Agent Pipelines: Error Handling & Recovery"
date: 2026-06-01
series: "agent-pipelines"
series_name: "Agent Pipelines and Orchestration"
week: 23
summary: "This chapter delves into advanced strategies for error handling, retries, and recovery mechanisms within agent pipelines, ensuring resilience and reliability for complex AI-driven workflows. We'll explore architectural patterns and practical implementation techniques for .NET and Java on Azure AI."
image: "/claude-daily-tips/assets/images/chapter-agent-pipelines-week23.jpg"
tags:
  - claude-code
  - mcp
  - dotnet
  - azure
  - agents
  - architecture
  - csharp
  - java
  - spring
  - rag
  - productivity
---



![Robust Agent Pipelines: Error Handling & Recovery](/claude-daily-tips/assets/images/chapter-agent-pipelines-week23.jpg)



# Agent Pipelines and Orchestration: Error Handling, Retries, and Recovery Strategies

As developers building sophisticated agent pipelines, we know that the promise of AI-driven automation is only as strong as its reliability. Transient network issues, API rate limits, unexpected model outputs, or downstream service failures are not exceptions but rather inevitable occurrences. Ignoring robust error handling, retry, and recovery strategies is a direct path to brittle, unreliable systems. This chapter equips you with the architectural insights and practical techniques to build agent pipelines that can gracefully handle failures and recover autonomously.

## TL;DR

*   **Idempotency is Key:** Design agents and their operations to be idempotent to safely retry without unintended side effects.
*   **Layered Retry Strategies:** Implement retries at multiple levels (agent, orchestration, and service) with exponential backoff and jitter.
*   **Circuit Breakers and Timeouts:** Employ circuit breakers to prevent cascading failures and judicious timeouts to bound execution.
*   **Structured Logging & Monitoring:** Comprehensive, structured logging is critical for diagnosing failures and informing recovery strategies.
*   **Dead-Letter Queues & Manual Intervention:** Establish mechanisms for unrecoverable errors, such as dead-letter queues, for later analysis and potential manual intervention.

## The Cost of Failure in Agent Pipelines

In a typical agent pipeline, a failure in one step can have a ripple effect. Imagine a multi-agent workflow:

1.  **Data Ingestion Agent:** Fetches data from an external source.
2.  **Data Validation Agent:** Checks the ingested data for integrity.
3.  **Analysis Agent:** Processes validated data using an LLM (e.g., Claude).
4.  **Report Generation Agent:** Compiles results into a report.
5.  **Notification Agent:** Alerts stakeholders about the report.

If the **Analysis Agent** times out due to a temporary Azure OpenAI service overload, the entire pipeline halts. Without proper handling, this might result in:

*   **Lost Work:** Data might not be processed, requiring manual re-initiation.
*   **User Frustration:** End-users waiting for a report get nothing.
*   **Cascading Failures:** Downstream systems that depend on timely reports might also fail.
*   **Increased Operational Overhead:** Developers and SREs spend time debugging and manually recovering.

Our goal is to transform such a brittle pipeline into a resilient one that can self-heal or provide clear diagnostics for efficient human intervention.

## Architectural Principles for Resilient Pipelines

Before diving into code, let's establish core architectural principles:

### 1. Idempotency: The Foundation of Retries

An idempotent operation is one that can be performed multiple times without changing the result beyond the initial application. In agent pipelines, this is paramount for retries. If an agent performs an action (e.g., saving a record to a database) and then fails, retrying that same action should not create duplicate records or corrupt data.

**How to Achieve Idempotency:**

*   **Unique Request IDs:** Each operation can be tagged with a unique identifier. Before performing an action, check if an operation with that ID has already been successfully completed.
*   **State Management:** Agents should maintain state. If an agent restarts or retries, it should know where it left off and what has already been accomplished.
*   **Transactional Operations:** For database interactions, use transactions to ensure atomicity.
*   **Idempotency Keys in APIs:** Many external services (like Azure Cosmos DB, Azure Service Bus) support idempotency keys. Leverage these where available.

### 2. Layered Retry Strategies

Retries shouldn't be a one-size-fits-all approach. They should be applied judiciously at different levels:

*   **Agent-Level Retries:** Individual agents might have internal mechanisms to retry operations against specific services (e.g., retrying an LLM call a few times).
*   **Orchestration-Level Retries:** The orchestrator (e.g., a custom .NET/Java application, or a future MCP orchestrator) should manage retries for entire agent tasks or sequences of tasks.
*   **Infrastructure/SDK-Level Retries:** Many SDKs (e.g., Azure SDKs for .NET/Java) provide built-in retry policies. Configure these to align with your overall strategy.

**Key Retry Policy Components:**

*   **Max Retries:** A hard limit on the number of attempts.
*   **Backoff Strategy:** How long to wait between retries.
    *   **Fixed Delay:** Simple but can lead to "thundering herd" issues.
    *   **Exponential Backoff:** Wait times increase exponentially (e.g., 1s, 2s, 4s, 8s). This is generally preferred.
    *   **Jitter:** Randomness added to the backoff delay (e.g., +/- 20% of the calculated delay). This further prevents synchronized retries from overwhelming a struggling service.

### 3. Circuit Breakers and Timeouts

*   **Timeouts:** Every external call (API, database, LLM) must have a timeout. This prevents an agent from hanging indefinitely while waiting for a response, consuming resources and blocking the pipeline.
*   **Circuit Breakers:** A pattern where, after a certain number of consecutive failures, a service call is "short-circuited" – subsequent calls fail immediately without attempting the actual operation. After a configurable timeout, the circuit breaker enters a "half-open" state, allowing a few test calls. If successful, the circuit closes; if not, it opens again. This protects the upstream service from being overloaded and allows it to recover.

### 4. Structured Logging and Monitoring

Robust logging is not optional. It's the primary tool for understanding *why* something failed and *what* happened during retries.

*   **Contextual Information:** Log details like agent name, operation ID, attempt number, error type, and relevant input/output snippets.
*   **Correlation IDs:** Use a correlation ID to trace a single pipeline execution across multiple agents and services.
*   **Structured Formats:** Log in structured formats (e.g., JSON) for easier parsing and analysis by monitoring tools.
*   **Metrics:** Instrument your pipeline with metrics for failure rates, retry counts, latency, and circuit breaker states.

### 5. Dead-Letter Queues (DLQs) and Recovery

Not all failures can be automatically resolved with retries. For operations that consistently fail after exhausting retry attempts, a Dead-Letter Queue (DLQ) is essential.

*   **Purpose:** Messages or tasks that fail persistently are moved to a DLQ. This prevents them from blocking other pipeline executions and allows for later inspection.
*   **Recovery:** A separate process or team can monitor the DLQ, analyze the failed items, and either:
    *   Manually correct the data and re-queue the item.
    *   Update the agent logic to handle the specific failure mode.
    *   Discard the item if it's deemed unrecoverable.

## Practical Implementation Patterns

Let's explore how to implement these principles using .NET and Java on Azure, with Claude Code for agent logic.

### Example Scenario: LLM Analysis Agent with Retries

We'll consider an agent responsible for calling an LLM (e.g., Azure OpenAI's Claude integration via an SDK).

#### .NET Implementation

We'll use `Microsoft.Extensions.Http.Resilience` for sophisticated retry and circuit breaker policies, integrating with Azure OpenAI.

**1. Project Setup:**

Ensure you have the necessary NuGet packages:
```bash
dotnet add package Azure.AI.OpenAI
dotnet add package Microsoft.Extensions.Http.Resilience
dotnet add package Microsoft.Extensions.Http.Polly # Older, still relevant for some integrations
dotnet add package Microsoft.Extensions.DependencyInjection
```

**2. Configuration (appsettings.json):**

```json
{
  "AzureOpenAI": {
    "Endpoint": "YOUR_AZURE_OPENAI_ENDPOINT",
    "Deployments": {
      "Claude": "YOUR_CLAUDE_DEPLOYMENT_NAME"
    }
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.Extensions.Http.Resilience": "Information"
    }
  }
}
```

**3. Program.cs (Service Registration):**

```csharp
using Azure.AI.OpenAI;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using System.Net.Http;
using Microsoft.Extensions.Options;
using Polly;
using Polly.Contrib.HttpClient; // For M.E.Http.Resilience
using System;

// Define agent interfaces and implementations later
interface IAnalysisAgent
{
    Task<string> AnalyzeAsync(string text);
}

class AzureOpenAIAnalysisAgent : IAnalysisAgent
{
    private readonly OpenAIClient _client;
    private readonly string _deploymentName;
    private readonly ILogger<AzureOpenAIAnalysisAgent> _logger;

    public AzureOpenAIAnalysisAgent(OpenAIClient client, IOptions<AzureOpenAIConfig> config, ILogger<AzureOpenAIAnalysisAgent> logger)
    {
        _client = client;
        _deploymentName = config.Value.Deployments.Claude;
        _logger = logger;
    }

    public async Task<string> AnalyzeAsync(string text)
    {
        _logger.LogInformation("Starting analysis for text snippet.");

        // Example: Calling Claude 3 Sonnet
        var chatCompletionsOptions = new ChatCompletionsOptions()
        {
            DeploymentName = _deploymentName,
            Messages =
            {
                new ChatRequestMessage(ChatRole.System, "You are a helpful assistant that summarizes text."),
                new ChatRequestMessage(ChatRole.User, $"Summarize the following: {text}"),
            },
            MaxTokens = 150,
            Temperature = 0.7f,
        };

        try
        {
            Response<ChatCompletions> response = await _client.GetChatCompletionsAsync(chatCompletionsOptions);
            if (response.Value.Choices.Count > 0)
            {
                _logger.LogInformation("Analysis successful.");
                return response.Value.Choices[0].Message.Content;
            }
            else
            {
                _logger.LogError("No choices returned from LLM.");
                throw new InvalidOperationException("LLM returned no valid choices.");
            }
        }
        catch (RequestFailedException ex)
        {
            _logger.LogError(ex, "Azure OpenAI request failed for analysis. Status: {StatusCode}", ex.Status);
            // Re-throw or handle specific status codes (e.g., 429 for rate limiting)
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "An unexpected error occurred during analysis.");
            throw;
        }
    }
}

// Configuration class
public class AzureOpenAIConfig
{
    public string Endpoint { get; set; }
    public DeploymentsConfig Deployments { get; set; }
}

public class DeploymentsConfig
{
    public string Claude { get; set; }
}

public class Program
{
    public static void Main(string[] args)
    {
        var host = Host.CreateDefaultBuilder(args)
            .ConfigureAppConfiguration((hostingContext, config) =>
            {
                config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
            })
            .ConfigureServices((context, services) =>
            {
                // Configuration Binding
                services.Configure<AzureOpenAIConfig>(context.Configuration.GetSection("AzureOpenAI"));
                services.AddSingleton(cfg => new OpenAIClient(cfg.GetRequiredService<IOptions<AzureOpenAIConfig>>().Value.Endpoint));

                // Resilience Policies
                var resilienceConfig = context.Configuration.GetSection("Resilience");
                var policyRegistry = services.AddPolicyRegistry();

                // Define retry policy for OpenAI calls
                var retryPolicy = Policy
                    .Handle<RequestFailedException>(ex => ex.Status == 429 || ex.Status == 503) // Retry on rate limits or service unavailable
                    .WaitAndRetryAsync(
                        retryCount: 5,
                        // Exponential backoff with jitter
                        sleepDurationProvider: (attempt, context) => TimeSpan.FromSeconds(Math.Pow(2, attempt) + Random.Shared.Next(0, 1000) / 1000.0),
                        onRetry: (exception, timeSpan, attempt, context) =>
                        {
                            var logMsg = $"Retry {attempt} for {context.OperationKey} due to {exception.Message}. Waiting {timeSpan.TotalSeconds:F2}s.";
                            context.Logger?.LogWarning(logMsg);
                        });

                // Define circuit breaker policy
                var circuitBreakerPolicy = Policy
                    .Handle<RequestFailedException>(ex => ex.Status >= 400 && ex.Status != 401 && ex.Status != 403) // Break on client errors (except auth) and server errors
                    .CircuitBreakerAsync(
                        exceptionsAllowedBeforeBreaking: 3, // Number of consecutive failures to break the circuit
                        durationOfBreak: TimeSpan.FromMinutes(1), // Duration to keep the circuit broken
                        onBreak: (exception, breakDelay, context) =>
                        {
                            var logMsg = $"Circuit breaker opened for {context.OperationKey} due to {exception.Message}. Breaking for {breakDelay.TotalSeconds:F2}s.";
                            context.Logger?.LogError(logMsg);
                        },
                        onReset: (context) =>
                        {
                            context.Logger?.LogInformation($"Circuit breaker reset for {context.OperationKey}.");
                        },
                        onHalfOpen: () =>
                        {
                            context.Logger?.LogInformation($"Circuit breaker half-open for {context.OperationKey}.");
                        });

                // Combine policies (e.g., retry then break)
                var combinedPolicy = retryPolicy.WrapAsync(circuitBreakerPolicy);

                policyRegistry.Register("OpenAIRetryAndBreak", combinedPolicy);

                // Register HttpClient with the policy
                services.AddHttpClient("OpenAIClient")
                    .AddPolicyHandler(policyRegistry.Get<IAsyncPolicy>("OpenAIClientRetryAndBreak"));
                    // Note: The above line is for M.E.Http.Polly.
                    // For M.E.Http.Resilience, it would be more direct:
                    // .AddResilienceHandler("OpenAIClientRetryAndBreak", builder => builder.AddRetry(...) .AddCircuitBreaker(...));

                // Register the agent
                services.AddScoped<IAnalysisAgent, AzureOpenAIAnalysisAgent>();

                // Example of how an orchestrator might use it:
                services.AddHostedService<PipelineOrchestratorService>();
            })
            .Build();

        host.Run();
    }
}

// Dummy Orchestrator Service for demonstration
public class PipelineOrchestratorService : BackgroundService
{
    private readonly IAnalysisAgent _analysisAgent;
    private readonly ILogger<PipelineOrchestratorService> _logger;
    private readonly IServiceProvider _serviceProvider; // For accessing policies

    public PipelineOrchestratorService(IAnalysisAgent analysisAgent, ILogger<PipelineOrchestratorService> logger, IServiceProvider serviceProvider)
    {
        _analysisAgent = analysisAgent;
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var textToAnalyze = "This is a sample text that needs summarization. The LLM should process this efficiently.";

        _logger.LogInformation("Pipeline started. Attempting analysis.");

        var policyRegistry = _serviceProvider.GetRequiredService<IPolicyRegistry<string>>();
        var analysisPolicy = policyRegistry.Get<IAsyncPolicy>("OpenAIRetryAndBreak");

        try
        {
            // Using the policy directly on the agent method
            var result = await analysisPolicy.ExecuteAsync(async () =>
            {
                // This context is useful for logging within Polly's onRetry/onBreak
                var context = new Context($"AnalyzeText_{Guid.NewGuid()}");
                context.Logger = _serviceProvider.GetRequiredService<ILogger<AzureOpenAIAnalysisAgent>>();
                return await _analysisAgent.AnalyzeAsync(textToAnalyze);
            }, new Context("AnalyzeText")); // Initial context for the operation

            _logger.LogInformation($"Analysis completed successfully. Result: {result}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Pipeline failed after multiple retries and circuit breaker activations.");
            // Handle persistent failure - e.g., send to DLQ, log for manual review
        }
    }
}

```

**Explanation:**

*   **`OpenAIClient` Registration:** We register the `OpenAIClient` with Azure OpenAI endpoint and deployment name.
*   **Resilience Policies:** We define two primary Polly policies:
    *   `retryPolicy`: Catches `RequestFailedException` with status codes 429 (rate limiting) and 503 (service unavailable). It uses exponential backoff with a random jitter.
    *   `circuitBreakerPolicy`: Catches any `RequestFailedException` (excluding authentication errors) and breaks the circuit after 3 consecutive failures.
*   **Combining Policies:** The `retryPolicy` is wrapped around the `circuitBreakerPolicy`. This means it will retry a few times before the circuit breaker is even considered.
*   **`HttpClient` Integration:** The `HttpClient` used to communicate with Azure OpenAI is configured to use the registered resilience policy.
*   **Agent Usage:** The `PipelineOrchestratorService` demonstrates how to fetch the policy from the `IPolicyRegistry` and execute the `AnalyzeAsync` method within its `ExecuteAsync` block. This ensures that the `AnalyzeAsync` call benefits from the configured retry and circuit breaker logic.

#### Java Implementation

We'll use Resilience4j for robust retry and circuit breaker patterns.

**1. Project Setup (Maven `pom.xml`):**

```xml
<dependencies>
    <!-- Azure OpenAI Client -->
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-ai-openai</artifactId>
        <version>1.0.0-beta.8</version> <!-- Use the latest stable version -->
    </dependency>

    <!-- Spring Boot Starter for Resilience4j -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot2-starter</artifactId>
        <version>1.7.1</version> <!-- Use the latest stable version -->
    </dependency>
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-circuitbreaker</artifactId>
        <version>1.7.1</version>
    </dependency>
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-retry</artifactId>
        <version>1.7.1</version>
    </dependency>

    <!-- Spring Boot Starter for logging -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

**2. Configuration (`application.yml`):**

```yaml
azure:
  openai:
    endpoint: ${AZURE_OPENAI_ENDPOINT:YOUR_AZURE_OPENAI_ENDPOINT}
    deployment-name: ${AZURE_OPENAI_CLAUDE_DEPLOYMENT:YOUR_CLAUDE_DEPLOYMENT_NAME}

resilience4j:
  retry:
    instances:
      openaiRetry:
        name: openaiRetry
        maxAttempts: 5
        waitDuration: 100ms # Initial wait, actual backoff is configured below
        retryExceptions:
          - com.azure.core.http.rest.RestException # Catch Azure SDK exceptions
        retryExceptionPredicate: | # Custom predicate for specific HTTP status codes
          exception -> {
              if (exception instanceof com.azure.core.http.rest.RestException) {
                  com.azure.core.http.rest.RestException restException = (com.azure.core.http.rest.RestException) exception;
                  // 429 Too Many Requests, 503 Service Unavailable
                  return restException.getResponse().getStatusCode() == 429 || restException.getResponse().getStatusCode() == 503;
              }
              return false;
          }
        exponentialBackoffMultiplier: 2
        exponentialBackoffRandomizationFactor: 0.3 # Jitter factor
  circuitbreaker:
    instances:
      openaiCircuitBreaker:
        name: openaiCircuitBreaker
        registerHealthIndicator: true
        failureRateThreshold: 50 # Percentage
        slowCallRateThreshold: 100 # Percentage
        slowCallDurationThreshold: 10s
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        permittedNumberOfCallsInHalfOpenState: 3
        waitDurationInOpenState: 1m
```

**3. Agent Implementation (`AnalysisAgent.java`):**

```java
package com.example.agents;

import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.models.ChatCompletions;
import com.azure.ai.openai.models.ChatCompletionsOptions;
import com.azure.ai.openai.models.ChatRequestMessage;
import com.azure.ai.openai.models.ChatRole;
import com.azure.core.exception.ClientAuthenticationException;
import com.azure.core.exception.ResourceNotFoundException;
import com.azure.core.exception.ServiceInvocationException;
import com.azure.core.http.rest.Response;
import com.azure.core.http.rest.RestException;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
@Slf4j
public class AnalysisAgent {

    private final OpenAIClient openAIClient;
    private final String deploymentName;

    public AnalysisAgent(OpenAIClient openAIClient, @Value("${azure.openai.deployment-name}") String deploymentName) {
        this.openAIClient = openAIClient;
        this.deploymentName = deploymentName;
    }

    // Apply Retry and CircuitBreaker annotations
    @Retry(name = "openaiRetry")
    @CircuitBreaker(name = "openaiCircuitBreaker")
    public String analyze(String text) {
        log.info("Attempting to analyze text: '{}'", text.substring(0, Math.min(text.length(), 50)) + "...");

        var chatCompletionsOptions = new ChatCompletionsOptions()
                .setDeploymentName(deploymentName)
                .setMessages(List.of(
                        new ChatRequestMessage(ChatRole.SYSTEM, "You are a helpful assistant that summarizes text."),
                        new ChatRequestMessage(ChatRole.USER, "Summarize the following: " + text)
                ))
                .setMaxTokens(150)
                .setTemperature(0.7f);

        try {
            Response<ChatCompletions> response = openAIClient.getChatCompletions(chatCompletionsOptions);

            if (response.getValue().getChoices() != null && !response.getValue().getChoices().isEmpty()) {
                String content = response.getValue().getChoices().get(0).getMessage().getContent();
                log.info("Analysis successful.");
                return content;
            } else {
                log.error("No choices returned from LLM for analysis.");
                throw new RuntimeException("LLM returned no valid choices.");
            }
        } catch (ClientAuthenticationException e) {
            log.error("Authentication error calling Azure OpenAI.", e);
            throw new RuntimeException("Authentication failed.", e);
        } catch (ResourceNotFoundException e) {
            log.error("Resource not found error calling Azure OpenAI.", e);
            throw new RuntimeException("Deployment or resource not found.", e);
        } catch (ServiceInvocationException e) {
            // This catches underlying HTTP errors from Azure SDK
            log.error("Service invocation error calling Azure OpenAI. Status code: {}", e.getStatusCode(), e);
            throw new RuntimeException("Service invocation failed.", e);
        } catch (RestException e) {
            // Resilience4j's retry and circuit breaker configurations will specifically look for this
            // based on statusCode in the yml.
            log.error("Azure OpenAI API returned an error. Status: {}. Body: {}", e.getResponse().getStatusCode(), e.getMessage(), e);
            throw e; // Re-throw to be caught by Resilience4j
        } catch (CallNotPermittedException e) {
            log.error("Circuit breaker is open. Call to analyze() is blocked.", e);
            throw e; // Re-throw to indicate the circuit breaker blocked the call
        } catch (Exception e) {
            log.error("An unexpected error occurred during analysis.", e);
            throw new RuntimeException("Unexpected analysis error.", e);
        }
    }
}
```

**4. Main Application (`AgentPipelineApplication.java`):**

```java
package com.example.agents;

import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.core.credential.AzureKeyCredential;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@Slf4j
public class AgentPipelineApplication implements CommandLineRunner {

    private final AnalysisAgent analysisAgent;

    public AgentPipelineApplication(AnalysisAgent analysisAgent) {
        this.analysisAgent = analysisAgent;
    }

    public static void main(String[] args) {
        SpringApplication.run(AgentPipelineApplication.class, args);
    }

    @Override
    public void run(String... args) {
        String textToAnalyze = "The market sentiment analysis indicates a bullish trend. Investors are optimistic about technology stocks.";
        log.info("Pipeline started. Attempting analysis.");

        try {
            String result = analysisAgent.analyze(textToAnalyze);
            log.info("Analysis completed successfully. Result: {}", result);
        } catch (Exception e) {
            log.error("Pipeline failed after retries and circuit breaker attempts.", e.getMessage());
            // Handle persistent failure: DLQ, manual review, etc.
        }
    }

    // Bean for OpenAIClient
    @Bean
    public OpenAIClient openAIClient(@Value("${azure.openai.endpoint}") String endpoint,
                                   @Value("${AZURE_OPENAI_KEY:YOUR_AZURE_OPENAI_KEY}") String apiKey) {
        return new OpenAIClientBuilder()
                .credential(new AzureKeyCredential(apiKey))
                .endpoint(endpoint)
                .build();
    }
}
```

**Explanation:**

*   **`application.yml`:** Configures Resilience4j's retry and circuit breaker instances.
    *   `openaiRetry`: Sets maximum attempts, initial wait, exception types to retry on, and uses exponential backoff with randomization (jitter).
    *   `openaiCircuitBreaker`: Configures thresholds for failure rate, slow calls, and wait times in the open state.
*   **`@Retry` and `@CircuitBreaker` Annotations:** These are applied directly to the `analyze` method in `AnalysisAgent`. Spring Boot and Resilience4j automatically wrap the method with the defined policies.
*   **Exception Handling:** The `analyze` method catches specific exceptions, logs them, and then re-throws them. This is crucial for Resilience4j to detect and act upon the failures (e.g., trigger a retry or open the circuit). `RestException` is explicitly caught and re-thrown for the retry policy to match.
*   **`CommandLineRunner`:** The `AgentPipelineApplication` implements `CommandLineRunner` to simulate a pipeline execution when the application starts. It calls the `analyze` method and logs the outcome.
*   **`OpenAIClient` Bean:** A Spring `@Bean` is defined for the `OpenAIClient`, configured with your Azure OpenAI endpoint and API key (preferably via environment variables).

### Claude Code CLI for Agent Logic

While the orchestrator and resilience policies are handled by .NET/Java, the core intelligence of an agent often resides in its prompts and potentially fine-tuned models. Claude Code CLI can be used to iterate on these.

**Example:** Developing an LLM prompt for an agent that needs to be particularly careful about error messages it generates.

```bash
claude messages create \
    --model "claude-3-opus-20240229" \
    --max-tokens 1024 \
    --temperature 0.7 \
    --system "You are an expert prompt engineer for AI agents. Your goal is to create prompts that guide the AI to handle errors gracefully and informatively, without being overly verbose or technical to a general user." \
    --message "System: You are an AI assistant processing user requests. Sometimes, requests fail due to external service issues or invalid input. When an error occurs, provide a user-friendly message. Examples:
User: 'Summarize this document.'
AI (Success): 'Here is your summary: [summary content]'
User: 'Translate this to French.'
AI (Temporary Issue): 'I'm having trouble accessing the translation service right now. Please try again in a few minutes.'
User: 'Process my order.'
AI (Invalid Input): 'I couldn't process your order because the product ID was invalid. Please check the ID and try again.'

Now, create a prompt for an agent that will analyze customer feedback and generate a concise sentiment report. This agent might fail if the feedback service is unavailable. Ensure the prompt guides the AI to produce a user-friendly error message in such cases." \
    --message "User: Write a prompt for the Customer Feedback Analysis Agent. The agent's task is to analyze provided feedback and output the sentiment (positive, negative, neutral) and a brief summary. If the underlying data source is unavailable, it should respond with 'I am currently unable to access the feedback data. Please check back later.'"

# Expected Output (example):
# System: You are an AI assistant designed to analyze customer feedback and report on sentiment.
# User: Analyze the following customer feedback:
# ---
# [Customer Feedback Text Here]
# ---
#
# Your task is to:
# 1. Determine the sentiment: Positive, Negative, or Neutral.
# 2. Provide a concise summary of the feedback.
#
# If you are unable to access the feedback data, respond ONLY with:
# "I am currently unable to access the feedback data. Please check back later."
#
# Expected Output Format:
# Sentiment: [Positive/Negative/Neutral]
# Summary: [Concise Summary]
```

This CLI interaction allows rapid prototyping of agent behaviors, including how they should respond to internal or external failures. This prompt can then be incorporated into the agent's logic in your .NET/Java application.

## Common Pitfalls and How to Avoid Them

*   **Overly Aggressive Retries:** Retrying too frequently or with too many attempts can exacerbate the problem, overwhelming the struggling service even further.
    *   **Avoidance:** Use exponential backoff with jitter and carefully tune retry counts based on the expected duration of transient issues. Monitor retry success rates.
*   **No Idempotency:** Retrying non-idempotent operations can lead to data duplication or corruption.
    *   **Avoidance:** Design every agent operation to be idempotent. Use unique IDs, check existing state, or leverage platform features for idempotency.
*   **Ignoring Specific Error Codes:** Treating all exceptions the same for retries can lead to retrying non-retryable errors (e.g., `400 Bad Request` due to malformed input).
    *   **Avoidance:** Configure retry policies to target specific transient error codes (e.g., 429, 5xx). Use predicates in your retry configuration.
*   **Lack of Visibility:** Not logging enough context or not having centralized monitoring makes debugging failures a nightmare.
    *   **Avoidance:** Implement structured, contextual logging. Use correlation IDs. Set up dashboards to monitor error rates, retry attempts, and circuit breaker states.
*   **Infinite Loops with Retries:** If an error is persistent and not properly handled by the retry policy or DLQ, the pipeline might get stuck in a retry loop.
    *   **Avoidance:** Ensure a finite `maxRetries` and a robust DLQ mechanism for persistent failures.

## Anti-patterns

*   **The "Fire and Forget" Agent:** Agents that perform critical operations without any retry logic or error reporting. If an external API fails, the operation is simply lost.
    *   **Why it's bad:** Leads to unreliable pipelines, lost data, and significant manual recovery effort.
*   **The "Retry Everything Always" Approach:** Applying a single, high-retry-count policy to all operations, including those that are not transient (e.g., authentication errors, invalid data).
    *   **Why it's bad:** Wastes resources, delays failure detection, and can mask underlying configuration or data issues. It might also exceed API rate limits unnecessarily.
*   **No Dead-Letter Queue:** When an agent consistently fails, it either halts the entire pipeline or logs an error and disappears, with no trace of what failed or why.
    *   **Why it's bad:** Lost visibility into failures. Difficult to diagnose systemic issues. Requires manual re-creation of failed tasks.

## Conclusion

Building resilient agent pipelines is not an afterthought; it's a core architectural responsibility. By embracing principles like idempotency, implementing layered retry strategies with appropriate backoff and jitter, employing circuit breakers, and ensuring comprehensive logging, you can construct AI-driven systems that are robust, self-healing, and dependable. When failures do occur, well-defined recovery mechanisms like Dead-Letter Queues ensure that no critical operation is truly lost. This proactive approach to error handling will be the hallmark of successful and scalable agent deployments on Azure AI and beyond.
