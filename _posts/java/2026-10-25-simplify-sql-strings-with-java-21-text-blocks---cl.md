---
layout: post
title: "Simplify SQL Strings with Java 21 Text Blocks & Claude Code"
date: 2026-10-25
type: how-to
summary: "Learn to write cleaner, more readable SQL queries in Java 21 using text blocks and Claude Code for better formatting."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - claude-code
  - productivity
  - devtools
---



![Simplify SQL Strings with Java 21 Text Blocks & Claude Code](assets/images/placeholder.jpg)



Writing SQL queries within Java applications often results in unwieldy, multi-line strings that are a nightmare to read and maintain. Traditional string concatenation or simple multi-line strings in older Java versions struggle to preserve SQL's indentation and structure, increasing the risk of syntax errors and making debugging a chore. Java 21's text blocks are a welcome addition, allowing strings to span multiple lines with preserved whitespace. However, they don't inherently solve the problem of *formatting* the SQL itself to be developer-friendly. This is where leveraging AI tools like Claude Code can significantly enhance developer productivity.

Claude Code, the command-line interface for Claude, offers a powerful way to transform raw SQL snippets into beautifully formatted, readable text blocks directly within your Java code. Imagine dealing with a complex `SELECT` statement or an `INSERT` query with numerous columns and conditions. Instead of manually aligning every clause or wrestling with escape characters, you can feed the raw SQL to Claude Code and instruct it to format it according to standard SQL conventions, producing output perfectly suited for embedding as a Java 21 text block. This approach not only dramatically improves code readability but also reduces the cognitive load when reviewing or modifying database queries, minimizing the chance of introducing errors.

Consider a common scenario with a less-than-ideal SQL string:

```java
String sqlQuery = "SELECT u.id, u.name, a.city FROM users u JOIN addresses a ON u.id = a.user_id WHERE u.status = 'active' ORDER BY u.name;";
```

To transform this into a more maintainable format using Claude Code, first ensure you have the `claude` CLI installed and configured. Then, you can use a prompt like this to generate a well-structured SQL block:

```bash
echo "SELECT u.id, u.name, a.city FROM users u JOIN addresses a ON u.id = a.user_id WHERE u.status = 'active' ORDER BY u.name;" | claude --prompt "Format the following SQL query for use in a Java 21 text block, preserving indentation and readability. Use standard SQL formatting conventions." --language java
```

This command will output a nicely formatted SQL string. You can then seamlessly wrap this output in a Java 21 text block for immediate use in your code:

```java
String formattedSqlQuery = """
    SELECT
        u.id,
        u.name,
        a.city
    FROM
        users u
    JOIN
        addresses a ON u.id = a.user_id
    WHERE
        u.status = 'active'
    ORDER BY
        u.name;
""";
```

A crucial "gotcha" to be mindful of is that Claude Code's formatting prowess stems from its training data and general understanding of common SQL styles. For highly specific, proprietary SQL dialects, or when adhering to very strict internal formatting guidelines, you might need to refine your prompts with more explicit instructions or perform minor manual adjustments to the generated output. Furthermore, always ensure the context you provide in your prompt is clear and specific to guide Claude towards the exact desired output format suitable for Java text blocks.
