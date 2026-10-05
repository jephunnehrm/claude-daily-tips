---
layout: chapter
title: "Java Observability with Claude: Tracing LLM Interactions"
date: 2026-10-05
series: "java-and-claude"
series_name: "Java and Claude Code"
week: 41
summary: "This chapter explores integrating OpenTelemetry with Java applications, focusing on enriching traces with insights from Claude Code interactions and Azure AI services. Learn architectural patterns for building observable LLM-powered systems."
image: "/claude-daily-tips/assets/images/chapter-java-and-claude-week41.jpg"
tags:
  - java
  - claude-code
  - azure
  - mcp
  - devtools
  - architecture
---



![Java Observability with Claude: Tracing LLM Interactions](/claude-daily-tips/assets/images/chapter-java-and-claude-week41.jpg)



## Deep Dive: Java Observability with Claude Code and OpenTelemetry

As developers increasingly integrate Large Language Models (LLMs) like Claude into their Java applications, the need for robust observability becomes paramount. Understanding not just the performance of your application's core logic but also the behavior and cost of your LLM interactions is crucial for debugging, performance tuning, and capacity planning. This chapter provides a deep dive into leveraging OpenTelemetry for comprehensive observability of Java applications that interact with Claude Code and other Azure AI services. We'll cover architectural patterns, practical implementation details, and common pitfalls.

## TL;DR

*   **Integrate OpenTelemetry:** Instrument your Java applications to capture traces for both application logic and LLM interactions using the OpenTelemetry Java agent.
*   **Enrich LLM Spans:** Add custom attributes to OpenTelemetry spans to record crucial LLM context like prompts, responses, model used, and cost estimations.
*   **Azure AI Integration:** Utilize Azure AI services for LLM calls and configure OpenTelemetry to trace these interactions, sending data to backends like Azure Monitor.
*   **Architect for Observability:** Design your LLM integration layers with observability in mind, making it easy to add tracing and metrics.

## Why Observability for LLM Interactions?

Traditional application observability focuses on request latency, error rates, and resource utilization. However, LLM-powered applications introduce new dimensions:

*   **Prompt Engineering Effectiveness:** Understanding which prompts lead to successful (or unsuccessful) LLM responses.
*   **LLM Cost Management:** Tracking the number of tokens and LLM calls to manage operational expenses.
*   **Latency Decomposition:** Identifying whether latency is due to application processing, network calls to the LLM API, or the LLM's own inference time.
*   **Hallucination Detection:** While not directly observable, tracing can help correlate user input with problematic LLM outputs, aiding in debugging.
*   **Model Performance Drift:** Monitoring response quality and latency over time to detect changes in LLM behavior.

## Setting Up OpenTelemetry in Java

The most straightforward way to instrument Java applications for OpenTelemetry is by using the official OpenTelemetry Java agent. This agent automatically instruments many popular libraries and frameworks, including HTTP clients, database drivers, and frameworks like Spring.

### 1. Download the OpenTelemetry Java Agent

Obtain the latest `opentelemetry-javaagent.jar` from the [OpenTelemetry Java Instrumentation Releases](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases) page.

### 2. Launch Your Application with the Agent

Attach the agent to your Java Virtual Machine (JVM) using the `-javaagent` flag:

```bash
java -javaagent:/path/to/opentelemetry-javaagent.jar -jar your-application.jar
```

### 3. Configure the Exporter

By default, the agent might not export traces. You need to configure an exporter. For this chapter, we'll assume you're sending traces to Azure Monitor, which is a common choice for Azure-centric applications.

Create a configuration file (e.g., `otel-config.properties`) and specify the exporter. For Azure Monitor, you'll use the OTLP (OpenTelemetry Protocol) exporter pointing to the Azure Monitor Exporter endpoint.

```properties
# opentelemetry-config.properties
otel.exporter.otlp.endpoint=https://<YOUR_AZURE_MONITOR_COLLECTOR_ENDPOINT>/v1/traces
otel.exporter.otlp.protocol=grpc
otel.resource.attributes=service.name=<YOUR_SERVICE_NAME>,service.version=<YOUR_SERVICE_VERSION>
otel.metrics.exporter=none # Example: Disable metrics if only interested in traces
```

**Note on Azure Monitor Exporter:** For direct export to Azure Monitor, you typically use the Azure Monitor OpenTelemetry Exporter package which provides the necessary `applicationinsights-agent.jar` (which is an OpenTelemetry agent with Azure Monitor integration). If you're using a generic OTLP endpoint for an intermediary collector like the OpenTelemetry Collector or Azure Monitor Agent, the above configuration is valid. For simplicity and direct Azure integration, using the `applicationinsights-agent.jar` is often preferred.

