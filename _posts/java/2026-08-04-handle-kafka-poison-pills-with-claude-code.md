---
layout: post
title: "Handle Kafka Poison Pills with Claude Code"
date: 2026-08-04
type: how-to
summary: "Quickly create a robust dead-letter topic handler for Kafka poison-pill messages in Spring Boot."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
---



![Handle Kafka Poison Pills with Claude Code](assets/images/placeholder.jpg)



Ever stared at Kafka logs, unraveling the mystery of a message that repeatedly fails, clogging your consumer and halting your processing pipeline? This "poison pill" scenario, where malformed or unprocessable messages cause endless retry loops, is a significant operational headache for any Java developer managing Kafka streams. Manually crafting robust dead-letter topic handlers, complete with detailed error logging and sophisticated re-processing logic, is not only time-consuming but also prone to errors, especially when under pressure.

Leveraging an AI coding assistant like Claude Code can dramatically accelerate the development of a Spring Boot-based Kafka listener designed to gracefully handle these poison pills. By providing a well-defined prompt, you can instruct Claude Code to generate the necessary configuration and listener logic to reroute problematic messages to a designated dead-letter topic, effectively isolating them from your main processing flow without blocking legitimate data. This typically involves setting up a `DeadLetterPublishingRecoverer` and configuring your `KafkaListenerContainerFactory` to integrate with it.

Here’s a conceptual prompt for Claude Code and a snippet of the resultant Java code. Remember to adapt the topic names and error handling strategies to your application's specific requirements.

```java
package com.example.kafka.listener;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer;
import org.springframework.kafka.listener.ListenerExecutionFailedException;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

@Component
public class PoisonPillKafkaListener {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final String deadLetterTopic;

    public PoisonPillKafkaListener(KafkaTemplate<String, String> kafkaTemplate,
                                   @Value("${kafka.dead-letter-topic}") String deadLetterTopic) {
        this.kafkaTemplate = kafkaTemplate;
        this.deadLetterTopic = deadLetterTopic;
    }

    @KafkaListener(topics = "${kafka.main-topic}", groupId = "my-consumer-group")
    public void listen(ConsumerRecord<String, String> record, Acknowledgment acknowledgment) {
        try {
            System.out.println("Processing message: " + record.value());
            // Your message processing logic here.
            // For demonstration, simulate a poison pill:
            if (record.value().contains("corrupt")) {
                throw new IllegalArgumentException("Encountered corrupt message data");
            }
            acknowledgment.acknowledge(); // Acknowledge only if processing succeeds.
        } catch (Exception e) {
            System.err.println("Error processing message: " + record.value() + ", error: " + e.getMessage());
            // Re-throw as ListenerExecutionFailedException to trigger container error handling.
            throw new ListenerExecutionFailedException("Failed to process message, delegating to DLQ recovery", e, record);
        }
    }

    // This recoverer is used by the KafkaListenerContainerFactory.
    public DeadLetterPublishingRecoverer recoverer() {
        return (consumerRecord, exception) -> {
            System.out.println("Recovering message to DLQ: " + consumerRecord.value() + ", original error: " + exception.getMessage());
            // Send the failed message to the dead-letter topic.
            kafkaTemplate.send(deadLetterTopic, consumerRecord.value());
        };
    }
}
```

A critical detail often missed is that simply throwing an exception within your `@KafkaListener` method doesn't automatically send the message to the dead-letter topic. The `KafkaListenerContainerFactory` must be explicitly configured to use a `DeadLetterPublishingRecoverer`. This `Recoverer` is the component that intercepts exceptions thrown by the listener and orchestrates sending the problematic `ConsumerRecord` to the designated dead-letter topic, often with added headers indicating the failure reason. Without this container-level configuration, your poison pills will continue to be retried by the listener.

To truly grasp this, set up a Spring Boot application with a Kafka producer sending messages to a topic, and a consumer listening to it. Introduce a deliberate processing failure (e.g., a malformed JSON, an unexpected data type, or a business rule violation) for specific messages. Then, observe how your configured `DeadLetterPublishingRecoverer`, integrated into the `KafkaListenerContainerFactory`, intercepts these failures and diverts the offending messages to your dead-letter topic, preventing them from endlessly retrying and blocking your main consumer group. This approach not only ensures message processing resilience but also provides a crucial audit trail of problematic messages.
