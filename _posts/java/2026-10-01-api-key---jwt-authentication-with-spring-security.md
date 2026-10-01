---
layout: post
title: "API Key & JWT Authentication with Spring Security Filters"
date: 2026-10-01
type: how-to
summary: "Implement dual API Key and JWT authentication seamlessly in your Spring Boot application using custom filters."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - devtools
  - productivity
---



![API Key & JWT Authentication with Spring Security Filters](assets/images/placeholder.jpg)



As a Java developer crafting APIs, you're frequently tasked with implementing robust authentication. While simple API keys suffice for internal services or basic integrations, more sensitive operations and user-facing endpoints demand the stronger security of JWTs. The challenge arises when you need to support both concurrently within a Spring Boot application without creating a configuration nightmare. This guide demonstrates how to elegantly manage both API key and JWT authentication using Spring Security's filter chain.

The strategy hinges on creating two distinct `OncePerRequestFilter` implementations. The first, `ApiKeyAuthenticationFilter`, will be responsible for extracting and validating an API key from a custom header (e.g., `X-API-KEY`). The second, `JwtAuthenticationFilter`, will handle JWT validation, typically from the `Authorization: Bearer <token>` header. These custom filters are then strategically inserted into the `SecurityFilterChain`. Spring Security's filter chain is inherently ordered, allowing us to place our filters at specific points. For example, an API key check might precede a JWT check if you intend to offer API key authentication for specific endpoints with a lower security requirement, or if you want to provide a fallback mechanism.

Here's how this integrates into your `SecurityConfig`:

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

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
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN") // Example of role-based access
                .anyRequest().authenticated()
            )
            // Insert custom filters before standard ones like UsernamePasswordAuthenticationFilter
            // The order here is crucial: API key might be checked first if it's a simpler or fallback mechanism
            .addFilterBefore(apiKeyAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

A critical consideration is the order of your filters. If both `ApiKeyAuthenticationFilter` and `JwtAuthenticationFilter` can authenticate a given request (e.g., a request legitimately carrying both an API key and a valid JWT), the filter that successfully authenticates *first* and populates the `SecurityContextHolder` will likely prevent the subsequent filter from executing its authentication logic. This is because Spring Security typically short-circuits the filter chain once authentication is established. Therefore, meticulously define the precedence or ensure your filters are designed to coexist gracefully, perhaps by having the API key filter handle specific endpoints and the JWT filter handle others, or by allowing both to execute their checks if the security requirements differ. Always remember to configure access rules like `.permitAll()` for truly public endpoints to avoid unexpected authentication failures.

This approach works because Spring Security processes filters sequentially within the `SecurityFilterChain`. By adding your custom filters using `addFilterBefore()` or `addFilterAfter()`, you're precisely controlling their position in the chain. When a request arrives, it traverses the filters in order. If `apiKeyAuthenticationFilter` successfully validates a key and sets the authentication principal in `SecurityContextHolder`, subsequent filters in the chain (including `jwtAuthenticationFilter` if it were placed later) might not execute their core authentication logic if the request is already considered authenticated. This allows you to prioritize authentication schemes or apply different security policies to different request types. The key takeaway is the explicit control over the filter execution order, enabling sophisticated authentication strategies beyond a single mechanism.
