---
layout: post
title: "Improve Cache Performance: ConcurrentHashMap Over synchronized"
date: 2026-10-23
type: how-to
summary: "Unlock faster concurrent access to shared mutable state in your Spring Boot app by replacing `synchronized` blocks with `ConcurrentHashMap`."
image: "/claude-daily-tips/assets/images/java-2026-10-23-improve-cache-performance--concurrenthashmap-over.jpg"
tags:
  - java
  - spring
  - devtools
  - productivity
---



![Improve Cache Performance: ConcurrentHashMap Over synchronized](/claude-daily-tips/assets/images/java-2026-10-23-improve-cache-performance--concurrenthashmap-over.jpg)



As Java developers, we frequently grapple with the challenge of managing shared, mutable state concurrently. While `synchronized` blocks offer a straightforward path to thread safety, their coarse-grained nature can quickly become a performance bottleneck in high-concurrency scenarios. Each thread waiting for a lock on a shared resource, such as a `HashMap` in a cache, serializes access, reducing overall application throughput. This contention is particularly problematic in a typical in-memory cache where multiple threads might simultaneously attempt to retrieve or update entries.

`java.util.concurrent.ConcurrentHashMap` emerges as a superior alternative for thread-safe map operations. It employs a segmented locking strategy, allowing multiple threads to operate on different segments of the map concurrently. This fine-grained control significantly reduces lock contention, leading to improved performance, especially under heavy load. For managing single, atomically updatable values outside of a map context, `java.util.concurrent.atomic.AtomicReference` provides atomic operations like `compareAndSet` and `getAndSet`, offering thread-safe manipulation of individual objects.

Consider a practical scenario: an in-memory cache for `User` objects. Instead of synchronizing access to a standard `HashMap<String, User>`, we can leverage `ConcurrentHashMap`. Furthermore, if we need to atomically track cache misses, combining `ConcurrentHashMap` with an `AtomicLong` is an elegant solution. The `getUser` method demonstrates this pattern: it attempts to retrieve a user from the cache. If a miss occurs, it atomically increments a `cacheMisses` counter and then fetches and caches the user.

```java
import org.springframework.stereotype.Service;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.Objects; // Import for Objects.requireNonNull

@Service
public class UserService {

    private final ConcurrentHashMap<String, User> userCache = new ConcurrentHashMap<>();
    private final AtomicLong cacheMisses = new AtomicLong(0);

    public User getUser(String userId) {
        // Attempt to retrieve from cache, leveraging ConcurrentHashMap's efficiency.
        User user = userCache.get(userId);
        if (user == null) {
            // This block executes only if the key is truly absent.
            // Simulate a cache miss and fetch from a "database".
            System.out.println("Cache miss for user: " + userId);
            cacheMisses.incrementAndGet(); // Atomically increment the miss count.
            user = fetchUserFromDatabase(userId); // Replace with actual DB call.
            if (user != null) {
                // putIfAbsent is an atomic operation.
                userCache.putIfAbsent(userId, user);
            }
        }
        return user;
    }

    // Simulate fetching user from a database.
    private User fetchUserFromDatabase(String userId) {
        // In a real application, this would be a database interaction.
        // For demonstration purposes, returning a dummy user.
        try {
            Thread.sleep(50); // Simulate network or disk latency.
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        // Return null for demonstration if needed, or a new user.
        // Returning a new user for this example.
        return new User(userId, "User " + userId);
    }

    public long getCacheMissCount() {
        return cacheMisses.get();
    }

    // Dummy User class for demonstration.
    // Ensure it's Serializable if used in distributed caches.
    static class User {
        private final String id;
        private final String name;

        public User(String id, String name) {
            this.id = Objects.requireNonNull(id, "User ID cannot be null");
            this.name = Objects.requireNonNull(name, "User name cannot be null");
        }

        public String getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            User user = (User) o;
            return Objects.equals(id, user.id);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id);
        }
    }
}
```

A crucial advantage of `ConcurrentHashMap` is its predictable performance under high concurrency, outperforming synchronized `HashMap`s significantly. However, developers must be aware of a common pitfall: while individual operations like `get` and `put` are atomic, sequences of operations requiring atomicity (e.g., checking for a key's existence and then inserting it only if absent) necessitate specific methods. For such compound operations, `ConcurrentHashMap` offers `compute` and `merge` methods. Alternatively, if dealing with a single value where `compareAndSet` semantics are needed, `AtomicReference` is the appropriate tool. This distinction is vital for maintaining data integrity in concurrent environments.
