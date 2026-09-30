---
layout: post
title: "Method-Level Security with Custom SpEL using Claude Code"
date: 2026-09-30
type: how-to
summary: "Implement fine-grained method-level security in Spring Boot using custom SpEL expressions and Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - claude-code
  - devtools
---



![Method-Level Security with Custom SpEL using Claude Code](assets/images/placeholder.jpg)



Many Java developers grapple with unwieldy authorization logic, often buried within service methods or scattered across repetitive `@PreAuthorize` annotations. This leads to code duplication and a maintenance nightmare as security policies become increasingly complex. While Spring Security's SpEL integration offers powerful dynamic access control, constructing intricate, reusable permission checks directly in annotations can become verbose and hard to manage.

This article demonstrates how to streamline method-level security by implementing a custom `PermissionEvaluator` that leverages SpEL. This approach allows you to encapsulate complex authorization rules, making them reusable and easily referenced from `@PreAuthorize` or `@PostAuthorize` annotations. Consider the common scenario of verifying a user's ability to edit a resource, a permission that might depend on their role *and* specific attributes of the resource itself. A custom `PermissionEvaluator` elegantly handles such nuanced checks, promoting cleaner code and more maintainable security configurations.

To begin, ensure you have the necessary Spring Security dependencies. For Spring Boot projects, `spring-boot-starter-security` typically suffices.

```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-core</artifactId>
</dependency>
```

Next, implement your custom `PermissionEvaluator`. This interface requires you to define logic for `hasPermission` checks, either with the target domain object or its identifier.

```java
package com.example.security;

import com.example.domain.Project; // Assuming Project is in com.example.domain
import org.springframework.security.access.PermissionEvaluator;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;

import java.io.Serializable;
import java.util.Optional;

@Component
public class CustomPermissionEvaluator implements PermissionEvaluator {

    @Override
    public boolean hasPermission(Authentication authentication, Object targetDomainObject, Object permission) {
        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        String requiredPermission = (String) permission;

        if (targetDomainObject instanceof Project) {
            Project project = (Project) targetDomainObject;
            return checkProjectPermission(authentication, project, requiredPermission);
        }
        // Add checks for other domain objects as needed

        return false; // Default to deny if object type is not handled
    }

    @Override
    public boolean hasPermission(Authentication authentication, Serializable targetId, String targetType, Object permission) {
        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        String requiredPermission = (String) permission;
        // In a real application, you'd fetch the domain object using targetId and targetType
        // For this example, we'll assume a simple permission check based on type and ID
        return checkPermissionById(authentication, targetType, targetId, requiredPermission);
    }

    private boolean checkProjectPermission(Authentication authentication, Project project, String requiredPermission) {
        // More granular permission logic based on user roles and project attributes
        Optional<GrantedAuthority> adminAuthority = authentication.getAuthorities().stream()
                .filter(ga -> ga.getAuthority().equals("ROLE_ADMIN"))
                .findFirst();
        Optional<GrantedAuthority> editorAuthority = authentication.getAuthorities().stream()
                .filter(ga -> ga.getAuthority().equals("ROLE_EDITOR"))
                .findFirst();
        Optional<GrantedAuthority> viewerAuthority = authentication.getAuthorities().stream()
                .filter(ga -> ga.getAuthority().equals("ROLE_VIEWER"))
                .findFirst();

        switch (requiredPermission.toUpperCase()) {
            case "READ":
                return viewerAuthority.isPresent() || editorAuthority.isPresent() || adminAuthority.isPresent();
            case "EDIT":
                return editorAuthority.isPresent() || adminAuthority.isPresent();
            case "DELETE":
                // Example: Only admins can delete
                return adminAuthority.isPresent();
            default:
                return false;
        }
    }

    private boolean checkPermissionById(Authentication authentication, String targetType, Serializable targetId, String requiredPermission) {
        // This method is typically used when the domain object isn't readily available.
        // In a real scenario, you'd fetch the object using repository/service calls.
        // For this example, we'll allow "EDIT" for any ID if user is editor or admin.
        boolean isAdmin = authentication.getAuthorities().stream().anyMatch(ga -> ga.getAuthority().equals("ROLE_ADMIN"));
        boolean isEditor = authentication.getAuthorities().stream().anyMatch(ga -> ga.getAuthority().equals("ROLE_EDITOR"));

        if ("Project".equals(targetType)) {
            if ("EDIT".equals(requiredPermission)) {
                return isEditor || isAdmin;
            } else if ("READ".equals(requiredPermission)) {
                return true; // Assuming anyone can read if they can identify it
            }
        }
        return false;
    }

    // Dummy Project class for compilation (ensure this matches your actual domain object)
    public static class Project {
        private Long id;
        private String name;

        public Project(Long id, String name) {
            this.id = id;
            this.name = name;
        }

        public Long getId() { return id; }
        public String getName() { return name; }
        // Add other getters/setters as needed
    }
}
```

To integrate this custom evaluator, configure Spring Security's method security. The `GlobalMethodSecurityConfiguration` allows you to customize the `MethodSecurityExpressionHandler` and inject your `CustomPermissionEvaluator`.

```java
package com.example.config;

import com.example.security.CustomPermissionEvaluator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.expression.method.DefaultMethodSecurityExpressionHandler;
import org.springframework.security.access.expression.method.MethodSecurityExpressionHandler;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.method.configuration.GlobalMethodSecurityConfiguration;

@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class MethodSecurityConfig extends GlobalMethodSecurityConfiguration {

    @Bean
    public CustomPermissionEvaluator customPermissionEvaluator() {
        return new CustomPermissionEvaluator();
    }

    @Override
    protected MethodSecurityExpressionHandler createExpressionHandler() {
        DefaultMethodSecurityExpressionHandler expressionHandler = new DefaultMethodSecurityExpressionHandler();
        expressionHandler.setPermissionEvaluator(customPermissionEvaluator()); // Register your custom evaluator
        return expressionHandler;
    }
}
```

With the configuration in place, you can now utilize the `hasPermission` SpEL function within your service methods. For instance, to restrict access based on a project's ID and a required permission:

```java
package com.example.service;

import com.example.domain.Project;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

@Service
public class ProjectService {

    // Example 1: Using hasPermission with target ID and type
    @PreAuthorize("hasPermission(#projectId, 'Project', 'READ')")
    public Project getProjectById(Long projectId) {
        // Dummy implementation: In a real app, fetch project from DB
        System.out.println("Fetching project with ID: " + projectId);
        return new Project(projectId, "Sample Project");
    }

    // Example 2: Using hasPermission with target domain object
    @PreAuthorize("hasPermission(#project, 'EDIT')")
    public void updateProject(Project project) {
        // Dummy implementation: In a real app, update project in DB
        System.out.println("Updating project: " + project.getName());
    }

    // Example 3: Adding a delete permission check
    @PreAuthorize("hasPermission(#projectId, 'Project', 'DELETE')")
    public void deleteProject(Long projectId) {
        System.out.println("Deleting project with ID: " + projectId);
    }
}
```

A common pitfall arises when `targetDomainObject` is ambiguous for SpEL. When passing primitive types or simple wrappers (like `Long`), SpEL might not automatically resolve them to a domain object. In such cases, explicitly use the `hasPermission(String targetType, Serializable targetId, Object permission)` overload, as demonstrated in `getProjectById`, or leverage `#root.target` if appropriate. This explicit approach clarifies intent and ensures correct permission evaluation.
