---
layout: post
title: "Trace Background .NET Workflows with OpenTelemetry"
date: 2026-10-19
type: how-to
summary: "Add OpenTelemetry spans to your .NET background jobs to improve distributed tracing visibility."
image: "/claude-daily-tips/assets/images/dotnet-2026-10-19-trace-background--net-workflows-with-opentelemetry.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
---



![Trace Background .NET Workflows with OpenTelemetry](/claude-daily-tips/assets/images/dotnet-2026-10-19-trace-background--net-workflows-with-opentelemetry.jpg)



Debugging asynchronous, long-running background tasks in distributed .NET systems is notoriously challenging. When an issue arises, manually piecing together the sequence of operations, identifying the failure point, and understanding its context across various services can be an exhaustive and error-prone undertaking. OpenTelemetry offers a standardized solution by enabling code instrumentation to generate traces that visualize request flow across your applications. However, for .NET background workflows, instrumenting every logical step manually can quickly become tedious and repetitive.

Claude Code can significantly alleviate this burden by intelligently analyzing your C# background worker code. It identifies distinct units of work and automatically generates the necessary OpenTelemetry API calls to create `Activity` spans. This process includes assigning meaningful activity names, enriching them with contextual tags, and correctly managing the start and stop times of these activities, all critical for effective distributed tracing.

Consider a common scenario: a background worker consuming messages from a message queue. Each message might trigger a series of distinct operations such as deserialization, data validation, business logic processing, and persistence. Tracing each of these steps individually is crucial for performance analysis and debugging. Instead of painstakingly writing boilerplate `ActivitySource` and `CreateActivity` calls for every single step, Claude Code can automate this process, saving significant development time and reducing the chance of instrumentation errors.

For instance, you can prompt Claude Code to instrument a `ProcessMessageAsync` method within your background worker. Given a `MyBackgroundWorker.cs` file and the instruction: "Add OpenTelemetry Activity spans for logical steps within the ProcessMessageAsync method. Use 'MyBackgroundWorker' as the ActivitySourceName. Include tags for message ID and status, and ensure correlation ID is propagated.", Claude Code can generate the instrumented code. A potential gotcha with such automation is ensuring that semantic conventions are applied correctly. While Claude Code can add generic tags, you may need to refine these to match specific OpenTelemetry attributes for your message queue integration or other framework-specific details to ensure proper integration with your tracing backend.
