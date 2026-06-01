---
layout: post
title: "Configure Spring Boot Multi-Datasource for Read-Write Split"
date: 2026-06-01
type: how-to
summary: "Implement efficient read-write splitting in Spring Boot using Claude Code for dynamic datasource management."
image: "/claude-daily-tips/assets/images/java-2026-06-01-configure-spring-boot-multi-datasource-for-read-wr.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
  - productivity
---



![Configure Spring Boot Multi-Datasource for Read-Write Split](/claude-daily-tips/assets/images/java-2026-06-01-configure-spring-boot-multi-datasource-for-read-wr.jpg)



When your Spring Boot application faces a high volume of read operations, directing those queries to dedicated read replicas offers a significant performance boost and alleviates pressure on your primary write database. While manually configuring multiple `DataSource` beans and implementing custom routing logic is feasible, it quickly becomes a maintenance burden, especially as your read replica topology scales. This is precisely where understanding Spring's built-in mechanisms for multi-datasource configurations, particularly `AbstractRoutingDataSource`, becomes essential.

The core principle behind read-write splitting in Spring Boot involves defining distinct `DataSource` beans: one for write operations (your master database) and one or more for read operations (your replicas). Spring's `AbstractRoutingDataSource` acts as the central orchestrator. You then provide a custom implementation for the `determineCurrentLookupKey()` method. This method, which is invoked before each data access operation, inspects the current context and returns a key that maps to the appropriate `DataSource` defined in your configuration. By returning "read" or "write" (or similar keys) based on the operation type or transaction context, you effectively steer traffic to the correct database.

To illustrate, consider the following Java configuration. This class defines an `AbstractRoutingDataSource` that dynamically selects a `DataSource` based on whether the current transaction is marked as read-only. If `TransactionSynchronizationManager.isCurrentTransactionReadOnly()` returns `true`, the operation is routed to the "read" data source; otherwise, it defaults to the "write" data source. This approach leverages the transactional metadata provided by Spring to intelligently route database calls without requiring explicit annotation on every repository method.

```java
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy;
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class ReadWriteRoutingDataSourceConfig {

    // Assuming these are configured in application.properties or application.yml
    // For example:
    // spring.datasource.master.url=jdbc:mysql://localhost:3306/write_db
    // spring.datasource.master.username=user
    // spring.datasource.master.password=password
    // spring.datasource.replica.url=jdbc:mysql://localhost:3306/read_db
    // spring.datasource.replica.username=user
    // spring.datasource.replica.password=password

    private final DataSourceProperties dataSourceProperties;

    public ReadWriteRoutingDataSourceConfig(DataSourceProperties dataSourceProperties) {
        this.dataSourceProperties = dataSourceProperties;
    }

    @Bean(name = "masterDataSource")
    public DataSource masterDataSource() {
        return dataSourceProperties.initializeDataSourceBuilder().build();
    }

    @Bean(name = "replicaDataSource")
    public DataSource replicaDataSource() {
        // In a real-world scenario, you'd configure replica-specific properties here
        // For simplicity, we're reusing the primary DataSourceProperties, but
        // you'd typically load distinct replica properties from your configuration.
        // Example: DataSourceProperties replicaProps = new DataSourceProperties();
        // replicaProps.setUrl("jdbc:mysql://localhost:3306/read_db");
        // ... etc.
        return dataSourceProperties.initializeDataSourceBuilder().build();
    }

    @Bean
    public DataSource routingDataSource(
            @Qualifier("masterDataSource") DataSource masterDataSource,
            @Qualifier("replicaDataSource") DataSource replicaDataSource) {

        ReadWriteFilteringDataSource routingDataSource = new ReadWriteFilteringDataSource();

        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("write", masterDataSource);
        targetDataSources.put("read", replicaDataSource);

        routingDataSource.setTargetDataSources(targetDataSources);
        routingDataSource.setDefaultTargetDataSource(masterDataSource); // Default to master for safety

        // Wrap with LazyConnectionDataSourceProxy for potential performance gains if connection pooling is managed externally
        return new LazyConnectionDataSourceProxy(routingDataSource);
    }

    private static class ReadWriteFilteringDataSource extends AbstractRoutingDataSource {
        @Override
        protected Object determineCurrentLookupKey() {
            // If the current transaction is marked as read-only, use the replica.
            if (TransactionSynchronizationManager.isCurrentTransactionReadOnly()) {
                return "read";
            }
            // Otherwise, default to the master for write operations.
            return "write";
        }
    }
}
```

A critical gotcha to be mindful of is the interaction between transactional annotations and this routing strategy. If a method is annotated with `@Transactional(readOnly = true)` but unexpectedly executes a write operation (e.g., due to an ORM's lazy loading or an internal helper method call), the `AbstractRoutingDataSource` will still direct it to the "read" data source. This can lead to `SQLFeatureNotSupportedException` if the replica doesn't support writes or, more subtly, data inconsistency if writes are attempted on stale data. Always ensure your `@Transactional` annotations accurately reflect the *actual* operations performed within the annotated methods.
