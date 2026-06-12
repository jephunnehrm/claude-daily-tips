---
layout: post
title: "Refactor `synchronized` Blocks with Concurrent Data Structures"
date: 2026-06-12
type: how-to
summary: "Improve performance and reduce contention by replacing `synchronized` blocks with `ConcurrentHashMap` and `AtomicReference`."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - devtools
  - claude-code
  - productivity
---



![Refactor `synchronized` Blocks with Concurrent Data Structures](assets/images/placeholder.jpg)



Excessive reliance on `synchronized` blocks is a common performance bottleneck for many Java developers. While `synchronized` offers a simple path to thread safety, it can severely limit throughput in high-concurrency scenarios. This often occurs when managing shared mutable state, such as counters or caches, where a lock is held for an extended period, preventing other threads from proceeding. Refactoring these `synchronized` blocks to utilize more granular, non-blocking, or lock-free concurrent data structures can unlock significant performance improvements.

Consider the common task of thread-safely managing a map for updates and retrievals. Instead of synchronizing access to a standard `HashMap`, `java.util.concurrent.ConcurrentHashMap` is a highly optimized alternative. It allows multiple threads to read and write concurrently without blocking each other, provided the operations don't conflict. For managing a single mutable variable, like a version number or status flag, `java.util.concurrent.atomic.AtomicReference` or `AtomicInteger` offer an efficient, lock-free replacement for `synchronized`.

Let's demonstrate with a typical scenario: tracking counts for distinct elements. A naive approach might use a `HashMap` guarded by a `synchronized` block.

```java
import java.util.HashMap;
import java.util.Map;

public class CounterService {
    private final Map<String, Integer> counts = new HashMap<>();

    public void increment(String key) {
        synchronized (this) {
            counts.put(key, counts.getOrDefault(key, 0) + 1);
        }
    }

    public int get(String key) {
        synchronized (this) {
            return counts.getOrDefault(key, 0);
        }
    }
}
```

We can refactor this to leverage `ConcurrentHashMap` and `AtomicInteger` for superior concurrency. The `ConcurrentHashMap`'s `computeIfAbsent` method is key here: it atomically checks if a key exists and, if not, creates a new `AtomicInteger` for it. Then, `incrementAndGet()` on the `AtomicInteger` efficiently updates the count lock-free.

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class ConcurrentCounterService {
    private final ConcurrentHashMap<String, AtomicInteger> counts = new ConcurrentHashMap<>();

    public void increment(String key) {
        // Atomically gets or creates an AtomicInteger and then increments it.
        counts.computeIfAbsent(key, k -> new AtomicInteger(0)).incrementAndGet();
    }

    public int get(String key) {
        AtomicInteger count = counts.get(key);
        return (count == null) ? 0 : count.get();
    }
}
```

A crucial aspect of this migration is understanding the semantics of concurrent structures. While `ConcurrentHashMap` and `Atomic*` classes offer significant gains, operations requiring atomic updates across *multiple* keys or complex logic with side effects within an update still demand careful consideration. In such advanced cases, a carefully managed `synchronized` block might remain the most appropriate solution, or exploring more sophisticated concurrency utilities like `java.util.concurrent.locks.StampedLock` for read-heavy scenarios might be necessary.

**Try it:** You can explore identifying these patterns with tools like Claude Code. Use the command `claude refactor --pattern synchronized-block --suggestion concurrent-map --source <your-java-file.java>` to get suggestions for replacing `synchronized` blocks.
