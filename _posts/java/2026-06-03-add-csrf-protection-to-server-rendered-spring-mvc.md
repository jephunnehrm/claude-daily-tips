---
layout: post
title: "Add CSRF Protection to Server-Rendered Spring MVC"
date: 2026-06-03
type: how-to
summary: "Configure robust CSRF protection for your server-rendered Spring MVC application using Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
---



![Add CSRF Protection to Server-Rendered Spring MVC](assets/images/placeholder.jpg)



As a Java developer building server-rendered Spring MVC applications, you know that security is paramount. Manually configuring Cross-Site Request Forgery (CSRF) protection can be tedious, involving understanding `CsrfTokenRepository`, `CsrfFilter`, and Thymeleaf integration. This process often leads to boilerplate code and potential misconfigurations, leaving your application vulnerable. Claude Code can significantly simplify this task by generating the necessary configuration classes and template snippets.

To leverage Claude Code for CSRF protection, you'll use its command-line interface to describe your requirements. You want to ensure that all state-changing HTTP requests (POST, PUT, DELETE) are protected. Claude Code can then provide a `SecurityConfig` class that extends `WebSecurityConfigurerAdapter` (or the newer `SecurityFilterChain` bean configuration), sets up the `CsrfTokenRepository`, and integrates with your templating engine. For Thymeleaf, it will generate the necessary Thymeleaf dialect and inclusion within your base layout.

Here's a typical CLI command sequence you might use. This prompts Claude Code to create a Spring Security configuration with CSRF enabled and basic Thymeleaf integration for server-rendered applications.

```bash
claude request \
  --tool "Spring Security CSRF Configuration" \
  --prompt "Generate a Spring Security configuration for a Spring MVC application using Thymeleaf. It should enable CSRF protection, use a HttpSessionCsrfTokenRepository, and include instructions on how to add the CSRF token to Thymeleaf forms. Assume a standard Spring Boot setup." \
  --output-file src/main/java/com/example/security/SecurityConfig.java
```

A key limitation to be aware of is that while Claude Code can generate the core configuration, you might still need to manually adjust the Thymeleaf template snippets it provides. Specifically, ensure that the `th:action` and hidden input field for the CSRF token are correctly placed within *all* your forms that perform state-changing operations. Furthermore, Claude Code might not automatically cover edge cases like custom `CsrfTokenRepository` implementations or complex filter chains, requiring manual review and adaptation.

**Try it:** Run the `claude` command above in your project's root directory and review the generated `SecurityConfig.java` file for correctness.
