---
layout: post
title: "Bicep for Azure App Service & SQL from Claude Code"
date: 2026-08-01
type: how-to
summary: "Use Claude Code to quickly create Bicep files for common Azure resources like App Service and SQL Database."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-01-bicep-for-azure-app-service---sql-from-claude-code.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - azure
---



![Bicep for Azure App Service & SQL from Claude Code](/claude-daily-tips/assets/images/dotnet-2026-08-01-bicep-for-azure-app-service---sql-from-claude-code.jpg)



As a .NET developer, the repetitive nature of provisioning foundational Azure infrastructure for applications – be it an App Service, a SQL Database, and a Key Vault – often leads to copy-pasting and meticulous configuration. This manual grind for resource definitions, parameters, and access policies eats into valuable development time that could be spent on core application logic. Leveraging AI assistants like Claude Code can dramatically accelerate this initial setup, freeing you from boilerplate infrastructure code and allowing for a faster path to deployment.

Claude Code, accessible through the `claude` CLI, can be a powerful ally in generating these Bicep resources. By providing specific prompts, you can instruct it to create a Bicep module for an Azure App Service and its associated plan, an Azure SQL Database server and database with essential firewall rules, and an Azure Key Vault. The generated code typically includes the necessary resource definitions, parameters for customization, and outputs for integration into your deployment pipelines, offering a solid starting point for your infrastructure.

Here’s an illustrative example of how you might prompt Claude Code to kickstart this resource creation. The key to obtaining useful output lies in the specificity of your prompt. You'll want to clearly define resource names, target regions, desired SKUs, and any critical dependencies.

```bash
claude prompt "Generate Bicep code for an Azure App Service, an Azure SQL Database server and database, and an Azure Key Vault. Include a standard App Service Plan, a Basic SQL tier, and a standard Key Vault. Ensure the SQL Database has a firewall rule allowing access from the App Service's outbound IP. Include parameters for resource names and locations." --output bicep-azure-resources.bicep
```

While Claude Code excels at generating initial Bicep scaffolding, a critical gotcha is its inherent limitation in handling sophisticated security configurations and intricate dependency resolution. For instance, while it might create a placeholder firewall rule for the SQL Database, it won't automatically infer or dynamically fetch the App Service's precise outbound IP address. This becomes especially relevant if your App Service utilizes VNet integration or private endpoints, where dynamic IP management is crucial. Always perform a thorough review and rigorous testing of any AI-generated Bicep code, paying meticulous attention to security settings, resource naming, and ensuring all dependencies are correctly managed before production deployment. This approach empowers you to rapidly iterate on infrastructure while maintaining robust control over your deployment's security and integrity.
