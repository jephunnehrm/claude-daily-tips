---
layout: post
title: "Untangle `synchronized` Blocks with Concurrent Collections"
date: 2026-07-18
type: how-to
summary: "Replace slow `synchronized` blocks with efficient concurrent data structures for better application performance."
image: "/claude-daily-tips/assets/images/java-2026-07-18-untangle--synchronized--blocks-with-concurrent-col.jpg"
tags:
  - java
  - spring
  - devtools
  - productivity
---



![Untangle `synchronized` Blocks with Concurrent Collections](/claude-daily-tips/assets/images/java-2026-07-18-untangle--synchronized--blocks-with-concurrent-col.jpg)



Java developers frequently grapple with performance bottlenecks arising from shared mutable state in high-concurrency applications, particularly within Spring Boot environments. The traditional solution, `synchronized` blocks or methods, ensures thread safety but often becomes a major contention point. This widespread reliance on coarse-grained locking can lead to threads blocking each other unnecessarily, severely impacting scalability when multiple threads attempt to access or modify shared resources simultaneously.

Consider the common task of tracking the frequency of processed items. A naive approach might involve a `HashMap` wrapped by `Collections.synchronizedMap()`, where the entire map is locked for every single operation, even if threads are working on entirely different keys. This is highly inefficient. A more robust and performant alternative is `java.util.concurrent.ConcurrentHashMap`. This specialized collection provides fine-grained, lock-free (or very low-contention) access to individual map entries. Multiple threads can safely read and write to distinct parts of the map concurrently. For managing counts, we can further enhance this by pairing `ConcurrentHashMap` with `AtomicLong` to atomically update individual item counts.

Here's a practical refactoring demonstrating this shift from a `synchronized` block to a concurrent collection:

```java
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.ConcurrentHashMap;

public class ItemCounter {

    // Old, potentially slow way
    private Map<String, Integer> synchronizedItemCounts = Collections.synchronizedMap(new HashMap<>());
    private int totalSynchronizedItems = 0;

    public synchronized void addItemSynchronized(String item) {
        synchronizedItemCounts.put(item, synchronizedItemCounts.getOrDefault(item, 0) + 1);
        totalSynchronizedItems++;
    }

    // New, concurrent way
    private final ConcurrentHashMap<String, AtomicLong> concurrentItemCounts = new ConcurrentHashMap<>();
    private final AtomicLong totalConcurrentItems = new AtomicLong(0);

    public void addItemConcurrent(String item) {
        concurrentItemCounts.computeIfAbsent(item, k -> new AtomicLong(0)).incrementAndGet();
        totalConcurrentItems.incrementAndGet();
    }

    public int getTotalSynchronizedItems() {
        return totalSynchronizedItems;
    }

    public long getTotalConcurrentItems() {
        return totalConcurrentItems.get();
    }

    public Map<String, AtomicLong> getConcurrentItemCounts() {
        return concurrentItemCounts;
    }
}
```

The underlying principle behind `ConcurrentHashMap`'s performance gain is its segmented locking or, in newer versions, its more advanced non-blocking techniques. Instead of a single lock protecting the entire map, it manages locks (or other concurrency control mechanisms) on smaller segments. This allows threads operating on different segments to proceed without blocking each other. For incrementing operations on individual counts, `AtomicLong` guarantees that updates are performed atomically, preventing race conditions without explicit `synchronized` blocks.

However, even with these powerful concurrent collections, developers must remain vigilant. `ConcurrentHashMap` does not guarantee element ordering during iteration, which can be a surprise if your logic relies on it. More critically, operations that require atomic updates across *multiple* keys or complex conditional logic that cannot be expressed via methods like `compute` or `merge` will still necessitate careful consideration. In such nuanced scenarios, you might need to introduce a smaller, more targeted `synchronized` block, locking only the critical section of code that accesses multiple concurrent map entries, thereby minimizing the scope of contention.