Update your launch command to include the configuration file:

```bash
java -javaagent:/path/to/opentelemetry-javaagent.jar -Dotel.config.file=/path/to/otel-config.properties -jar your-application.jar
```

If using the Azure Monitor specific agent:

```bash
java -javaagent:/path/to/applicationinsights-agent.jar -jar your-application.jar
```

And configure Azure Monitor details via environment variables or `applicationinsights.json`:

```json
// applicationinsights.json
{
  "connectionString": "InstrumentationKey=YOUR_INSTRUMENTATION_KEY;IngestionEndpoint=YOUR_INGESTION_ENDPOINT",
  "instrumentation": {
    "java": {
      "enabled": true,
      "spring": {
        "enabled": true
      }
    }
  }
}
```

```bash
java -javaagent:/path/to/applicationinsights-agent.jar -Dapplicationinsights.configurationFile=/path/to/applicationinsights.json -jar your-application.jar
```

## Tracing Claude Code Interactions

Claude Code, like other LLMs, is typically accessed via HTTP APIs. The OpenTelemetry Java agent automatically instruments common HTTP clients (like Apache HttpClient, OkHttp, and the default `java.net.HttpURLConnection`). This means that calls to the Claude API endpoint will automatically generate spans.

However, these default spans are often generic and lack the specific context needed for LLM observability. We need to enrich these spans with LLM-specific attributes.

### 1. Identifying LLM HTTP Spans

You can usually identify LLM API calls by their URL or the target service. The OpenTelemetry agent captures the HTTP method, URL, and status code as attributes.

### 2. Adding Custom Attributes to Spans

To add custom attributes, you can use the OpenTelemetry SDK directly within your Java code. This requires adding the `opentelemetry-api` dependency to your project.

**Maven Dependency:**

```xml
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-api</artifactId>
    <version>1.33.0</version> <!-- Use the latest stable version -->
</dependency>
```

Now, let's look at a conceptual Java code snippet illustrating how to wrap an LLM call and add attributes. We'll assume you're using a common HTTP client library.

```java
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.MediaType;
import okhttp3.RequestBody;
import org.json.JSONObject;

import java.io.IOException;

public class ClaudeCodeService {

    // Assume OpenTelemetry is initialized and available (e.g., via agent auto-instrumentation or explicit setup)
    private static final OpenTelemetry openTelemetry = OpenTelemetry.get();
    private static final Tracer tracer = openTelemetry.getTracer("claude-code-instrumentation");

    private final OkHttpClient httpClient;
    private final String claudeApiEndpoint;
    private final String claudeApiKey;

    public ClaudeCodeService(OkHttpClient httpClient, String claudeApiEndpoint, String claudeApiKey) {
        this.httpClient = httpClient;
        this.claudeApiEndpoint = claudeApiEndpoint;
        this.claudeApiKey = claudeApiKey;
    }

    public String sendMessageToClaude(String prompt, String modelId) throws IOException {
        Span parentSpan = Span.current(); // Get the current span from the incoming request

        // Create a new span for the Claude API call
        Span span = tracer.spanBuilder("Claude API Call")
                          .setSpanKind(SpanKind.CLIENT)
                          .setParent(io.opentelemetry.context.Context.current().with(parentSpan)) // Link to parent request span
                          .setAttribute("llm.model.name", modelId)
                          .setAttribute("llm.prompt.text", prompt.substring(0, Math.min(prompt.length(), 500)) + "...") // Truncate long prompts
                          .startSpan();

        String responseBody = "";
        try (Scope scope = span.makeCurrent()) {
            JSONObject requestBodyJson = new JSONObject();
            requestBodyJson.put("model", modelId);
            requestBodyJson.put("max_tokens", 1000); // Example parameter
            requestBodyJson.put("messages", new JSONArray()
                .put(new JSONObject()
                    .put("role", "user")
                    .put("content", prompt)
                )
            );

            RequestBody body = RequestBody.create(requestBodyJson.toString(), MediaType.get("application/json; charset=utf-8"));

            Request request = new Request.Builder()
                .url(claudeApiEndpoint)
                .addHeader("x-api-key", claudeApiKey)
                .addHeader("anthropic-version", "2023-06-01") // Claude specific header
                .post(body)
                .build();

            try {
                Response response = httpClient.newCall(request).execute();
                if (!response.isSuccessful()) {
                    span.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "HTTP error " + response.code());
                    // Optionally add error details
                    if (response.body() != null) {
                         span.setAttribute("exception.message", response.body().string());
                    }
                    throw new IOException("Unexpected code " + response.code());
                }

                if (response.body() != null) {
                    responseBody = response.body().string();
                    JSONObject responseJson = new JSONObject(responseBody);
                    String completion = responseJson.getString("completion"); // Assuming Claude's response structure

                    // Add response attributes
                    span.setAttribute("llm.response.text", completion.substring(0, Math.min(completion.length(), 500)) + "..."); // Truncate
                    // You might extract token usage if available from response headers or body
                    // span.setAttribute("llm.usage.prompt_tokens", responseJson.getJSONObject("usage").getInt("prompt_tokens"));
                    // span.setAttribute("llm.usage.completion_tokens", responseJson.getJSONObject("usage").getInt("completion_tokens"));
                    // span.setAttribute("llm.usage.total_tokens", responseJson.getJSONObject("usage").getInt("total_tokens"));

                    span.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
                } else {
                    span.setStatus(io.opentelemetry.api.trace.StatusCode.OK); // Or ERROR if response body is expected
                }
            } catch (IOException e) {
                span.recordException(e);
                span.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "LLM API call failed");
                throw e;
            }
        } finally {
            span.end();
        }
        return responseBody;
    }

    // Example of how to use it within a Spring Boot controller or service
    // @Autowired
    // private ClaudeCodeService claudeCodeService;

    // public String processUserQuery(String query) throws IOException {
    //     // OpenTelemetry agent will automatically create a span for the incoming request
    //     // The span created in sendMessageToClaude will be a child of this span.
    //     return claudeCodeService.sendMessageToClaude(query, "claude-3-opus-20240229");
    // }
}
```

