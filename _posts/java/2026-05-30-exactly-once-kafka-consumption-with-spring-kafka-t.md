---
layout: post
title: "Exactly-Once Kafka Consumption with Spring Kafka Transactions"
date: 2026-05-30
type: how-to
summary: "Achieve exactly-once processing guarantees in your Spring Kafka consumers using transactional capabilities."
image: "/claude-daily-tips/assets/images/java-2026-05-30-exactly-once-kafka-consumption-with-spring-kafka-t.jpg"
tags:
  - java
  - spring
  - devtools
---



![Exactly-Once Kafka Consumption with Spring Kafka Transactions](/claude-daily-tips/assets/images/java-2026-05-30-exactly-once-kafka-consumption-with-spring-kafka-t.jpg)



Many Java developers grapple with the persistent challenge of ensuring Kafka messages are processed *exactly once*. The default at-least-once delivery semantics, while robust, can lead to duplicate message processing if consumers crash mid-operation, forcing developers to implement complex, error-prone idempotency logic. Spring Kafka, however, elegantly bridges this gap by leveraging Kafka's native transactional capabilities, seamlessly integrated with Spring's declarative transaction management. This allows us to atomically group the consumption of a Kafka message with subsequent actions, such as producing another message to a different topic or updating a transactional data store.

The magic behind exactly-once processing with Spring Kafka lies in configuring your transaction-aware components. This typically involves setting up your `KafkaTemplate` with a transactional `ProducerFactory` and configuring your `ConcurrentKafkaListenerContainerFactory` to use a `KafkaTransactionManager`. The listener method itself is then annotated with `@Transactional`. This annotation signals to Spring that the listener's execution, including any Kafka sends performed by the injected `KafkaTemplate`, should be managed as a single, atomic transaction. If the listener method completes successfully, Spring Kafka will orchestrate the commit of the Kafka transaction. Conversely, if any `RuntimeException` is thrown within the `@Transactional` method, Spring will trigger a rollback, ensuring that neither the consumption nor any produced messages are permanently committed to Kafka.

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TransactionalKafkaService {

    private final KafkaTemplate<String, String> kafkaTemplate;

    @Autowired
    public TransactionalKafkaService(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    // The @Transactional annotation ensures this listener's execution
    // is part of a transactional boundary.
    @Transactional
    @KafkaListener(topics = "input-topic", groupId = "my-group")
    public void processAndForward(String message, @Header(KafkaHeaders.OFFSET) long offset) {
        System.out.println("Received message: " + message + " with offset: " + offset);

        // Simulate a business process that might fail.
        // If this throws an exception, the entire transaction will be rolled back.
        if (message.contains("failure")) {
            throw new RuntimeException("Simulated processing failure for message: " + message);
        }

        // Produce to an output topic. This send operation is included in the transaction.
        // If the transaction commits, this message will be visible to downstream consumers.
        // If it rolls back, this message will not be sent.
        kafkaTemplate.send("output-topic", "Processed successfully: " + message);

        System.out.println("Successfully processed and enqueued for output: " + message);
    }
}
```

It's crucial to understand that true end-to-end exactly-once semantics extend beyond Kafka itself. While Spring Kafka transactions guarantee atomicity between Kafka consumption and production (or state updates managed by `KafkaTransactionManager`), this guarantee is broken if your transaction interacts with non-transactional external systems. For instance, if your `@Transactional` method successfully commits its Kafka transaction but fails to update a non-transactional database, you'll still face data inconsistency. Furthermore, Kafka transactions introduce inherent overhead and latency compared to non-transactional producers. Therefore, meticulously evaluate if the complexity and performance implications are truly justified for your specific use case.

To experiment, configure a `KafkaTemplate` with a transactional `ProducerFactory` and a `KafkaTransactionManager` within your Spring Boot application. Then, annotate a `@KafkaListener` method with `@Transactional` and simulate both successful processing and processing that throws an exception. Observe how Kafka offsets are managed and how messages are or are not delivered to the output topic, paying close attention to the behavior during failures.
