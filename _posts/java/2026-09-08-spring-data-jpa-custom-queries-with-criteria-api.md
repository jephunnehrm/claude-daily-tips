---
layout: post
title: "Spring Data JPA Custom Queries with Criteria API"
date: 2026-09-08
type: how-to
summary: "Integrate Claude Code to efficiently generate custom Spring Data JPA repository methods using the Criteria API."
image: "/claude-daily-tips/assets/images/java-2026-09-08-spring-data-jpa-custom-queries-with-criteria-api.jpg"
tags:
  - java
  - spring
  - claude-code
  - productivity
  - devtools
---



![Spring Data JPA Custom Queries with Criteria API](/claude-daily-tips/assets/images/java-2026-09-08-spring-data-jpa-custom-queries-with-criteria-api.jpg)



Navigating complex, dynamic queries in Spring Data JPA often pushes developers beyond the convenience of standard finder methods and `@Query` annotations. When you need to construct sophisticated filters based on multiple, potentially optional, conditions, the JPA Criteria API emerges as a type-safe, programmatic solution. However, its inherent verbosity can lead to tedious manual implementation and subtle, hard-to-debug errors. This is precisely where AI code assistants, like Claude Code, can significantly streamline the process by generating the intricate Criteria API logic for custom repository methods, freeing you to concentrate on core business requirements.

Consider a common scenario: fetching `Product` entities within a specific price range that are also marked as active. In a Spring Data JPA setup, you'd typically define a custom method signature in your `ProductRepository` interface (which extends `JpaRepository`) and then provide an implementation in a separate class, often named `ProductRepositoryImpl`. This `Impl` class is where the Criteria API code lives. An AI assistant can generate this implementation, including the necessary `EntityManager` setup and the predicate construction, significantly reducing boilerplate code and the risk of syntax errors.

The magic lies in how you prompt the AI. For our `Product` example, you might ask: "Generate a Java implementation for a custom Spring Data JPA repository method `findByPriceRangeAndActive` in a `ProductRepositoryImpl` class. This method should accept `BigDecimal minPrice`, `BigDecimal maxPrice`, and `Boolean isActive` as parameters. Use the JPA Criteria API to dynamically filter `Product` entities based on these parameters, applying `between` for the price range and `equal` for the active status. Assume the `Product` entity has `price` (BigDecimal) and `active` (Boolean) fields and the repository interface is `ProductRepositoryCustom`." The AI then constructs the code, leveraging the `EntityManager` and `CriteriaBuilder` to dynamically build the query's `WHERE` clause.

```java
package com.example.demo.repository.impl;

import com.example.demo.entity.Product;
import com.example.demo.repository.ProductRepositoryCustom; // Assuming this custom interface
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Repository
public class ProductRepositoryImpl implements ProductRepositoryCustom {

    @PersistenceContext
    private EntityManager entityManager;

    @Override
    public List<Product> findByPriceRangeAndActive(BigDecimal minPrice, BigDecimal maxPrice, Boolean isActive) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Product> query = cb.createQuery(Product.class);
        Root<Product> productRoot = query.from(Product.class);

        List<Predicate> predicates = new ArrayList<>();

        // Dynamically add predicates only if parameters are provided
        if (minPrice != null && maxPrice != null) {
            predicates.add(cb.between(productRoot.get("price"), minPrice, maxPrice));
        } else if (minPrice != null) {
            predicates.add(cb.greaterThanOrEqualTo(productRoot.get("price"), minPrice));
        } else if (maxPrice != null) {
            predicates.add(cb.lessThanOrEqualTo(productRoot.get("price"), maxPrice));
        }

        if (isActive != null) {
            predicates.add(cb.equal(productRoot.get("active"), isActive));
        }

        // Ensure query.where only receives predicates if any are present
        if (!predicates.isEmpty()) {
            query.where(predicates.toArray(new Predicate[0]));
        }

        return entityManager.createQuery(query).getResultList();
    }
}
```

A critical "gotcha" developers must remain vigilant about, even with AI-generated code, is the precise handling of null or optional input parameters. The Criteria API, by its nature, builds query components conditionally. If not carefully implemented, leaving predicates for `null` parameters can lead to unexpected query results (e.g., filtering by a `null` price range) or even runtime `NullPointerException`s. Always meticulously review the generated code to ensure that predicates are only added when their corresponding parameters are genuinely present, and that the `query.where()` clause is correctly applied. This diligent review is what elevates AI assistance from a code generator to a true development accelerator.
