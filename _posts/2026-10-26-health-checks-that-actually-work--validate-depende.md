---
layout: post
title: "Health Checks That Actually Work: Validate Dependencies"
date: 2026-10-26
type: how-to
summary: "Write a robust health check endpoint using Claude Code that verifies all critical downstream services are responsive."
image: "/claude-daily-tips/assets/images/2026-10-26-health-checks-that-actually-work--validate-depende.jpg"
tags:
  - claude-code
  - java
  - spring
  - devtools
  - automation
---



![Health Checks That Actually Work: Validate Dependencies](/claude-daily-tips/assets/images/2026-10-26-health-checks-that-actually-work--validate-depende.jpg)



When deploying microservices, a simple "app is running" health check is a dangerous oversimplification. It tells you nothing about whether your service can actually connect to the databases, external APIs, or message queues it relies on. Manually verifying these critical integrations before every deployment is not only tedious but also a prime recipe for errors. This is where intelligent code generation can drastically improve your confidence, by helping you craft health endpoints that go beyond basic process checks to perform *genuine* dependency validation.

The fundamental advantage of using a tool like Claude Code lies in its ability to understand your existing codebase and generate functional, context-aware code. You can instruct it to create a robust Spring Boot controller that exposes a `/health/deep` endpoint. This endpoint will then intelligently orchestrate calls to various dependency health checks, consolidating their individual statuses into a single, actionable response. For instance, you might need to confirm a database connection, verify the availability and responsiveness of a critical downstream REST API, or ensure a Redis instance is accessible.

Here's a practical example of how you might prompt Claude Code to generate such a sophisticated endpoint. Crucially, you'll specify the framework (e.g., Spring Boot) and list the specific dependencies requiring checks. Claude Code can then produce the necessary Java code, complete with proper error handling and clear status reporting, like the example below which checks both a database connection and a downstream API.

```java
package com.example.health;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.Status;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

@RestController
public class ComprehensiveHealthController {

    private final DataSource dataSource;
    private final String downstreamApiUrl;
    private final HttpClient httpClient;

    public ComprehensiveHealthController(
            DataSource dataSource,
            @Value("${downstream.api.url}") String downstreamApiUrl) {
        this.dataSource = dataSource;
        this.downstreamApiUrl = downstreamApiUrl;
        this.httpClient = HttpClient.newBuilder()
                               .connectTimeout(Duration.ofSeconds(5)) // Connection timeout for the client itself
                               .build();
    }

    @GetMapping("/health/deep")
    public ResponseEntity<Health> deepHealthCheck() {
        Health.Builder builder = new Health.Builder();

        // Database Check
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(2)) { // 2-second validation timeout
                builder.up().withDetail("database", "Connected and valid");
            } else {
                builder.down().withDetail("database", "Connection invalid or timed out");
            }
        } catch (SQLException e) {
            builder.down().withDetail("database", "Connection error: " + e.getMessage());
        }

        // Downstream API Check
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(downstreamApiUrl + "/health")) // Assumes downstream has its own /health endpoint
                .timeout(Duration.ofSeconds(5)) // Request timeout
                .build();

        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                builder.withDetail("downstreamApi", "Reachable (Status: " + response.statusCode() + ")");
            } else {
                builder.down().withDetail("downstreamApi", "Unreachable (Status: " + response.statusCode() + ")");
            }
        } catch (Exception e) {
            builder.down().withDetail("downstreamApi", "Exception: " + e.getMessage());
        }

        // Aggregate overall status: if any detail is down, the entire check is down
        Health finalHealth = builder.build();
        if (finalHealth.getStatus().equals(Status.DOWN)) {
            return ResponseEntity.status(503).body(finalHealth);
        } else {
            return ResponseEntity.ok(finalHealth);
        }
    }
}
```

A critical, often overlooked limitation here is the potential for cascading failures within the health check itself. If a single slow dependency causes its check to time out, it can render the entire health endpoint sluggish or unresponsive, potentially masking other genuine issues or leading to false alarms. It's imperative to establish sensible timeouts for *each* individual dependency check and, for extremely complex scenarios, consider asynchronous execution. Furthermore, ensure that your dependencies expose their own reliable health or status endpoints that can be predictably queried.

Try it: Ask Claude Code to generate a Spring Boot health check endpoint that includes checks for a Redis connection and a mock downstream API, and observe how it handles the complexity.
