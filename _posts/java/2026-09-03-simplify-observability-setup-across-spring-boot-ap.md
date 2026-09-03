---
layout: post
title: "Simplify Observability Setup Across Spring Boot Apps"
date: 2026-09-03
type: how-to
summary: "Create a reusable Spring Boot starter for consistent observability without repetitive configuration."
image: "/claude-daily-tips/assets/images/java-2026-09-03-simplify-observability-setup-across-spring-boot-ap.jpg"
tags:
  - java
  - spring
  - devtools
  - productivity
  - claude-code
---



![Simplify Observability Setup Across Spring Boot Apps](/claude-daily-tips/assets/images/java-2026-09-03-simplify-observability-setup-across-spring-boot-ap.jpg)



As a Java developer managing multiple Spring Boot microservices, you're likely familiar with the repetitive choreography of configuring logging, tracing, and metrics. Each new service demands the same `application.properties` or `application.yml` entries for your chosen observability stack, be it OpenTelemetry or Micrometer. This manual, per-service configuration leads to configuration drift, inconsistencies, and the tedious chore of global observability updates. What if integrating observability was as simple as adding a dependency?

This is precisely where a custom Spring Boot starter becomes invaluable. By encapsulating common observability configurations, you can create a plug-and-play solution for your projects. We'll explore how to build such a starter, focusing on ensuring consistent trace ID logging. The core idea is to leverage Spring Boot's `AutoConfiguration` mechanism, conditionally applying settings based on the presence of other observability-related dependencies.

Our custom starter will feature an `ObservabilityAutoConfiguration` class, annotated with `@Configuration` and `@ConditionalOnClass`. This ensures our configuration only activates when specific observability classes, like `OpenTelemetry` and `MeterRegistry`, are found on the classpath. For example, we can automatically configure a common logging pattern that includes trace IDs, but only if an OpenTelemetry tracing library is detected. This automatic application of consistent configurations prevents manual errors and saves significant development time.

```java
package com.example.observability.starter;

import io.micrometer.core.instrument.MeterRegistry;
import io.opentelemetry.api.OpenTelemetry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;

@AutoConfiguration
@ConditionalOnClass({OpenTelemetry.class, MeterRegistry.class})
@ConditionalOnProperty(value = "my.observability.enabled", havingValue = "true", matchIfMissing = true)
public class ObservabilityAutoConfiguration {

    private static final Logger logger = LoggerFactory.getLogger(ObservabilityAutoConfiguration.class);

    @Bean
    public String commonObservabilitySetupMessage() {
        logger.info("Custom Observability Starter: Applying common configuration for tracing and metrics.");
        // In a real-world scenario, this would involve configuring beans for
        // MDC (Mapped Diagnostic Context) integration, common metric tags, or custom trace exporters.
        return "Observability configuration applied!";
    }
}
```

A significant "gotcha" to watch out for is dependency version conflicts. If your starter mandates specific versions of observability libraries, it could clash with versions already present in the consuming application, leading to "dependency hell." To mitigate this, always aim for broad compatibility by declaring dependencies with `provided` scope or utilize Spring Boot's dependency management features to align versions. Additionally, while `@ConditionalOnProperty` offers great flexibility, requiring consumers to explicitly enable the starter can sometimes add an extra step that might be overlooked in fast-paced development environments.

To test this, create a new Spring Boot project and add this custom starter as a dependency. If you define `my.observability.enabled=true` in your application properties, you'll see the "Observability configuration applied!" log message upon startup, demonstrating how a single dependency can standardize your observability setup across numerous microservices. This approach moves beyond basic Spring Boot auto-configuration by providing a targeted, opinionated solution for a common cross-cutting concern.
