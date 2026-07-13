---
layout: post
title: "HTTP Client Virtual Threads with Claude Code"
date: 2026-07-13
type: how-to
summary: "Implement non-blocking HTTP calls in Spring Boot using virtual threads with Claude Code assistance."
image: "/claude-daily-tips/assets/images/java-2026-07-13-http-client-virtual-threads-with-claude-code.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
  - productivity
---



![HTTP Client Virtual Threads with Claude Code](/claude-daily-tips/assets/images/java-2026-07-13-http-client-virtual-threads-with-claude-code.jpg)



When building modern Java applications, particularly those in microservice architectures, the sheer volume of outbound HTTP requests can become a significant performance bottleneck. Traditional thread-per-request models quickly exhaust system resources, leading to high latency and poor scalability. Project Loom's virtual threads offer a compelling solution, enabling massive concurrency with minimal operating system thread overhead. However, seamlessly integrating virtual threads into existing Java HTTP clients, especially within Spring Boot applications and when leveraging AI code assistants like Claude, requires a nuanced approach.

The key to unlocking virtual thread benefits with HTTP clients lies in `java.net.http.HttpClient`. This modern Java API is inherently designed to work harmoniously with virtual threads. When utilizing the asynchronous `sendAsync` method, it returns a `CompletableFuture`. Crucially, the continuation of this `CompletableFuture` will automatically execute on a virtual thread if one is available in the application's executor. Tools like Claude Code can significantly assist in refactoring existing synchronous HTTP client code to adopt this pattern, thereby abstracting away much of the boilerplate associated with asynchronous programming. For instance, you can prompt Claude Code with a request like, "Refactor this method to use `HttpClient.sendAsync` and return a `CompletableFuture` for non-blocking I/O," guiding it to adapt your synchronous calls.

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

import org.springframework.stereotype.Service;

@Service
public class VirtualThreadHttpClient {

    private final HttpClient httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .followRedirects(HttpClient.Redirect.NORMAL)
            .build();

    /**
     * Fetches content from a URL asynchronously using Java's HttpClient.
     * This method returns a CompletableFuture that will complete with the response body.
     * When executed within a virtual thread context, the underlying sendAsync operation
     * will leverage virtual threads for non-blocking I/O.
     *
     * @param url The URL to fetch.
     * @return A CompletableFuture holding the response body as a String.
     */
    public CompletableFuture<String> fetchUrlAsync(String url) {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                         .thenApply(HttpResponse::body);
    }

    /**
     * Example of processing multiple URLs concurrently using virtual threads.
     * This method demonstrates how to manage multiple asynchronous HTTP calls
     * and aggregate their results.
     *
     * @param url1 The first URL to fetch.
     * @param url2 The second URL to fetch.
     */
    public void processUrls(String url1, String url2) {
        CompletableFuture<String> future1 = fetchUrlAsync(url1);
        CompletableFuture<String> future2 = fetchUrlAsync(url2);

        CompletableFuture<Void> allFutures = CompletableFuture.allOf(future1, future2);

        allFutures.thenRun(() -> {
            try {
                // Calling .get() here blocks the *current virtual thread*, not an OS thread.
                // This is generally the desired behavior for sequencing operations within a virtual thread.
                String result1 = future1.get();
                String result2 = future2.get();
                System.out.println("Result 1 (first 50 chars): " + result1.substring(0, Math.min(result1.length(), 50)) + "...");
                System.out.println("Result 2 (first 50 chars): " + result2.substring(0, Math.min(result2.length(), 50)) + "...");
            } catch (Exception e) {
                System.err.println("Error fetching URLs: " + e.getMessage());
            }
        });
    }
}
```

A crucial aspect to understand is the behavior of `.get()` when used with `CompletableFuture`s in a virtual thread environment. While `sendAsync` itself doesn't block the underlying OS thread, calling `.get()` *will* block the current virtual thread. This is precisely the intended design: virtual threads are extremely lightweight and inexpensive to park and resume, allowing them to block without depleting system resources. However, developers should be aware of this if they have highly sequential, performance-critical logic that *absolutely* cannot yield. In such rare scenarios, careful consideration of `CompletableFuture` composition or explicit platform thread management might be necessary. Furthermore, ensure your Spring Boot application is configured to leverage virtual threads. For recent Spring Boot versions, enabling this is typically done by setting `spring.threads.virtual.enabled=true` in `application.properties`.

To experiment with this, try prompting Claude Code with a synchronous HTTP client call from your Spring Boot project and request a refactoring to use `HttpClient.sendAsync`, ensuring the output returns a `CompletableFuture`. This hands-on approach, combined with understanding the non-blocking I/O principles enabled by virtual threads and the `HttpClient` API, provides a robust pathway to enhancing your application's concurrency and responsiveness.
