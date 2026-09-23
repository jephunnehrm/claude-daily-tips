---
layout: post
title: "Centralize Observability Config with Spring Boot Starters"
date: 2026-09-23
type: how-to
summary: "Reduce boilerplate and ensure consistent observability setup across your Spring Boot applications by creating a custom starter."
image: "/claude-daily-tips/assets/images/java-2026-09-23-centralize-observability-config-with-spring-boot-s.jpg"
tags:
  - java
  - spring
  - devtools
  - productivity
  - claude-code
---



![Centralize Observability Config with Spring Boot Starters](/claude-daily-tips/assets/images/java-2026-09-23-centralize-observability-config-with-spring-boot-s.jpg)



Developers building microservices frequently face the repetitive task of configuring observability – setting up distributed tracing, collecting application metrics, and managing structured logging – across a multitude of Spring Boot applications. This common configuration, when scattered, leads to inconsistencies, a proliferation of boilerplate code, and a significant burden when updates or changes are required. A custom Spring Boot starter offers an elegant solution by encapsulating this entire observability stack into a single, reusable module, establishing a "single source of truth" and dramatically simplifying the development process for individual services.

To construct such a starter, you’ll craft a new Maven or Gradle module. This module will house the essential observability libraries, such as Micrometer for metrics, Brave or OpenTelemetry for tracing, and your chosen logging framework. The core of the starter lies in its Spring Boot auto-configuration classes, particularly an `@AutoConfiguration` class. This class leverages Spring Boot’s conditional features (`@ConditionalOnClass`, `@ConditionalOnBean`) to intelligently activate the observability setup only when the necessary dependencies are present in the consuming application. This ensures your starter is robust and doesn't interfere with applications that don't require its specific observability configuration.

Here’s an example of how such an auto-configuration class might be structured. This example demonstrates configuring a basic setup using Micrometer for metrics and OpenTelemetry for tracing, leveraging its bridge for Micrometer Tracing.

```java
package com.example.observability.autoconfiguration;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.micrometer.tracing.Tracer;
import io.micrometer.tracing.otel.bridge.OtelCurrentTraceContext;
import io.micrometer.tracing.otel.bridge.OtelTracer;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.TracerProvider;
import io.opentelemetry.context.propagation.TextMapPropagator;
import io.opentelemetry.extension.trace.propagation.W3CTraceContext;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
import io.opentelemetry.sdk.trace.samplers.Sampler;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.core.env.Environment;

@AutoConfiguration
@ConditionalOnClass({MeterRegistry.class, Tracer.class})
public class ObservabilityAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MeterRegistry meterRegistry(Environment environment) {
        // A simple default MeterRegistry; consider configuring exporters in production.
        return new SimpleMeterRegistry();
    }

    @Bean
    @ConditionalOnMissingBean
    public TracerProvider otelTracerProvider() {
        // Configure sampling for trace collection. This is a placeholder.
        return SdkTracerProvider.builder()
                .setSampler(Sampler.alwaysOn()) // In production, use a configurable sampler.
                .addSpanProcessor(SimpleSpanProcessor.create(io.opentelemetry.sdk.trace.export.ConsoleSpanExporter.create())) // For demonstration, log spans to console.
                .build();
    }

    @Bean
    @ConditionalOnMissingBean
    public OpenTelemetry openTelemetry(TracerProvider tracerProvider) {
        return OpenTelemetrySdk.builder()
                .setTracerProvider(tracerProvider)
                .setPropagators(io.opentelemetry.context.propagation.DefaultPropagators.builder()
                        .add(W3CTraceContext.getInstance()) // Include W3C Trace Context for interoperability.
                        .build())
                .build();
    }

    @Bean
    @ConditionalOnMissingBean
    public OtelCurrentTraceContext otelCurrentTraceContext() {
        return new OtelCurrentTraceContext();
    }

    @Bean
    @ConditionalOnMissingBean
    public OtelTracer otelTracer(OpenTelemetry openTelemetry, OtelCurrentTraceContext otelCurrentTraceContext) {
        // In a real scenario, you'd likely inject a custom SpanProcessor here
        // for exporting traces to a backend like Jaeger or Zipkin.
        return new OtelTracer(openTelemetry, otelCurrentTraceContext, new io.micrometer.tracing.util.ExceptionUtils());
    }

    @Bean
    @ConditionalOnMissingBean
    public Tracer micrometerTracer(OtelTracer otelTracer) {
        return otelTracer; // Bridge OtelTracer to Micrometer's Tracer interface.
    }

    @Bean
    @ConditionalOnMissingBean
    public TextMapPropagator textMapPropagator(OpenTelemetry openTelemetry) {
        return openTelemetry.getPropagators().getTextMapPropagator();
    }

    // Beans for PropagatingReceiverPredicate and PropagatingSenderPredicate would be added if needed
    // for specific integrations, but are omitted here for brevity.
}
```

A critical consideration when developing your starter is dependency management. Directly including observability libraries as compile-time dependencies can lead to version conflicts if the consuming application intends to use different versions. A robust strategy is to declare these as `optional` dependencies in your starter's `pom.xml` or `build.gradle`. Alternatively, leverage Spring Boot's dependency management, often through its Bill of Materials (BOM), to allow the consuming application to control versions. Crucially, ensure your starter’s `META-INF/spring.factories` or `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` file correctly lists your primary `@AutoConfiguration` class, enabling Spring Boot to discover and apply it.

To solidify your understanding, consider creating a minimal Spring Boot starter project. You can use your preferred build tool and then strategically add dependencies for Micrometer and OpenTelemetry, marking them as optional. Pay close attention to the starter's `pom.xml` (or `build.gradle`) and its `META-INF` directory to ensure the auto-configuration is properly registered. This hands-on approach will reveal the nuances of dependency management and the mechanics of Spring Boot's auto-configuration.