**Key takeaways from the code:**

*   **`tracer.spanBuilder(...)`**: Creates a new span.
*   **`setSpanKind(SpanKind.CLIENT)`**: Indicates this span represents an outgoing call.
*   **`setParent(...)`**: Crucially links the LLM span to the span representing the incoming request or the preceding application logic.
*   **`setAttribute(...)`**: Adds key-value pairs to the span. We've added `llm.model.name` and truncated `llm.prompt.text`.
*   **`llm.*` semantic convention**: While not fully standardized for LLMs across all observability platforms, using a prefix like `llm.` is a good practice for custom attributes related to LLM interactions. Official semantic conventions are evolving.
*   **Error Handling**: `span.setStatus(StatusCode.ERROR, ...)` and `span.recordException(e)` are vital for capturing failures.
*   **Token Usage**: If the LLM API response includes token usage, add these as attributes for cost tracking.

### Integrating with Azure AI Services

If you are using Azure OpenAI Service or other Azure AI services (e.g., Azure AI Search for RAG), the principles are the same. The primary difference is the endpoint and authentication mechanism.

For example, if you use the Azure OpenAI Java SDK:

```java
// Add dependency:
// <dependency>
//     <groupId>com.azure</groupId>
//     <artifactId>azure-ai-openai</artifactId>
//     <version>1.0.0-beta.13</version> <!-- Use the latest stable version -->
// </dependency>

import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.ai.openai.models.ChatCompletionsOptions;
import com.azure.ai.openai.models.ChatResponseMessage;
import com.azure.ai.openai.models.ChatMessage;
import com.azure.ai.openai.models.ChatRole;
import com.azure.core.credential.AzureKeyCredential;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

import java.util.Arrays;

public class AzureOpenAIService {

    private static final OpenTelemetry openTelemetry = OpenTelemetry.get();
    private static final Tracer tracer = openTelemetry.getTracer("azure-openai-instrumentation");

    private final OpenAIClient openAIClient;
    private final String deploymentName; // Equivalent to model name for Azure OpenAI

    public AzureOpenAIService(String endpoint, String apiKey, String deploymentName) {
        this.openAIClient = new OpenAIClientBuilder()
            .endpoint(endpoint)
            .credential(new AzureKeyCredential(apiKey))
            .build();
        this.deploymentName = deploymentName;
    }

    public String askQuestion(String question) {
        Span parentSpan = Span.current(); // Get the current span

        Span span = tracer.spanBuilder("Azure OpenAI API Call")
                          .setSpanKind(SpanKind.CLIENT)
                          .setParent(io.opentelemetry.context.Context.current().with(parentSpan))
                          .setAttribute("llm.provider", "azure")
                          .setAttribute("llm.model.name", deploymentName)
                          .setAttribute("llm.prompt.text", question.substring(0, Math.min(question.length(), 500)) + "...")
                          .startSpan();

        String responseContent = "";
        try (Scope scope = span.makeCurrent()) {
            ChatCompletionsOptions chatCompletionsOptions = new ChatCompletionsOptions(Arrays.asList(
                    new ChatMessage(ChatRole.USER, question)
            ))
            .setModel(deploymentName)
            .setMaxTokens(1000); // Example parameter

            try {
                com.azure.ai.openai.models.ChatCompletions chatCompletions = openAIClient.getChatCompletions(deploymentName, chatCompletionsOptions);

                if (chatCompletions != null && chatCompletions.getChoices() != null && !chatCompletions.getChoices().isEmpty()) {
                    ChatResponseMessage firstChoice = chatCompletions.getChoices().get(0).getMessage();
                    if (firstChoice != null && firstChoice.getContent() != null) {
                        responseContent = firstChoice.getContent();
                        span.setAttribute("llm.response.text", responseContent.substring(0, Math.min(responseContent.length(), 500)) + "...");

                        // Azure OpenAI also provides usage information
                        if (chatCompletions.getUsage() != null) {
                            span.setAttribute("llm.usage.prompt_tokens", chatCompletions.getUsage().getPromptTokens());
                            span.setAttribute("llm.usage.completion_tokens", chatCompletions.getUsage().getCompletionTokens());
                            span.setAttribute("llm.usage.total_tokens", chatCompletions.getUsage().getTotalTokens());
                        }

                        span.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
                    } else {
                        span.setStatus(io.opentelemetry.api.trace.StatusCode.OK); // Or ERROR if content is mandatory
                    }
                } else {
                    span.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
                }
            } catch (Exception e) {
                span.recordException(e);
                span.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "Azure OpenAI API call failed");
                throw e;
            }
        } finally {
            span.end();
        }
        return responseContent;
    }
}
```

