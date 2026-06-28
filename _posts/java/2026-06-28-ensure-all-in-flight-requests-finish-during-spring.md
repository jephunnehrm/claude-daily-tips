---
layout: post
title: "Ensure All In-Flight Requests Finish During Spring Boot Shutdown"
date: 2026-06-28
type: how-to
summary: "Configure Spring Boot to gracefully drain in-flight requests during shutdown, preventing data loss and ensuring clean state."
image: "/claude-daily-tips/assets/images/java-2026-06-28-ensure-all-in-flight-requests-finish-during-spring.jpg"
tags:
  - java
  - spring
  - devtools
  - claude-code
---



![Ensure All In-Flight Requests Finish During Spring Boot Shutdown](/claude-daily-tips/assets/images/java-2026-06-28-ensure-all-in-flight-requests-finish-during-spring.jpg)



As Java developers building microservices with Spring Boot, we often face the challenge of shutting down our applications cleanly. A common pain point is when an in-flight request, perhaps a long-running database operation or an external API call, is interrupted abruptly during a deployment or graceful restart. This can lead to incomplete transactions, inconsistent application state, or even user-facing errors if clients retry. While Spring Boot offers some built-in mechanisms, fine-tuning this shutdown behavior for robust in-flight request draining requires specific configuration.

Fortunately, we can leverage Claude Code to assist in configuring this behavior. By defining custom `BeanFactoryPostProcessor` implementations or directly configuring Spring's `ApplicationContext` properties, we can instruct the embedded Tomcat, Jetty, or Undertow server to wait for active requests to complete. This involves setting specific properties that control the shutdown lifecycle of the web server.

Here’s how you can configure your Spring Boot application to wait for a certain duration to drain in-flight requests. This example focuses on Tomcat, which is Spring Boot’s default embedded server.

```java
import org.springframework.boot.web.embedded.tomcat.TomcatServletWebServerFactory;
import org.springframework.boot.web.server.WebServerFactoryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GracefulShutdownConfig {

    @Bean
    public WebServerFactoryCustomizer<TomcatServletWebServerFactory> tomcatCustomizer() {
        return (factory) -> {
            factory.addConnectorCustomizers(connector -> {
                connector.setConnectionTimeout(0); // Optional: Prevents new connections during shutdown
                connector.setGracefulShutdownTimeout(30000); // Wait up to 30 seconds for in-flight requests
            });
        };
    }
}
```

A potential gotcha here is the `GracefulShutdownTimeout` value. Setting it too short might still lead to abrupt terminations for longer requests, while setting it too high could significantly increase application downtime during restarts. You’ll need to benchmark your typical request latencies to determine an appropriate value. Also, this configuration primarily impacts the embedded web server; background tasks or asynchronous operations not directly tied to incoming HTTP requests might require additional custom shutdown logic using `DisposableBean` or `ApplicationListener<ContextClosedEvent>`.

**Try it:** Add the `GracefulShutdownConfig.java` file to your Spring Boot project and restart your application. Then, simulate a long-running request (e.g., using `Thread.sleep` in a controller endpoint) and trigger an application shutdown to observe the extended waiting period.
