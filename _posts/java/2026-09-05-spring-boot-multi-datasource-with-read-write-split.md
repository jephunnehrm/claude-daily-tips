---
layout: post
title: "Spring Boot Multi-Datasource with Read-Write Splitting"
date: 2026-09-05
type: how-to
summary: "Configure Spring Boot to use separate data sources for reads and writes, improving performance and scalability."
image: "/claude-daily-tips/assets/images/java-2026-09-05-spring-boot-multi-datasource-with-read-write-split.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
  - productivity
---



![Spring Boot Multi-Datasource with Read-Write Splitting](/claude-daily-tips/assets/images/java-2026-09-05-spring-boot-multi-datasource-with-read-write-split.jpg)



As a Java developer working with Spring Boot, you've likely faced performance bottlenecks in database-intensive applications. For read-heavy workloads, a common and effective strategy is read-write splitting: directing read operations to replica databases and write operations to the primary. This dramatically alleviates pressure on your write instance. While Spring Boot offers the building blocks, manually orchestrating multiple `DataSource` beans and a dynamic routing mechanism can introduce significant boilerplate and complexity.

The core of achieving read-write splitting in Spring Boot lies in defining separate `DataSource` beans for your primary (write) and replica (read) databases. Then, you configure a `RoutingDataSource`, a Spring abstraction that dynamically selects a target `DataSource` based on a lookup key. This key is determined by the nature of the current operation – whether it's a read or a write. The `AbstractRoutingDataSource` class provides the framework for this, requiring you to implement the `determineCurrentLookupKey()` method to dictate this selection logic.

Here's a robust example illustrating the configuration. The crucial element is the `determineCurrentLookupKey()` method within our custom `RoutingDataSource`. Instead of relying on a simplified `ThreadLocal` for demonstration, a production-ready solution will leverage Spring's `TransactionSynchronizationManager`. This allows you to inspect the transaction's read-only status, which Spring correctly manages when using methods annotated with `@Transactional(readOnly = true)` or when Spring Data JPA infers read-only transactions.

```java
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy;
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class ReadWriteSplittingConfig {

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.write")
    public DataSourceProperties writeDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    public DataSource writeDataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.read")
    public DataSourceProperties readDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    public DataSource readDataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }

    @Bean
    public DataSource dataSource(
            @Qualifier("writeDataSource") DataSource writeDataSource,
            @Qualifier("readDataSource") DataSource readDataSource) {

        final RoutingDataSource routingDataSource = new RoutingDataSource();

        Map<Object, Object> dataSourceMap = new HashMap<>();
        dataSourceMap.put("write", writeDataSource);
        dataSourceMap.put("read", readDataSource);

        routingDataSource.setTargetDataSources(dataSourceMap);
        routingDataSource.setDefaultTargetDataSource(writeDataSource); // Fallback to write datasource
        routingDataSource.afterPropertiesSet();

        return new LazyConnectionDataSourceProxy(routingDataSource);
    }

    @Bean
    public DataSourceTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }

    private static class RoutingDataSource extends AbstractRoutingDataSource {
        @Override
        protected Object determineCurrentLookupKey() {
            // TransactionSynchronizationManager is the key for robust read/write detection.
            // It correctly reflects the read-only status set by Spring's transaction management.
            return TransactionSynchronizationManager.isCurrentTransactionReadOnly() ? "read" : "write";
        }
    }
}
```

A critical "gotcha" is accurately determining the read-only nature of a transaction. Relying on manual flags or simplistic `ThreadLocal`s is fragile and error-prone. The power of Spring's transaction management, specifically `TransactionSynchronizationManager`, provides a robust, context-aware mechanism. By configuring your read-only methods with `@Transactional(readOnly = true)`, or allowing Spring Data JPA to infer it, the `determineCurrentLookupKey()` method can reliably distinguish between read and write operations, ensuring the correct `DataSource` is selected without developer intervention in service methods. This approach goes beyond basic Spring documentation by demonstrating a production-ready implementation that leverages core Spring transaction features for reliable dynamic data source routing.
