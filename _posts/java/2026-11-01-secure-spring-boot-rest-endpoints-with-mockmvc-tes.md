---
layout: post
title: "Secure Spring Boot REST Endpoints with MockMvc Tests"
date: 2026-11-01
type: how-to
summary: "Proactively test security for all Spring Boot REST endpoints by generating MockMvc security test suites with Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - java
  - spring
  - junit
  - claude-code
  - productivity
---



![Secure Spring Boot REST Endpoints with MockMvc Tests](assets/images/placeholder.jpg)



Manually crafting robust security tests for every REST endpoint in a Spring Boot application can be a time-consuming and error-prone endeavor. Developers often find themselves painstakingly writing `MockMvc` tests for each endpoint, meticulously verifying HTTP methods, ensuring correct status codes for unauthenticated users, users with insufficient privileges, and properly authorized users, and handling various exception scenarios. This manual process is not only tedious but also increases the likelihood of overlooking critical security vulnerabilities, leaving your API exposed.

Leveraging AI-powered code generation, like that offered by Claude Code, can significantly accelerate this security testing process. By analyzing your Spring Boot controller code, Claude Code can automatically generate a foundational `MockMvc` test suite. This suite can proactively cover essential security scenarios, such as attempts to access endpoints without any authentication, requests made with inadequate permissions, and successful access for appropriately authenticated users. This dramatically reduces the initial manual effort, allowing developers to focus on more complex testing logic and ensuring a more comprehensive security posture from the outset.

Here’s an example of how Claude Code can assist in generating security tests for a hypothetical `UserController`. After providing your controller code to Claude, you might prompt it to generate security tests. The generated output could resemble the following:

```java
package com.example.demo.controller;

import com.example.demo.config.SecurityConfig; // Ensure this import points to your actual security config
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

@SpringBootTest
@AutoConfigureMockMvc
@Import(SecurityConfig.class) // Crucial: import your application's security configuration
public class UserControllerSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void getAllUsers_whenNotAuthenticated_shouldReturnUnauthorized() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/api/users"))
               .andExpect(MockMvcResultMatchers.status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "VIEWER") // Example: VIEWER role is insufficient for POST operations
    void createUser_whenAuthenticatedAsViewer_shouldReturnForbidden() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.post("/api/users")
                        .contentType("application/json")
                        .content("{\"username\":\"newuser\",\"password\":\"password\"}")) // Example payload
               .andExpect(MockMvcResultMatchers.status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "MANAGER") // Example: MANAGER role has POST permissions
    void createUser_whenAuthenticatedAsManager_shouldReturnCreated() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.post("/api/users")
                        .contentType("application/json")
                        .content("{\"username\":\"newuser\",\"password\":\"password\"}"))
               .andExpect(MockMvcResultMatchers.status().isCreated()); // Expecting 201 Created
    }

    @Test
    @WithMockUser(username = "testuser", roles = "USER")
    void getUserProfile_whenAccessingOwnProfile_shouldReturnOk() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/api/users/profile/testuser"))
               .andExpect(MockMvcResultMatchers.status().isOk());
    }

    // Additional tests for other endpoints and role combinations are essential.
}
```

A critical limitation of AI-generated tests is their inability to grasp nuanced business logic or intricate authorization rules. While Claude Code excels at producing boilerplate security tests, it cannot intuit your custom authorization predicates (e.g., "a user can only update their *own* profile"). Therefore, developers *must* meticulously review the generated tests. This includes adding specific assertions for successful scenarios (like verifying response bodies), ensuring `@WithMockUser` annotations accurately mirror your application's role hierarchy, and implementing tests for custom authorization logic that go beyond simple role checks. This approach acts as a powerful accelerator, not a complete replacement for careful, domain-aware testing.

**Practical Application:** To experience this acceleration, paste your Spring Boot controller class into Claude Code and use a prompt such as: "Generate `MockMvc` security tests for this controller, focusing on unauthorized access, role-based access control, and common security pitfalls." This proactive security testing methodology, augmented by intelligent code generation, offers a significant time-saving advantage and helps mitigate costly security oversights in your Java applications. By integrating tools like Claude Code into your development workflow, you can cultivate a more resilient and secure API surface.
