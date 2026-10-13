---
layout: post
title: "JPA Criteria API Queries with Claude Code"
date: 2026-10-13
type: how-to
summary: "Enhance Spring Data repositories with custom JPA Criteria API queries using Claude Code for complex filtering."
image: "/claude-daily-tips/assets/images/java-2026-10-13-jpa-criteria-api-queries-with-claude-code.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
  - productivity
---



![JPA Criteria API Queries with Claude Code](/claude-daily-tips/assets/images/java-2026-10-13-jpa-criteria-api-queries-with-claude-code.jpg)



When you need to perform dynamic, complex queries that go beyond the capabilities of Spring Data's derived query methods, the JPA Criteria API offers a robust, type-safe solution. However, crafting these queries manually can quickly become verbose, error-prone, and difficult to maintain, often obscuring the intent of the query. This is where AI assistants like Claude Code can significantly streamline the process, helping you define custom repository methods that leverage the Criteria API with dramatically less boilerplate. Imagine needing to find all `Order` entities placed by a specific customer, where the order total exceeds a certain threshold, and the order status is not 'CANCELLED'. A standard Criteria API implementation can easily stretch into dozens of lines, making it a chore to write and debug.

Claude Code can assist in generating the necessary boilerplate for your custom repository implementation. The typical pattern involves an interface extending `JpaRepository` (or a similar Spring Data interface), alongside a custom interface defining your new method. You then create an implementation class for this custom interface, where the Criteria API logic resides. Claude Code can help draft the structure of this implementation class and the Criteria API query itself, based on your natural language description of the desired query, saving you from tedious manual setup and common syntax mistakes.

Here’s an example of how you might ask Claude Code to help implement a custom method for finding orders by customer and minimum total, excluding a specific status. Notice how Claude Code generates the `CriteriaBuilder`, `CriteriaQuery`, `Root`, and the initial predicate setup, allowing you to focus on refining the query logic:

```java
// In your repository interface:
public interface OrderRepository extends JpaRepository<Order, Long>, OrderRepositoryCustom {
}

// In your custom repository interface:
public interface OrderRepositoryCustom {
    List<Order> findOrdersByCustomerAndMinTotalExcludingStatus(Long customerId, BigDecimal minTotal, OrderStatus excludedStatus);
}

// In your implementation class (using Claude Code assistance):
@Repository
public class OrderRepositoryImpl implements OrderRepositoryCustom {

    @PersistenceContext
    private EntityManager entityManager;

    @Override
    public List<Order> findOrdersByCustomerAndMinTotalExcludingStatus(Long customerId, BigDecimal minTotal, OrderStatus excludedStatus) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Order> query = cb.createQuery(Order.class);
        Root<Order> orderRoot = query.from(Order.class);

        List<Predicate> predicates = new ArrayList<>();
        // Claude Code helps generate these lines based on the natural language request:
        predicates.add(cb.equal(orderRoot.get("customer").get("id"), customerId));
        predicates.add(cb.greaterThanOrEqualTo(orderRoot.get("totalAmount"), minTotal));
        predicates.add(cb.notEqual(orderRoot.get("status"), excludedStatus));

        query.where(predicates.toArray(new Predicate[0]));
        return entityManager.createQuery(query).getResultList();
    }
}
```

A common gotcha when using the Criteria API directly is managing complex join conditions or handling nullable fields robustly. While Claude Code can help generate the basic query structure, you still need to review and ensure the join paths are correct, especially in entities with many-to-one or one-to-many relationships. For instance, incorrectly specifying a join path can lead to `NullPointerException`s or inefficient queries. You must also ensure that predicates correctly handle potential `null` values if your business logic requires it, for example, by using `cb.isNull()` or `cb.isNotNull()`. The generated code will be functional for straightforward cases, but a deep understanding of your entity relationships and nullability is crucial for complex scenarios and robust error handling.

This approach works because the Criteria API builds a `javax.persistence.criteria.CriteriaQuery` object programmatically. The `CriteriaBuilder` acts as a factory for creating query components like expressions and predicates. By chaining these components, we construct a fully defined query that the `EntityManager` can then translate into SQL. Claude Code's value lies in its ability to understand your natural language request and translate it into this programmatic structure, significantly reducing the cognitive load and the likelihood of syntactic errors. While Spring Data's documentation is excellent for standard use cases, it doesn't offer AI-driven assistance for generating complex Criteria API implementations, which is where this tool provides a tangible advantage for senior developers facing intricate dynamic query requirements.

**Try it:** Ask Claude Code to help you write a custom Spring Data JPA repository method using the Criteria API to find all `Product` entities whose `price` is within a specified range and are marked as 'AVAILABLE'.