The Azure SDK itself might also be instrumented by the OpenTelemetry agent, so you'll get a span for the `openAIClient.getChatCompletions` call. However, you'll still want to add custom attributes to make it LLM-specific as shown above.

## Architectural Patterns for LLM Observability

### 1. The LLM Gateway/Facade Layer

**Problem:** Direct LLM calls sprinkled throughout your codebase make instrumentation difficult and inconsistent.

**Solution:** Introduce an "LLM Gateway" or "Facade" layer. This is a dedicated service or set of classes responsible for all interactions with LLMs.

```java
// Example LLMGateway interface
public interface LLMGateway {
    String generateText(String prompt, String modelName);
    // Other methods like chat, embed, etc.
}

// Implementation that incorporates OpenTelemetry
public class OpenTelemetryLLMGateway implements LLMGateway {
    private final LLMClient actualLLMClient; // e.g., ClaudeCodeService or AzureOpenAIService
    private static final Tracer tracer = OpenTelemetry.get().getTracer("llm-gateway-instrumentation");

    public OpenTelemetryLLMGateway(LLMClient actualLLMClient) {
        this.actualLLMClient = actualLLMClient;
    }

    @Override
    public String generateText(String prompt, String modelName) {
        Span span = tracer.spanBuilder("LLMGateway.generateText")
                          .setAttribute("llm.model.name", modelName)
                          .setAttribute("llm.prompt.text", prompt.substring(0, Math.min(prompt.length(), 500)) + "...")
                          .startSpan();
        try (Scope scope = span.makeCurrent()) {
            // The actual LLM call will also be instrumented if actualLLMClient is
            // set up with its own tracing, forming a parent-child relationship.
            String result = actualLLMClient.callLLM(prompt, modelName);
            span.setAttribute("llm.response.text", result.substring(0, Math.min(result.length(), 500)) + "...");
            span.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
            return result;
        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "LLM generation failed");
            throw e;
        } finally {
            span.end();
        }
    }
}
```

**Benefits:**

*   **Centralized Logic:** All LLM observability logic (adding attributes, error handling) lives in one place.
*   **Abstraction:** Easily swap LLM providers or models without changing your core application logic.
*   **Consistency:** Ensures all LLM interactions are traced uniformly.

### 2. Correlation IDs for Request Tracing

Ensure that your application's request correlation ID (often an `X-Request-ID` header or a context variable) is propagated and associated with your OpenTelemetry traces. This allows you to link specific user requests to their corresponding LLM interactions in your observability backend.

The OpenTelemetry agent often handles propagation of trace context automatically for common protocols. If you are using custom mechanisms, you might need to manually inject and extract the `Context` using `io.opentelemetry.context.propagation.TextMapPropagator`.

