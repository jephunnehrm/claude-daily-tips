---
layout: post
title: "Handle Poison Pill Kafka Messages with Claude Code"
date: 2026-10-26
type: how-to
summary: "Quickly create a robust dead-letter handler for Kafka poison pill messages using Claude Code."
image: "/claude-daily-tips/assets/images/java-2026-10-26-handle-poison-pill-kafka-messages-with-claude-code.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
---



![Handle Poison Pill Kafka Messages with Claude Code](/claude-daily-tips/assets/images/java-2026-10-26-handle-poison-pill-kafka-messages-with-claude-code.jpg)



Ever encountered the dreaded "poison pill" message in Kafka – a message that repeatedly causes your consumer to fail, blocking your entire partition? Manually crafting robust error handling for these scenarios, especially for dead-letter queues (DLQs), can be tedious and error-prone. You need a reliable way to identify, isolate, and process these problematic messages without disrupting your main consumer flow.

Leveraging LLMs like Claude can significantly expedite the creation of a dedicated Kafka listener for handling "poison pill" messages. By clearly defining the problem – a message that consistently fails processing and needs to be offloaded after a set number of retries – you can prompt Claude to generate the necessary Spring Boot configurations and listener logic. The generated code will typically implement a `KafkaListener` with retry mechanisms, ultimately moving messages that exceed a retry count to a designated dead-letter topic. This approach works by using Spring Kafka's built-in retry capabilities and an external `KafkaTemplate` to manually dispatch to the DLQ.

Here's an example of how you might prompt Claude to generate such a handler. You would typically provide context about your existing Kafka setup, including your `KafkaTemplate` and the desired DLQ topic name.

```java
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class PoisonPillHandler {

    private static final Logger logger = LoggerFactory.getLogger(PoisonPillHandler.class);
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final String deadLetterTopic;
    private static final int MAX_RETRIES = 3; // Configurable retry count

    public PoisonPillHandler(KafkaTemplate<String, String> kafkaTemplate,
                             @Value("${kafka.dlq.topic}") String deadLetterTopic) {
        this.kafkaTemplate = kafkaTemplate;
        this.deadLetterTopic = deadLetterTopic;
    }

    @KafkaListener(topics = "${kafka.main.topic}", groupId = "poison-pill-group")
    public void handleMessage(String message, Acknowledgment acknowledgment,
                              @Header(KafkaHeaders.DELIVERY_ATTEMPT) int deliveryAttempt) {
        try {
            logger.info("Attempt {} to process message: {}", deliveryAttempt, message);
            // --- Your core message processing logic goes here ---
            // For demonstration, we simulate a failure for messages containing "POISON"
            if (message != null && message.contains("POISON")) {
                throw new RuntimeException("Simulated poison pill failure for message: " + message);
            }
            // --- End of core message processing logic ---

            logger.debug("Message processed successfully: {}", message);
            acknowledgment.acknowledge(); // Acknowledge only on successful processing
        } catch (Exception e) {
            logger.error("Error processing message: {}", message, e);

            if (deliveryAttempt >= MAX_RETRIES) {
                logger.warn("Message failed after {} retries. Sending to DLQ: {}", MAX_RETRIES, message);
                // Sending to DLQ and acknowledging allows the message to be removed from the main topic.
                kafkaTemplate.send(deadLetterTopic, message);
                acknowledgment.acknowledge();
            } else {
                logger.debug("Retrying message. Current attempt: {}, Max retries: {}", deliveryAttempt, MAX_RETRIES);
                // Do NOT acknowledge. This allows Kafka's redelivery mechanism to kick in.
                // If you needed more sophisticated re-queuing (e.g., backoff), you'd implement that here.
            }
        }
    }
}
```

A crucial gotcha when implementing DLQ handlers, particularly with Spring Kafka's `Acknowledgment`, is managing acknowledgments. You *must* ensure that a message is only acknowledged *after* it has been either successfully processed *or* definitively moved to the dead-letter topic. Failing to acknowledge a message that's then sent to the DLQ will result in it being re-processed by the *main* consumer indefinitely because Kafka will assume the processing failed and attempt redelivery. Ensure your acknowledgment logic is tightly coupled to successful DLQ dispatch or successful final processing. This pattern goes beyond basic Spring Kafka documentation by illustrating a common, intricate error-handling scenario and providing a practical, LLM-assisted solution.
