---
layout: chapter
title: "Token Optimization & Cost Control in Multi-Agent Systems"
date: 2026-07-20
series: "agent-pipelines"
series_name: "Agent Pipelines and Orchestration"
week: 30
summary: "This chapter delves into practical strategies and architectural considerations for minimizing token consumption and managing costs within complex multi-agent systems leveraging Claude Code and Azure AI. You will learn to design for efficiency and implement robust cost-control mechanisms for scalable agent deployments."
image: "/claude-daily-tips/assets/images/chapter-agent-pipelines-week30.jpg"
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



![Token Optimization & Cost Control in Multi-Agent Systems](/claude-daily-tips/assets/images/chapter-agent-pipelines-week30.jpg)



## Introduction

Multi-agent systems offer unprecedented capabilities for automating complex workflows, leveraging specialized AI agents to tackle distinct sub-problems. However, as the number of agents and the intricacy of their interactions grow, so does the potential for escalating token consumption and, consequently, operational costs. This chapter focuses on practical strategies and architectural patterns to ensure that your multi-agent systems remain economically viable and scalable, particularly when utilizing Claude Code and Azure AI services. We'll explore techniques for token optimization at the agent level and architectural approaches for orchestrating cost-effective agent pipelines.

## Understanding Token Consumption in Multi-Agent Contexts

At its core, token optimization is about minimizing the input and output tokens processed by your language models. In a multi-agent system, this amplification occurs due to:

*   **Redundant Information Transfer:** Agents might repeatedly send the same or similar context to other agents.
*   **Overly Verbose Prompts:** Individual agent prompts may not be concise, including unnecessary preamble or examples.
*   **Inefficient Conversation History:** Maintaining extensive, unpruned conversation histories between agents can quickly inflate token counts.
*   **Uncontrolled Agent Output:** Agents producing lengthy, rambling outputs or excessive intermediate thoughts add to costs.
*   **Orchestration Layer Overhead:** The orchestrator itself might add to token usage by summarizing states or managing context.

## Architectural Strategies for Token Optimization

Designing your multi-agent system with token efficiency in mind from the outset is paramount.

### 1. Specialized Agents with Minimal Context Dependencies

Design agents to be as self-contained as possible, requiring only the essential information to perform their task. Avoid building agents that rely on extensive shared context or history unless absolutely necessary.

**Example:** Instead of a single "Customer Service Agent" that handles all queries, break it down into:
*   **"Intent Recognition Agent":** Identifies the user's core need.
*   **"Information Retrieval Agent":** Fetches relevant data based on intent.
*   **"Response Generation Agent":** Crafts a concise response using retrieved info.

This modularity allows each agent to operate with a smaller, focused context window.

### 2. Smart Orchestration and Context Management

The orchestrator plays a critical role in managing the flow of information and pruning unnecessary context.

#### a. Context Summarization and Condensation

Instead of passing raw conversation histories, have the orchestrator (or a dedicated summarization agent) periodically condense and summarize the relevant parts of the interaction. This reduces the input token count for subsequent agent calls.

**Conceptual Approach:**

```csharp
// In your orchestrator logic
string recentConversation = GetLastNMessages(conversationHistory, 5); // Get last 5 messages
string summary = await ClaudeCode.GenerateSummaryAsync(
    prompt: $"Summarize the following conversation snippet concisely, highlighting key decisions and outstanding questions: {recentConversation}",
    model: "claude-3-haiku-20240307" // Or a cheaper model for summarization
);
// Add summary to the context for the next agent
```

#### b. Conditional Agent Invocation

Only invoke an agent if its task is truly necessary for the current step. The orchestrator can make these decisions based on the current state and previous agent outputs.

#### c. State Management without Full History

Store essential state information (e.g., user ID, product of interest, current stage of a workflow) in a structured format (like a database or Azure Cosmos DB) rather than relying solely on passing large text blobs.

### 3. Prompt Engineering for Conciseness

Each agent's prompt is a direct contributor to token costs.

#### a. Lean Prompts

Remove any unnecessary preamble, verbose instructions, or overly elaborate examples. Focus on the direct task and desired output format.

**Bad Prompt Example:**
```
"You are an extremely helpful AI assistant. Your task is to analyze the following customer review and extract any mentions of product defects. Please be very thorough and provide a detailed list of all potential issues you find. For each issue, provide a brief description of why it might be a defect. Remember to be polite and professional in your response. Here is the review: [review text]"
```

**Good Prompt Example:**
```
"Extract product defects from the following review. Output as a JSON array of defect names.
Review: [review text]"
```

#### b. Few-Shot Learning with Minimal Examples

If using few-shot examples, keep them as short and relevant as possible. Consider dynamic example selection based on the current query.

#### c. Output Formatting Constraints

Explicitly request concise output formats like JSON, bullet points, or single-sentence answers where appropriate. This guides the model to be less verbose.

