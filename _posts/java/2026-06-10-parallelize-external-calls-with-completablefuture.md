---
layout: post
title: "Parallelize External Calls with CompletableFuture and Claude Code"
date: 2026-06-10
type: how-to
summary: "Learn how to use Claude Code and CompletableFuture to efficiently execute multiple external service calls concurrently in your Spring Boot applications."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - claude-code
  - productivity
  - devtools
---



![Parallelize External Calls with CompletableFuture and Claude Code](assets/images/placeholder.jpg)



Fetching data from multiple independent external services for a single request is a common performance bottleneck. Performing these calls sequentially can lead to a sluggish user experience. While Java's `CompletableFuture` is designed for asynchronous operations, building intricate, robust pipelines for multiple calls can become verbose and introduce subtle error-handling complexities. This is where AI coding assistants can significantly streamline the process, helping generate cleaner, more manageable asynchronous code.

Consider the scenario of retrieving a user's profile, their recent orders, and their activity log, each from distinct microservices. Initiating these calls in parallel using `CompletableFuture` is key to improving responsiveness. Instead of manually writing all the boilerplate for chaining these asynchronous tasks, you can leverage an AI assistant. For example, a prompt like "Generate Java `CompletableFuture` code to fetch user details, orders, and activity concurrently from separate REST endpoints, combining the results" can yield a solid starting point. The AI-generated code will naturally employ methods like `CompletableFuture.supplyAsync` for offloading tasks to an `ExecutorService` and `thenCombine` for elegantly merging results from parallel computations, effectively reducing overall request latency.

Here's a practical illustration using `CompletableFuture` for concurrent external calls. Assume you have methods `fetchUserDetails(userId)`, `fetchOrderHistory(userId)`, and `fetchRecentActivity(userId)`, each returning a `CompletableFuture<T>` representing the result of an asynchronous service invocation:

```java
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.Collections; // Import Collections for Collections.emptyList()

// Placeholder for actual domain classes
class UserDetails { }
class Order { }
class Activity { }

// Represents the aggregated user data
class CombinedUserData {
    UserDetails userDetails;
    List<Order> orderHistory;
    List<Activity> recentActivity;

    CombinedUserData(UserDetails userDetails, List<Order> orderHistory, List<Activity> recentActivity) {
        this.userDetails = userDetails;
        this.orderHistory = orderHistory;
        this.recentActivity = recentActivity;
    }
}

public class UserDataService {

    // Consider using a shared, properly managed ExecutorService (e.g., Spring's TaskExecutor)
    // for production applications to avoid resource leaks.
    private final ExecutorService executorService = Executors.newFixedThreadPool(5); // Example executor

    // Assume these methods are implemented to call external services and return CompletableFuture
    private CompletableFuture<UserDetails> fetchUserDetails(String userId) {
        // Simulate network call
        return CompletableFuture.supplyAsync(() -> {
            System.out.println("Fetching user details for " + userId);
            // In a real app: call an HTTP client
            return new UserDetails();
        }, executorService);
    }

    private CompletableFuture<List<Order>> fetchOrderHistory(String userId) {
        // Simulate network call
        return CompletableFuture.supplyAsync(() -> {
            System.out.println("Fetching order history for " + userId);
            // In a real app: call an HTTP client
            return Collections.emptyList(); // Dummy data
        }, executorService);
    }

    private CompletableFuture<List<Activity>> fetchRecentActivity(String userId) {
        // Simulate network call
        return CompletableFuture.supplyAsync(() -> {
            System.out.println("Fetching recent activity for " + userId);
            // In a real app: call an HTTP client
            return Collections.emptyList(); // Dummy data
        }, executorService);
    }

    public CompletableFuture<CombinedUserData> getUserDataConcurrently(String userId) {
        CompletableFuture<UserDetails> userDetailsFuture = fetchUserDetails(userId);
        CompletableFuture<List<Order>> orderHistoryFuture = fetchOrderHistory(userId);
        CompletableFuture<List<Activity>> recentActivityFuture = fetchRecentActivity(userId);

        // Combine the results as they become available
        return userDetailsFuture.thenCombineAsync(orderHistoryFuture, (userDetails, orderHistory) -> {
                    // This lambda executes after both userDetailsFuture and orderHistoryFuture complete
                    return new UserDataAggregator.IntermediateUserData(userDetails, orderHistory);
                }, executorService)
                .thenCombineAsync(recentActivityFuture, (intermediateData, recentActivity) -> {
                    // This lambda executes after the previous combine and recentActivityFuture complete
                    return new CombinedUserData(intermediateData.userDetails, intermediateData.orderHistory, recentActivity);
                }, executorService);
    }

    // Helper class for intermediate data aggregation
    private static class UserDataAggregator {
        static class IntermediateUserData {
            UserDetails userDetails;
            List<Order> orderHistory;

            IntermediateUserData(UserDetails userDetails, List<Order> orderHistory) {
                this.userDetails = userDetails;
                this.orderHistory = orderHistory;
            }
        }
    }

    // Example usage (for demonstration)
    public static void main(String[] args) {
        UserDataService service = new UserDataService();
        String userId = "user123";

        service.getUserDataConcurrently(userId)
               .thenAccept(combinedData -> {
                   System.out.println("Successfully fetched combined data for " + userId);
                   // Process combinedData
               })
               .exceptionally(ex -> {
                   System.err.println("An error occurred: " + ex.getMessage());
                   return null; // Return null to complete exceptionally
               })
               .join(); // Wait for the future to complete

        service.executorService.shutdown(); // Properly shut down the executor
    }
}
```

A critical aspect often overlooked with `CompletableFuture` is the management of the `ExecutorService`. Failing to properly shut down or reuse an `ExecutorService` can lead to resource leaks or thread pool exhaustion, impacting application stability. In Spring Boot applications, leveraging Spring's `TaskExecutor` bean, configured and managed by the Spring context, provides a more robust and idiomatic solution. Additionally, robust error handling is paramount; methods like `exceptionally` and `handle` are essential for gracefully managing exceptions that may arise from any of the asynchronous operations in the pipeline, preventing cascading failures.

To explore more advanced patterns and error handling strategies, try asking your AI assistant for code examples demonstrating how to implement fault tolerance with retries or circuit breakers within `CompletableFuture` chains for external service calls.
