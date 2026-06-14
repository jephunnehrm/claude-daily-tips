---
layout: post
title: "Configure YARP Reverse Proxy with Claude Code"
date: 2026-06-14
type: how-to
summary: "Quickly define complex YARP configurations for API gateways using Claude Code, saving manual setup time."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Configure YARP Reverse Proxy with Claude Code](assets/images/placeholder.jpg)



When developing .NET microservices, orchestrating traffic across numerous backend APIs can quickly become a complex undertaking. Manually configuring a reverse proxy like YARP, especially with multiple services and intricate routing rules, is a common source of developer friction and potential errors. This is precisely where leveraging AI code assistants, such as Claude Code, can dramatically streamline the process. By translating natural language descriptions of your gateway's desired behavior into YARP's structured JSON configuration, Claude Code offers a more intuitive and efficient approach to defining routes, clusters, and endpoints.

Instead of meticulously hand-crafting JSON, you can articulate your requirements conversationally. For instance, you might describe a scenario where all incoming requests prefixed with `/api/customers` should be directed to a dedicated `CustomerService` cluster, and requests matching `/api/orders/*` should target the `OrderService` cluster. Claude Code can then interpret these instructions and generate the corresponding `yarp.json` configuration, including essential elements like load balancing policies. This allows you to focus on the architectural intent rather than the syntactical minutiae of the configuration file.

Consider the following example illustrating how you might use the `claude` CLI to generate a foundational YARP configuration for an API gateway with two distinct backend services:

```bash
claude --input "Generate YARP JSON configuration for ASP.NET Core. Define two clusters: 'customers' mapped to http://localhost:5011 and 'orders' mapped to http://localhost:5012. Create a route named 'CustomerRoute' that matches '/api/customers/{**catchall}' and forwards to the 'customers' cluster. Create another route named 'OrderRoute' that matches '/api/orders/{**catchall}' and forwards to the 'orders' cluster. Implement round-robin load balancing for both clusters." --output-file yarp.json
```

This command empowers Claude Code to produce a `yarp.json` file populated with the necessary `Routes` and `Clusters` to establish your API gateway. While Claude Code excels at generating standard configurations, a critical limitation to note is its current inability to handle highly nuanced or custom authentication middleware configurations. For advanced scenarios like fine-grained access control policies or custom session affinity implementations, manual adjustments to the generated JSON will still be required to achieve the precise behavior you need. Always thoroughly review the AI-generated output against your specific security and operational requirements.

To experience this firsthand, execute the `claude` command provided. Afterward, inspect the generated `yarp.json` file. Reflect on how you might expand this configuration with additional routes for new services or explore YARP's built-in capabilities for more sophisticated load balancing strategies, recognizing where manual intervention might become necessary for advanced features.
