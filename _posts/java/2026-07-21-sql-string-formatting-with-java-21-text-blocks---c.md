---
layout: post
title: "SQL String Formatting with Java 21 Text Blocks & Claude Code"
date: 2026-07-21
type: how-to
summary: "Use Java 21 text blocks and Claude Code for readable, maintainable SQL strings in your Spring Boot apps."
image: "/claude-daily-tips/assets/images/java-2026-07-21-sql-string-formatting-with-java-21-text-blocks---c.jpg"
tags:
  - java
  - spring
  - claude-code
  - productivity
  - devtools
---



![SQL String Formatting with Java 21 Text Blocks & Claude Code](/claude-daily-tips/assets/images/java-2026-07-21-sql-string-formatting-with-java-21-text-blocks---c.jpg)



Crafting dynamic SQL queries in Java, especially within a Spring Boot environment, can quickly descend into a tangled mess of string concatenation and cumbersome escape characters. This problem is amplified for multi-line SQL statements, turning codebases into readability nightmares and maintenance headaches. While Java 21's text blocks dramatically improve the ergonomics of multi-line strings, eliminating the need for explicit newline characters and escape sequences, securely injecting dynamic values remains a challenge.

This is where integrating intelligent coding assistants like Claude Code can provide significant value. When faced with complex SQL queries requiring dynamic filters or variable table names, instead of manually constructing strings with error-prone `.append()` or `String.format()` calls, you can leverage Claude Code to suggest formatting *within* your text blocks. Claude Code's contextual understanding of your Java code can guide you in embedding variables safely and correctly, particularly crucial in SQL where proper quoting and escaping are paramount to prevent syntax errors and, more importantly, security vulnerabilities.

Consider a common scenario: retrieving user data with an optional email filter. A naive approach might involve messy string building. Here's how text blocks and a *hypothetical* Claude Code-assisted `String.format` could be integrated for better clarity during development:

```java
import java.util.Optional;

public class UserRepository {

    public String buildFindUserSql(Optional<String> emailFilter) {
        String baseSql = """
            SELECT u.id, u.name, u.email
            FROM users u
            WHERE 1 = 1
            """;

        StringBuilder sqlBuilder = new StringBuilder(baseSql);

        emailFilter.ifPresent(email -> {
            // Claude Code might suggest this pattern for embedding the dynamic value safely within the string context
            // Note: For production, parameterized queries are essential!
            sqlBuilder.append(" AND u.email = '%s'".formatted(email));
        });

        return sqlBuilder.toString();
    }

    public static void main(String[] args) {
        UserRepository repo = new UserRepository();

        // Case 1: No email filter
        System.out.println("SQL without filter: " + repo.buildFindUserSql(Optional.empty()));

        // Case 2: With email filter
        System.out.println("SQL with filter: " + repo.buildFindUserSql(Optional.of("test@example.com")));
    }
}
```

The primary gotcha, and a critical one, is SQL injection. While text blocks and dynamic string formatting enhance code readability and developer experience, they offer *no inherent protection* against SQL injection vulnerabilities. In production environments, it is **imperative** to always use parameterized queries via `PreparedStatement` with JDBC or Spring Data JPA's `@Query` annotation with named parameters. Claude Code can assist in generating the string *representation* of your query, but ensuring the *secure execution* remains your responsibility. The example above is purely for demonstrating string construction ergonomics, not for direct use with sensitive data.

For a practical exploration, try this in your IDE with an AI coding assistant enabled for Java: Begin writing a multi-line text block containing a placeholder for a value. Then, initiate the AI's code completion feature. Observe how it suggests incorporating `String.format()` or `.formatted()` to efficiently and cleanly embed that dynamic value within your readable text block, mirroring the pattern shown.
