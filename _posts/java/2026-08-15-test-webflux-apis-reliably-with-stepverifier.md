---
layout: post
title: "Test WebFlux APIs Reliably with StepVerifier"
date: 2026-08-15
type: how-to
summary: "Master testing reactive Spring WebFlux APIs using WebTestClient and StepVerifier for robust integration tests."
image: "/claude-daily-tips/assets/images/java-2026-08-15-test-webflux-apis-reliably-with-stepverifier.jpg"
tags:
  - java
  - spring
  - junit
  - productivity
  - devtools
---



![Test WebFlux APIs Reliably with StepVerifier](/claude-daily-tips/assets/images/java-2026-08-15-test-webflux-apis-reliably-with-stepverifier.jpg)



As a Java developer building reactive APIs with Spring WebFlux, you've probably wrestled with how to reliably test asynchronous data streams. Standard unit tests can feel awkward when dealing with `Flux` and `Mono`. Thankfully, Spring Boot provides `WebTestClient` for making HTTP requests within your integration tests, and Project Reactor offers `StepVerifier` to assert the behavior of reactive streams. Combining these tools unlocks precise, readable, and robust testing for your reactive endpoints.

The synergy lies in using `WebTestClient` to trigger an HTTP request to your WebFlux application and obtain a `Flux` or `Mono` representing the response body. `StepVerifier` then subscribes to this reactive type, allowing you to declaratively assert that specific elements are emitted, that the stream completes as expected, or that it signals an error under particular conditions. This systematic approach ensures your reactive API handles both success and error scenarios exactly as intended.

Here's how you can test a common scenario: a Spring WebFlux controller endpoint that returns a `Flux` of simple objects. You'll need these standard Spring Boot test dependencies:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

Within your test class, inject `WebTestClient` and configure it to target your application context. Then, invoke your endpoint, for example, using `webTestClient.get().uri("/items").exchange()`. To test the response body as a reactive stream, use `.returnResult(Item.class)` (assuming `Item` is the type returned by your endpoint), access the `getResponseBody()`, and then cast it to a `StepVerifier` instance: `.as(StepVerifier::create)`. From here, you can chain assertions like `expectNext(item1, item2)`, `expectErrorMessage("Some expected error")`, or `expectComplete()`. A crucial detail often overlooked is forgetting to call `.verify()` on the `StepVerifier` instance. Without this final call, the assertions won't actually be executed, and your test will misleadingly pass.

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;
import reactor.test.StepVerifier;

// Assuming you have an Item class like:
// class Item { public String name; public Item(String name) { this.name = name; } }

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ItemControllerIT {

    @Autowired
    private WebTestClient webTestClient;

    @Test
    void shouldReturnListOfItems() {
        webTestClient.get()
            .uri("/items")
            .exchange()
            .expectStatus().isOk()
            .expectHeader().contentType("application/json") // Example: checking content type
            .returnResult(Item.class) // Assuming your endpoint returns Flux<Item>
            .getResponseBody()
            .as(StepVerifier::create)
            .expectNext(new Item("item1"), new Item("item2"), new Item("item3"))
            .expectComplete()
            .verify();
    }

    @Test
    void shouldHandleErrorOnEmptyItems() {
        webTestClient.get()
            .uri("/items/invalid") // Assuming this endpoint returns an error
            .exchange()
            .expectStatus().isBadRequest()
            .returnResult(String.class) // Assuming error response is String
            .getResponseBody()
            .as(StepVerifier::create)
            .expectErrorMessage("Invalid item requested")
            .verify();
    }
}
```
