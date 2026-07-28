---
layout: post
title: "Dual Auth for Spring Boot APIs: API Key & JWT"
date: 2026-07-28
type: how-to
summary: "Secure your Spring Boot APIs with both API keys and JWTs using Claude Code for efficient filter chain setup."
image: "/claude-daily-tips/assets/images/java-2026-07-28-dual-auth-for-spring-boot-apis--api-key---jwt.jpg"
tags:
  - java
  - spring
  - claude-code
---



![Dual Auth for Spring Boot APIs: API Key & JWT](/claude-daily-tips/assets/images/java-2026-07-28-dual-auth-for-spring-boot-apis--api-key---jwt.jpg)



As a Java developer building modern APIs, you often face the challenge of implementing robust and flexible authentication. A common scenario is supporting both API keys for simpler integrations and JWTs for more complex, user-centric authentication flows. Manually crafting the Spring Security filter chain for this dual requirement can be tedious and error-prone, especially when dealing with filter precedence.

To address this, you'll need to define custom `OncePerRequestFilter` implementations for each authentication mechanism. For API keys, this involves extracting a key from a header (e.g., `X-API-Key`) and validating it against a trusted source, such as an in-memory map or a database. For JWTs, you'll extract the token from the `Authorization` header, validate its signature and expiry using a `JwtDecoder`, and then populate the `Authentication` object with the user's details. Spring Security's `FilterChainProxy` is then configured to chain these filters appropriately.

The core of this solution lies in configuring Spring Security's `FilterChainProxy` within a `SecurityFilterChain` bean. You define multiple security filter chains, each with a specific order and responsibility. Crucially, the filter chain responsible for API key authentication should typically come *before* the JWT authentication filter. This is because API keys might be used for simpler, less sensitive operations or as an initial gatekeeper before a more detailed JWT-based authentication is attempted.

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

// Assume ApiKeyAuthenticationFilter and JwtAuthenticationFilter are properly implemented
// and autowired beans.
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final ApiKeyAuthenticationFilter apiKeyAuthenticationFilter;
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(ApiKeyAuthenticationFilter apiKeyAuthenticationFilter, JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.apiKeyAuthenticationFilter = apiKeyAuthenticationFilter;
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable() // Disable CSRF for stateless APIs
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/secure/apikey/**").hasRole("API_KEY_USER")
                .requestMatchers("/api/secure/jwt/**").hasRole("JWT_USER")
                .anyRequest().authenticated()
            )
            // Add custom filters, ensuring API Key filter comes first
            .addFilterBefore(apiKeyAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

A key consideration, and potential "gotcha," is managing the order of your custom filters correctly. If your JWT filter is placed *before* the API key filter, and an incoming request contains *both* valid credentials, the JWT might be processed first. This could lead to the API key being bypassed entirely, potentially granting unintended access or masking an API key authentication attempt. Always ensure that the filter for the simpler or more general authentication mechanism (like API keys) is evaluated *before* the filter for the more complex one (like JWTs), unless your specific security requirements dictate otherwise.