### 3. Tracing for Retrieval Augmented Generation (RAG)

For RAG pipelines, observability becomes even more critical. You need to trace:

1.  The initial user query.
2.  The process of querying your vector database or search index.
3.  The retrieval of relevant documents.
4.  The construction of the prompt for the LLM, including the retrieved context.
5.  The LLM call itself.
6.  The final response generation.

Each of these steps can be represented as separate spans, forming a detailed trace of the RAG process.

```java
// Example snippet within a RAG service
public String processRAGQuery(String query) {
    Span parentSpan = Span.current(); // For the incoming request to this RAG service

    String finalAnswer = "";

    // Span 1: Document Retrieval
    Span retrievalSpan = tracer.spanBuilder("Document Retrieval")
                               .setParent(io.opentelemetry.context.Context.current().with(parentSpan))
                               .setAttribute("rag.query", query.substring(0, Math.min(query.length(), 200)) + "...")
                               .startSpan();
    List<Document> retrievedDocs = null;
    try (Scope scope = retrievalSpan.makeCurrent()) {
        retrievedDocs = vectorSearchService.search(query); // Assume this is also instrumented
        retrievalSpan.setAttribute("rag.retrieved_documents.count", retrievedDocs.size());
        retrievalSpan.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
    } catch (Exception e) {
        retrievalSpan.recordException(e);
        retrievalSpan.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "Failed to retrieve documents");
        throw e;
    } finally {
        retrievalSpan.end();
    }

    // Span 2: Prompt Construction
    Span promptConstructionSpan = tracer.spanBuilder("Prompt Construction")
                                       .setParent(io.opentelemetry.context.Context.current().with(parentSpan))
                                       .startSpan();
    String finalPrompt = constructPromptWithContext(query, retrievedDocs); // Your logic
    try (Scope scope = promptConstructionSpan.makeCurrent()) {
        promptConstructionSpan.setAttribute("llm.prompt.text", finalPrompt.substring(0, Math.min(finalPrompt.length(), 500)) + "...");
        promptConstructionSpan.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
    } catch (Exception e) {
        promptConstructionSpan.recordException(e);
        promptConstructionSpan.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "Failed to construct prompt");
        throw e;
    } finally {
        promptConstructionSpan.end();
    }

    // Span 3: LLM Call (using the gateway pattern)
    // The LLMGateway.generateText will handle its own span, and it will be a child of this span.
    Span llmCallSpan = tracer.spanBuilder("LLM Call (RAG)")
                             .setParent(io.opentelemetry.context.Context.current().with(parentSpan))
                             .startSpan();
    try (Scope scope = llmCallSpan.makeCurrent()) {
        finalAnswer = llmGateway.generateText(finalPrompt, "claude-3-opus-20240229"); // Assume this is instrumented internally
        llmCallSpan.setStatus(io.opentelemetry.api.trace.StatusCode.OK);
    } catch (Exception e) {
        llmCallSpan.recordException(e);
        llmCallSpan.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR, "LLM call failed in RAG");
        throw e;
    } finally {
        llmCallSpan.end();
    }

    return finalAnswer;
}
```

This nested structure of spans provides a granular view of where time and resources are spent within your RAG pipeline.

## Common Pitfalls and How to Avoid Them

## Anti-patterns

*   **Instrumenting Every LLM Call Manually:** Without a gateway or facade, developers tend to sprinkle `Span.current().setAttribute(...)` calls throughout their code. This leads to duplicated logic, inconsistencies, and is hard to maintain. Use a centralized LLM integration layer.
*   **Not Capturing LLM Specifics:** Relying solely on the auto-instrumentation for HTTP calls is insufficient. You miss critical LLM context like prompts, responses, model names, and token counts, rendering the traces less useful for LLM debugging and cost analysis. Always add custom attributes.
*   **Ignoring Errors in LLM Calls:** LLM APIs can fail for various reasons (rate limits, invalid requests, model issues). Failing to set span status to `ERROR` or record exceptions means you won't be alerted to problems in your observability backend, and you'll miss crucial debugging information.

## Conclusion

Observing your Java applications interacting with Claude Code and Azure AI services is no longer a luxury but a necessity. By strategically applying OpenTelemetry, enriching spans with LLM-specific context, and adopting architectural patterns like the LLM Gateway, you can gain deep insights into the performance, reliability, and cost of your LLM-powered features. This enables you to build more robust, efficient, and maintainable AI-driven applications.
