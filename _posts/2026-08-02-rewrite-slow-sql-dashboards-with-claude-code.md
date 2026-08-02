---
layout: post
title: "Rewrite Slow SQL Dashboards with Claude Code"
date: 2026-08-02
type: how-to
summary: "Enhance dashboard performance by refactoring slow SQL queries using Claude Code and window functions."
image: "/claude-daily-tips/assets/images/2026-08-02-rewrite-slow-sql-dashboards-with-claude-code.jpg"
tags:
  - claude-code
  - cli
  - productivity
  - devtools
---



![Rewrite Slow SQL Dashboards with Claude Code](/claude-daily-tips/assets/images/2026-08-02-rewrite-slow-sql-dashboards-with-claude-code.jpg)



Tired of dashboards that lag due to painstakingly slow SQL queries? Manually untangling complex joins and subqueries to find performance bottlenecks, especially when modern analytical functions offer a more elegant solution, is a draining task. This is precisely where Claude Code can be a game-changer, dramatically accelerating your optimization workflow. Instead of hours spent meticulously rewriting SQL, you can leverage Claude Code to suggest and implement significantly more efficient queries, often by introducing powerful window functions like `ROW_NUMBER()`, `LAG()`, or the ubiquitous `SUM() OVER()`.

Consider a common scenario: calculating cumulative sales per month. A typical naive approach might involve inefficient subqueries or correlated joins that repeatedly scan your sales table. Presenting such a problematic query to Claude Code and explicitly asking it to refactor using window functions can yield remarkable results. For instance, if you're dealing with a query like this:

```sql
SELECT
    sale_date,
    SUM(sale_amount) AS daily_sales,
    (SELECT SUM(sub_sale_amount)
     FROM sales s2
     WHERE s2.sale_date <= s1.sale_date) AS cumulative_sales
FROM sales s1
GROUP BY sale_date
ORDER BY sale_date;
```

You can prompt Claude Code to transform it using `SUM() OVER (ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`. Claude Code can then generate a far cleaner and typically more performant version, eliminating the overhead of costly self-joins or subqueries that re-scan the entire table for each row. This approach works because window functions compute aggregate values across a set of table rows that are somehow related to the current row, without collapsing those rows into a single output row like traditional aggregate functions, allowing for calculations like running totals in a single pass.

A crucial caveat to keep in mind is that while Claude Code excels at generating modern SQL constructs, it doesn't possess an inherent understanding of your specific database's performance characteristics, underlying hardware, or bespoke indexing strategies. The output query may be syntactically perfect and brilliantly leverage window functions, but it might still require fine-tuning or targeted indexing on your end to achieve peak performance. Always rigorously test any query modifications on a staging environment before deploying to production.

**Your Turn:** Paste your most problematic, slow-loading dashboard SQL query into a Claude Code session and instruct it: "Rewrite this SQL query using window functions to improve performance, specifically focusing on calculating cumulative values or any other appropriate analytical calculation."