**Example using `claude` CLI:**
```bash
claude prompt "Extract the main sentiment (positive, negative, neutral) from this text and output only the sentiment. Text: 'The product arrived on time but was slightly damaged.'" \
--model claude-3-haiku-20240307 \
--output-format json
```
*(Note: While `claude` CLI doesn't have a direct `--output-format json` flag for *literal* JSON output of sentiment, you would engineer the prompt to ask for JSON and parse it. The spirit here is to guide the LLM output.)*

## Practical Implementation Techniques

Beyond architectural patterns, specific techniques can be applied within agent implementations.

### 1. Selective Context Inclusion

When an agent needs to consult previous interactions or external data, be selective. Instead of passing the entire document or chat log, extract only the most relevant snippets. Techniques like RAG (Retrieval Augmented Generation) are crucial here.

**Example with Azure AI Search (formerly Azure Cognitive Search) and RAG:**

Imagine an agent needs to answer a question based on a large knowledge base. Instead of loading the entire KB into the prompt:

1.  **User Query:** "What are the warranty terms for product X?"
2.  **Orchestrator/Agent RAG Component:** Queries Azure AI Search for relevant document chunks.
3.  **Retrieval:** Azure AI Search returns relevant passages (e.g., "Product X carries a 2-year limited warranty against manufacturing defects.").
4.  **Prompt Construction:** The agent's prompt includes the original query and the retrieved passages:
    ```
    prompt = f"Based on the following information, answer the user's question: {retrieved_passages}\n\nUser Question: What are the warranty terms for product X?"
    ```
    This drastically reduces token usage compared to sending the entire knowledge base.

### 2. Output Pruning and Validation

Implement post-processing logic for agent outputs. If an agent generates overly verbose text, trim it down. If it generates extraneous information, filter it out.

**.NET Example (Illustrative):**

```csharp
// Assuming 'agentOutput' is a string from a Claude Code call
string cleanedOutput = agentOutput.Trim();
if (cleanedOutput.Length > 200) // Simple example: truncate if too long
{
    cleanedOutput = cleanedOutput.Substring(0, 200) + "...";
}
// Further validation could involve parsing JSON, extracting specific entities, etc.
```

### 3. Model Selection for Cost vs. Capability

Not all tasks require the most advanced (and expensive) models. Use cheaper, faster models for simpler tasks like summarization, classification, or initial parsing, and reserve the powerful models for complex reasoning or generation. Claude Code offers various models, including `claude-3-haiku-20240307` which is significantly more cost-effective for many tasks.

**CLI Example:**

```bash
# For complex reasoning
claude prompt "Develop a detailed marketing strategy for a new SaaS product." \
--model claude-3-opus-20240229

# For simpler classification
claude prompt "Classify the following customer feedback into one of these categories: bug report, feature request, general inquiry. Feedback: 'The login button isn't working.'" \
--model claude-3-haiku-20240307
```

### 4. Rate Limiting and Cost Ceilings

Implement mechanisms at the orchestrator level to:

*   **Track token usage per agent call and per user session.**
*   **Set daily or hourly token budgets.**
*   **Trigger alerts or disable agent functionality when budgets are approached or exceeded.**
*   **Use Azure Cost Management + Billing to set budgets and alerts for Azure AI services.**

## Cost Control Mechanisms

Beyond optimization, direct cost control is crucial.

### 1. Azure Cost Management + Billing

*   **Set Budgets:** Define monetary budgets for your Azure AI services (e.g., Azure OpenAI Service, Azure AI Search).
*   **Configure Alerts:** Set up alerts to notify you when spending reaches a certain percentage of your budget.
*   **Resource Tagging:** Tag all your Azure resources related to the agent system (e.g., by agent function, by project) to accurately track costs.

### 2. Token Counting Libraries and Services

Integrate libraries or custom solutions to accurately count tokens for both input and output. This is essential for granular tracking and reporting.

**Example using `tiktoken` (common for OpenAI, but conceptual for Claude's tokenization):**
While Claude Code has its own internal tokenization, conceptually you'd use a library to count:

```python
# Conceptual Python snippet, assume a Claude Code equivalent exists or is implemented
# For example, you might call a Claude Code SDK method that returns token counts,
# or use an approximation based on character count for certain Claude models if direct count isn't exposed.

# from anthropic.tokenizers import async_get_tokenizer # Example for Anthropic SDK

# async def count_tokens(text, model_name):
#     tokenizer = await async_get_tokenizer(model_name)
#     return len(tokenizer.encode(text))

# input_tokens = await count_tokens(user_prompt, "claude-3-opus-20240229")
# output_tokens = await count_tokens(llm_response, "claude-3-opus-20240229")
# total_tokens = input_tokens + output_tokens
```
*Self-correction: Claude Code itself doesn't expose a public `tiktoken`-like direct token counting API for programmatic use via its CLI or a readily available Python library in the same way OpenAI does. However, one can estimate token counts by understanding that Claude models generally tokenise text at a rate of roughly 4 characters per token. For precise billing, rely on the Azure AI service usage reports.*

### 3. Agent-Specific Cost Caps

For critical or experimental agents, consider implementing hard caps on token usage per invocation or per user session. If an agent exceeds its cap, it can either stop processing or return a generic "processing limit reached" message.

**Java Example (Illustrative - MCP Integration):**

```java
// Within an agent's execution logic in a .NET or Java MCP environment

// Assume you have a token counter utility
TokenCounter tokenCounter = new TokenCounter();
int maxTokensPerCall = 1000; // Example cap

// Before making the Claude Code call
Prompt prompt = new Prompt("Analyze this data...");
int inputTokens = tokenCounter.countTokens(prompt.getText(), "claude-3-haiku-20240307"); // Hypothetical counter

if (inputTokens > maxTokensPerCall) {
    throw new TokenLimitExceededException("Input prompt exceeds token limit for this agent.");
}

// Make the Claude Code call
// Assuming a helper method that returns both text and token count for the output
ClaudeCodeResponse response = callClaudeCodeApi(prompt, "claude-3-haiku-20240307");
int outputTokens = response.getTokenCount();

if (outputTokens > maxTokensPerCall) {
    // Handle overly verbose output
    response.setText(response.getText().substring(0, 150) + "..."); // Truncate
    // Log this event for review
}
```

## Common Pitfalls and How to Avoid Them

*   **Pitfall:** Relying solely on cheaper models without considering their capability limitations.
    **Avoidance:** Benchmark different models for your specific tasks. Use Opus or Sonnet for complex reasoning and Haiku for simpler, high-volume tasks. Continuous monitoring and A/B testing can help find the optimal balance.
*   **Pitfall:** Not tracking token usage granularly.
    **Avoidance:** Implement robust logging and utilize Azure Cost Management + Billing. Tag resources meticulously. If possible, use SDKs that report token usage for each API call.
*   **Pitfall:** Treating conversation history as a free resource.
    **Avoidance:** Implement explicit strategies for context summarization or selective retrieval. Regularly prune or archive old conversation states.
*   **Pitfall:** Over-engineering prompts with excessive detail or examples.
    **Avoidance:** Adopt a "lean prompt" philosophy. Start with the minimal prompt necessary and iterate. Test prompts for clarity and conciseness.

## Conclusion

Token optimization and cost control are not afterthoughts but fundamental architectural considerations for any production-grade multi-agent system. By employing smart orchestration, disciplined prompt engineering, selective context management, and leveraging Azure's cost management tools, you can build powerful, scalable, and economically viable agent pipelines. Remember that continuous monitoring and iteration are key to maintaining cost-efficiency as your system evolves.

## Anti-patterns

### 1. The "Echo Chamber" Agent

**Description:** An agent that repeatedly feeds its own output back as input to another agent (or itself) without significant transformation or progress. This creates an infinite loop of token consumption, often leading to runaway costs and no meaningful output.

**Why it's bad:** Directly inflates token counts unnecessarily. Wastes computational resources. Indicates a flaw in the agent's reasoning or the orchestrator's control flow.

**Example Scenario:** An agent tasked with creative writing might recursively ask for more descriptive adjectives without a clear stopping condition or integration of plot progression, consuming tokens to generate increasingly redundant or irrelevant descriptions.

### 2. The "Kitchen Sink" Prompt

**Description:** Individual agent prompts that include vast amounts of irrelevant context, overly verbose instructions, multiple unrelated examples, or a demand for an excessively detailed output format. This is often a symptom of a lack of clarity in the agent's role or the overall system design.

**Why it's bad:** Maximizes input tokens for every single call, dramatically increasing costs. Dilutes the model's focus, potentially leading to poorer quality responses.

**Example Scenario:** A simple intent classification agent prompt that includes the entire user's chat history for the past week, a lengthy preamble about AI ethics, and three complex, multi-turn example conversations, when only the current user utterance and a single, concise example are needed for classification.

### 3. Neglecting Model Tiering

**Description:** Using the most powerful and expensive Claude Code model (e.g., Opus) for every single task within the multi-agent system, regardless of complexity. This might stem from a desire for "best possible quality" everywhere or a lack of awareness of the different capabilities and costs of available models like Haiku and Sonnet.

**Why it's bad:** Leads to significantly higher operational costs than necessary. The marginal benefit of a more powerful model is often negligible for simpler tasks, making it an inefficient use of resources.

**Example Scenario:** Using `claude-3-opus-20240229` to extract a single email address from a short piece of text when `claude-3-haiku-20240307` could perform the task with high accuracy at a fraction of the cost.
