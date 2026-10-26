---
layout: chapter
title: "Multi-Agent Pipeline Design: Orchestrator & Sub-Agent Patterns"
date: 2026-10-26
series: "agent-pipelines"
series_name: "Agent Pipelines and Orchestration"
week: 44
summary: "This chapter explores advanced multi-agent pipeline design using orchestrator and sub-agent patterns, detailing their implementation with Claude Code and Azure AI. We'll cover practical code examples and architectural considerations for building robust agent systems."
image: "https://image.pollinations.ai/prompt/Dark%2C%20futuristic%20architectural%20blueprint%20of%20interconnected%20nodes%20and%20pathways%2C%20AI%20network%20diagram%20aesthetic?width=800&height=400&nologo=true&model=flux"
tags:
  - claude-code
  - agents
  - architecture
  - azure
  - dotnet
  - mcp
---



![Multi-Agent Pipeline Design: Orchestrator & Sub-Agent Patterns](https://image.pollinations.ai/prompt/Dark%2C%20futuristic%20architectural%20blueprint%20of%20interconnected%20nodes%20and%20pathways%2C%20AI%20network%20diagram%20aesthetic?width=800&height=400&nologo=true&model=flux)



## TL;DR

*   Understand the roles of Orchestrator and Sub-Agent patterns in complex agent pipelines.
*   Implement orchestrator-sub-agent communication using Claude Code's messaging and Azure AI services.
*   Design for scalability, fault tolerance, and testability in multi-agent systems.
*   Leverage Azure services like Azure OpenAI, Azure Functions, and Azure Service Bus for robust orchestration.

## Introduction to Multi-Agent Pipelines

As AI capabilities advance, the complexity of tasks that can be automated grows. Simple, monolithic agents are often insufficient for intricate workflows. Multi-agent systems, where specialized agents collaborate to achieve a common goal, offer a powerful paradigm. This chapter delves into two fundamental patterns for structuring these systems: the **Orchestrator** and **Sub-Agent** patterns. We will explore how to design and implement these patterns using Claude Code, .NET, Java, and Azure AI services.

The Orchestrator-Sub-Agent pattern establishes a clear hierarchy and division of labor. The Orchestrator acts as the central coordinator, managing the overall workflow, delegating tasks to specialized Sub-Agents, and aggregating their results. Sub-Agents are designed to perform specific, well-defined tasks, communicating their outcomes back to the Orchestrator. This modular approach enhances maintainability, testability, and scalability.

## The Orchestrator Pattern

The Orchestrator is the brain of the operation. Its primary responsibilities include:

*   **Workflow Management:** Defining and executing the sequence of operations.
*   **Task Delegation:** Identifying the appropriate Sub-Agent for a given task and sending it the necessary input.
*   **State Management:** Keeping track of the overall pipeline's progress and the results from each Sub-Agent.
*   **Error Handling & Retry Logic:** Implementing strategies to manage failures within Sub-Agents.
*   **Result Aggregation:** Combining or processing the outputs from multiple Sub-Agents to produce the final outcome.

For building an Orchestrator, we often leverage general-purpose programming languages and frameworks, enhanced with AI capabilities. Azure Functions or Azure Container Apps provide excellent serverless or containerized environments for hosting orchestrators. Communication between the Orchestrator and Sub-Agents can be achieved through various mechanisms, including direct API calls, message queues (like Azure Service Bus or Azure Queue Storage), or event grids.

### Orchestrator Implementation Example (.NET)

This example illustrates a conceptual .NET Orchestrator using `claude` CLI for agent interactions and Azure Service Bus for communication.

First, let's define a simple `Command` and `Result` structure for inter-agent communication.

```csharp
// Shared Project (e.g., Common/AgentCommunication.cs)
public record AgentCommand(string AgentId, string Operation, Dictionary<string, object> Parameters);
public record AgentResult(string AgentId, bool Success, object Output, string ErrorMessage);
```

Now, the Orchestrator, likely running as an Azure Function or a service:

```csharp
// Orchestrator Project (e.g., OrchestratorService/Orchestrator.cs)
using Azure.Messaging.ServiceBus;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

public class PipelineOrchestrator
{
    private readonly ServiceBusSender _commandSender;
    private readonly ServiceBusReceiver _resultReceiver;
    private readonly Dictionary<string, TaskCompletionSource<AgentResult>> _pendingTasks = new();
    private readonly string _orchestratorAgentId = "Orchestrator_001";

    public PipelineOrchestrator(string serviceBusConnectionString, string commandQueueName, string resultQueueName)
    {
        var client = new ServiceBusClient(serviceBusConnectionString);
        _commandSender = client.CreateSender(commandQueueName);
        _resultReceiver = client.CreateReceiver(resultQueueName);

        // Start listening for results
        _ = ListenForResultsAsync();
    }

    public async Task<TOutput> ExecuteSubAgentAsync<TOutput>(string subAgentId, string operation, object parameters)
    {
        var command = new AgentCommand(subAgentId, operation, ConvertToDictionary(parameters));
        var commandJson = JsonConvert.SerializeObject(command);
        var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(commandJson));

        var tcs = new TaskCompletionSource<AgentResult>();
        _pendingTasks[command.AgentId] = tcs; // Using AgentId as a unique identifier for now, might need a correlation ID

        await _commandSender.SendMessageAsync(message);
        Console.WriteLine($"Sent command to {subAgentId}: {operation}");

        var result = await tcs.Task;

        if (!result.Success)
        {
            throw new Exception($"Sub-agent {subAgentId} failed: {result.ErrorMessage}");
        }

        return (TOutput)result.Output;
    }

    private async Task ListenForResultsAsync()
    {
        while (true)
        {
            try
            {
                var receivedMessage = await _resultReceiver.ReceiveMessageAsync(maxWaitTime: TimeSpan.FromMinutes(5));
                if (receivedMessage == null) continue;

                var body = receivedMessage.Body.ToString();
                var agentResult = JsonConvert.DeserializeObject<AgentResult>(body);

                if (_pendingTasks.TryGetValue(agentResult.AgentId, out var tcs))
                {
                    tcs.SetResult(agentResult);
                    _pendingTasks.Remove(agentResult.AgentId);
                }
                else
                {
                    Console.WriteLine($"Received result for unknown/completed task: {agentResult.AgentId}");
                }

                await _resultReceiver.CompleteMessageAsync(receivedMessage);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error listening for results: {ex.Message}");
                // Implement more robust error handling and dead-lettering logic
                await Task.Delay(TimeSpan.FromSeconds(5)); // Backoff
            }
        }
    }

    private Dictionary<string, object> ConvertToDictionary(object obj)
    {
        if (obj == null) return new Dictionary<string, object>();
        return obj.GetType().GetProperties()
                  .Where(pi => pi.CanRead)
                  .ToDictionary(pi => pi.Name, pi => pi.GetValue(obj, null));
    }

    // Example of starting the orchestrator logic
    public async Task RunPipelineAsync()
    {
        Console.WriteLine("Starting pipeline...");

        // Example: Step 1 - Get user query from an input source (not shown)
        var userQuery = "Summarize the latest advancements in AI for healthcare.";

        // Delegate to a 'QueryUnderstandingAgent'
        var queryAnalysis = await ExecuteSubAgentAsync<Dictionary<string, string>>(
            "QueryUnderstandingAgent_001",
            "AnalyzeQuery",
            new { Query = userQuery }
        );
        Console.WriteLine($"Query analysis: {JsonConvert.SerializeObject(queryAnalysis)}");

        // Delegate to a 'InformationRetrievalAgent'
        var documents = await ExecuteSubAgentAsync<List<string>>(
            "InformationRetrievalAgent_001",
            "RetrieveDocuments",
            new { Keywords = queryAnalysis["keywords"] }
        );
        Console.WriteLine($"Retrieved {documents.Count} documents.");

        // Delegate to a 'SummarizationAgent'
        var summary = await ExecuteSubAgentAsync<string>(
            "SummarizationAgent_001",
            "Summarize",
            new { ContentList = documents }
        );
        Console.WriteLine($"Final Summary: {summary}");

        Console.WriteLine("Pipeline finished.");
    }
}
```

To run this, you'll need:
1.  An Azure Service Bus namespace and two queues: `commands` and `results`.
2.  The `Azure.Messaging.ServiceBus` NuGet package.
3.  The `Newtonsoft.Json` NuGet package.
4.  A mechanism to launch `RunPipelineAsync` (e.g., an HTTP trigger for an Azure Function).

## The Sub-Agent Pattern

Sub-Agents are specialized workers. They are responsible for executing a single, well-defined task. Their key characteristics include:

*   **Single Responsibility:** Each Sub-Agent performs one type of operation (e.g., text summarization, data extraction, code generation).
*   **Clear Input/Output:** They expect specific input formats and produce predictable output formats.
*   **Communication Interface:** They expose a method or endpoint to receive commands and a mechanism to send results back.
*   **Idempotency (Desirable):** Ideally, Sub-Agents can be run multiple times with the same input and produce the same output, simplifying retry logic.

Sub-Agents are where we often integrate LLMs. Claude Code, through its CLI or SDKs, is a prime candidate for powering these agents. Azure Functions, Azure Container Apps, or even simple console applications can host Sub-Agents.

### Sub-Agent Implementation Example (Claude Code CLI)

This example shows a Sub-Agent that uses Claude Code for text analysis. It would listen on a message queue for commands and respond with results.

Assume a `QueryUnderstandingAgent` that analyzes a user query to extract keywords and intent.

**1. `claude` Configuration (`claude.yaml` or environment variables)**

```yaml
# For example, if you have a ~/.claude/config.yaml or want to set via env vars
# Ensure API keys, model preferences, etc., are configured.
# Example:
# api_key: "sk-..."
# default_model: "claude-3-opus-20240229"
```

**2. Sub-Agent Code (e.g., `QueryUnderstandingAgent/QueryUnderstandingAgent.cs`)**

This agent would be part of a service that listens to the `commands` queue.

```csharp
// QueryUnderstandingAgent Project (e.g., QueryUnderstandingAgent/AgentLogic.cs)
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Azure.Messaging.ServiceBus; // Assuming this agent also uses Service Bus

public class QueryUnderstandingAgent
{
    private readonly ServiceBusSender _resultSender;
    private readonly string _agentId = "QueryUnderstandingAgent_001"; // Must match Orchestrator's expectation

    public QueryUnderstandingAgent(string serviceBusConnectionString, string resultQueueName)
    {
        var client = new ServiceBusClient(serviceBusConnectionString);
        _resultSender = client.CreateSender(resultQueueName);
    }

    public async Task ProcessCommandAsync(AgentCommand command)
    {
        if (command.AgentId != _agentId || command.Operation != "AnalyzeQuery")
        {
            Console.WriteLine($"Ignoring command for agent {_agentId} with operation {command.Operation}");
            return;
        }

        Console.WriteLine($"Received command: AnalyzeQuery for '{command.Parameters.GetValueOrDefault("Query")}'");

        try
        {
            var query = command.Parameters["Query"].ToString();

            // Construct the prompt for Claude Code
            var prompt = $@"Analyze the following user query and extract:
1. Key keywords relevant to the topic.
2. The user's primary intent (e.g., 'information_seeking', 'task_completion', 'comparison').

Output your findings in JSON format with 'keywords' (an array of strings) and 'intent' (a single string) fields.

User Query: {query}";

            // Execute Claude Code CLI
            var claudeArgs = new List<string>
            {
                "completion",
                "--prompt", prompt,
                "--output-format", "json", // Request JSON output directly
                "--max-tokens", "200" // Adjust as needed
            };

            // Using ProcessStartInfo to run the claude CLI
            var psi = new ProcessStartInfo
            {
                FileName = "claude", // Assumes 'claude' is in PATH
                Arguments = string.Join(" ", claudeArgs),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (var process = Process.Start(psi))
            {
                string output = await process.StandardOutput.ReadToEndAsync();
                string error = await process.StandardError.ReadToEndAsync();
                await process.WaitForExitAsync();

                if (process.ExitCode != 0)
                {
                    throw new Exception($"Claude CLI failed with exit code {process.ExitCode}. Error: {error}");
                }

                // Parse the JSON output from Claude
                var analysisResult = JsonConvert.DeserializeObject<Dictionary<string, object>>(output);
                if (analysisResult == null || !analysisResult.ContainsKey("keywords") || !analysisResult.ContainsKey("intent"))
                {
                    throw new JsonException($"Claude output was not in the expected JSON format. Output: {output}");
                }

                var agentResult = new AgentResult(
                    AgentId: _agentId,
                    Success: true,
                    Output: new Dictionary<string, string>
                    {
                        {"keywords", string.Join(",", (List<object>)analysisResult["keywords"]).Replace("\"", "") }, // Simple conversion
                        {"intent", analysisResult["intent"].ToString()}
                    },
                    ErrorMessage: null
                );

                var resultJson = JsonConvert.SerializeObject(agentResult);
                var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(resultJson));
                await _resultSender.SendMessageAsync(message);
                Console.WriteLine($"Successfully analyzed query. Sent result for {_agentId}.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing command for {_agentId}: {ex.Message}");
            var agentResult = new AgentResult(
                AgentId: _agentId,
                Success: false,
                Output: null,
                ErrorMessage: ex.Message
            );
            var resultJson = JsonConvert.SerializeObject(agentResult);
            var message = new ServiceBusMessage(Encoding.UTF8.GetBytes(resultJson));
            await _resultSender.SendMessageAsync(message);
        }
    }
}
```

**Requirements:**
*   The `claude` executable must be installed and accessible in the system's PATH.
*   Appropriate Azure Service Bus connection string and queue names.
*   `Newtonsoft.Json` and `Azure.Messaging.ServiceBus` NuGet packages.

### Java Sub-Agent Example

A Java agent would follow a similar pattern, using the Claude Code CLI or SDK (if available) and an appropriate messaging library like JMS or Spring Cloud Stream for Azure Service Bus.

```java
// src/main/java/com/example/agents/QueryUnderstandingAgent.java
import com.azure.messaging.servicebus.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.TextNode;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeoutException;

// Assuming AgentCommand and AgentResult classes are defined and accessible
// (e.g., in a shared library or common package)

public class QueryUnderstandingAgent {

    private final ServiceBusSender resultSender;
    private final String agentId = "QueryUnderstandingAgent_001";
    private final ObjectMapper objectMapper = new ObjectMapper();

    public QueryUnderstandingAgent(String serviceBusConnectionString, String resultQueueName) {
        ServiceBusClient client = new ServiceBusClient(serviceBusConnectionString);
        this.resultSender = client.createSender(resultQueueName);
    }

    public void processCommand(AgentCommand command) {
        if (!command.getAgentId().equals(this.agentId) || !command.getOperation().equals("AnalyzeQuery")) {
            System.out.println("Ignoring command for agent " + this.agentId + " with operation " + command.getOperation());
            return;
        }

        System.out.println("Received command: AnalyzeQuery for '" + command.getParameters().get("Query") + "'");

        try {
            String query = (String) command.getParameters().get("Query");

            String prompt = String.format(
                "Analyze the following user query and extract:\n" +
                "1. Key keywords relevant to the topic.\n" +
                "2. The user's primary intent (e.g., 'information_seeking', 'task_completion', 'comparison').\n\n" +
                "Output your findings in JSON format with 'keywords' (an array of strings) and 'intent' (a single string) fields.\n\n" +
                "User Query: %s", query);

            // Execute Claude Code CLI
            List<String> claudeArgs = new ArrayList<>();
            claudeArgs.add("completion");
            claudeArgs.add("--prompt");
            claudeArgs.add(prompt);
            claudeArgs.add("--output-format");
            claudeArgs.add("json");
            claudeArgs.add("--max-tokens");
            claudeArgs.add("200");

            ProcessBuilder pb = new ProcessBuilder("claude", claudeArgs.toArray(new String[0]));
            pb.redirectErrorStream(true); // Merge stdout and stderr

            Process process = pb.start();
            StringBuilder outputBuilder = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    outputBuilder.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            String claudeOutput = outputBuilder.toString().trim();

            if (exitCode != 0) {
                throw new IOException("Claude CLI failed with exit code " + exitCode + ". Output: " + claudeOutput);
            }

            // Parse the JSON output from Claude
            JsonNode rootNode = objectMapper.readTree(claudeOutput);
            if (rootNode == null || !rootNode.has("keywords") || !rootNode.has("intent")) {
                throw new IOException("Claude output was not in the expected JSON format. Output: " + claudeOutput);
            }

            List<String> keywords = new ArrayList<>();
            if (rootNode.get("keywords").isArray()) {
                for (JsonNode keywordNode : (ArrayNode) rootNode.get("keywords")) {
                    if (keywordNode.isTextual()) {
                        keywords.add(keywordNode.asText());
                    }
                }
            }
            String intent = rootNode.get("intent").asText();

            Map<String, String> analysisResult = new HashMap<>();
            analysisResult.put("keywords", String.join(",", keywords));
            analysisResult.put("intent", intent);

            AgentResult agentResult = new AgentResult(
                this.agentId,
                true,
                analysisResult,
                null
            );

            String resultJson = objectMapper.writeValueAsString(agentResult);
            ServiceBusMessage message = new ServiceBusMessage(resultJson.getBytes(StandardCharsets.UTF_8));
            resultSender.sendMessage(message);
            System.out.println("Successfully analyzed query. Sent result for " + this.agentId);

        } catch (Exception e) {
            System.err.println("Error processing command for " + this.agentId + ": " + e.getMessage());
            e.printStackTrace();
            AgentResult agentResult = new AgentResult(
                this.agentId,
                false,
                null,
                e.getMessage()
            );
            try {
                String resultJson = objectMapper.writeValueAsString(agentResult);
                ServiceBusMessage message = new ServiceBusMessage(resultJson.getBytes(StandardCharsets.UTF_8));
                resultSender.sendMessage(message);
            } catch (Exception sendEx) {
                System.err.println("Failed to send error result: " + sendEx.getMessage());
            }
        }
    }
}
```

**Dependencies (Maven `pom.xml`)**:
*   `com.azure:azure-messaging-servicebus`
*   `com.fasterxml.jackson.core:jackson-databind`

## Communication Patterns

Choosing the right communication pattern is crucial for pipeline performance and reliability.

*   **Synchronous (e.g., direct HTTP calls):** Simple for tightly coupled agents but can lead to long-running requests and brittle dependencies.
*   **Asynchronous (Message Queues/Event Buses):** Decouples agents, improves resilience, and allows for scaling independently. Azure Service Bus is excellent for this. Orchestrators can post commands to a `commands` queue, and Sub-Agents consume from it. Sub-Agents post results to a `results` queue, consumed by the Orchestrator.
*   **Shared State (Databases/Caches):** Can be used for passing larger data blobs or complex state, but introduces potential concurrency issues and tight coupling to the data store.

For the Orchestrator-Sub-Agent pattern, asynchronous communication via message queues is generally preferred for robustness and scalability.

## Architectural Considerations

### Scalability

*   **Orchestrator:** Can be scaled by running multiple instances (e.g., as Azure Functions with scaling enabled or Kubernetes deployments). Ensure idempotency and handling of duplicate messages if scaling out.
*   **Sub-Agents:** Scale independently based on their workload. Azure Functions, Azure Container Apps, or worker services can automatically scale based on queue depth for message-driven agents.

### Fault Tolerance

*   **Retries:** Implement retry mechanisms for transient failures (network issues, temporary service unavailability). Message queues like Azure Service Bus offer built-in retry policies and dead-letter queues.
*   **Idempotency:** Design Sub-Agents to be idempotent so that retrying a failed operation doesn't cause unintended side effects.
*   **Circuit Breakers:** For synchronous calls or calls to external LLM APIs, implement circuit breaker patterns to prevent cascading failures.

### Monitoring and Observability

*   **Logging:** Centralized logging for all agents (Orchestrator and Sub-Agents) is essential for debugging. Azure Application Insights can aggregate logs.
*   **Tracing:** Distributed tracing helps visualize the flow of a request across multiple agents.
*   **Metrics:** Track key metrics like task completion times, error rates, and queue lengths to identify performance bottlenecks and issues.

## Anti-patterns

### 1. The "God" Orchestrator

**What it is:** An Orchestrator that becomes overly complex, handling too much logic, and knowing intimate details about many Sub-Agents. It tries to do too much, blurring the lines between orchestration and agent execution.

**Why it's bad:** This leads to a monolithic, hard-to-maintain system. Changes to Sub-Agent logic require changes to the Orchestrator, defeating the purpose of modularity. It becomes a single point of failure and a bottleneck for development.

**How to avoid:** Strictly define the Orchestrator's role: managing flow, delegation, and result aggregation. Keep agent-specific logic within the Sub-Agents. Use clear, abstract interfaces for communication.

### 2. Unreliable Communication Channels

**What it is:** Relying on simple, unreliable communication methods (e.g., direct HTTP calls without error handling, basic in-memory queues that disappear on restart) for inter-agent communication.

**Why it's bad:** This makes the system brittle. Message loss or delivery failures lead to pipeline failures that are hard to diagnose and recover from. It undermines the reliability and robustness that multi-agent systems aim to provide.

**How to avoid:** Use robust, managed messaging services like Azure Service Bus or Kafka. Implement proper error handling, acknowledgments, and dead-lettering for messages. Ensure agents can handle out-of-order or duplicate messages if necessary.

### 3. Ambiguous Agent Responsibilities

**What it is:** Sub-Agents that have overlapping responsibilities or are too general. For example, having a "Data Processor" agent that sometimes summarizes, sometimes extracts, and sometimes transforms.

**Why it's bad:** This leads to confusion, makes testing difficult, and hinders reusability. It's hard to guarantee consistency when an agent is responsible for multiple distinct tasks.

**How to avoid:** Adhere strictly to the Single Responsibility Principle. Each Sub-Agent should do one thing and do it well. If an agent's logic grows too complex, refactor it into smaller, more specialized agents.

## Conclusion

The Orchestrator-Sub-Agent pattern provides a robust and scalable framework for building complex AI-driven pipelines. By clearly defining roles and responsibilities, leveraging appropriate communication patterns, and paying attention to architectural considerations like fault tolerance and monitoring, developers can create sophisticated multi-agent systems using tools like Claude Code and Azure AI services. The modularity offered by this pattern significantly enhances the maintainability and evolution of AI applications.
