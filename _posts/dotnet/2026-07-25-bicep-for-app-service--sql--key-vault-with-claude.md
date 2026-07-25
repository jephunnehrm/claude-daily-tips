---
layout: post
title: "Bicep for App Service, SQL, Key Vault with Claude Code"
date: 2026-07-25
type: how-to
summary: "Quickly get Bicep infrastructure code for common Azure resources using Claude Code, saving manual authoring time."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-25-bicep-for-app-service--sql--key-vault-with-claude.jpg"
tags:
  - dotnet
  - claude-code
  - azure
  - devtools
  - automation
---



![Bicep for App Service, SQL, Key Vault with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-07-25-bicep-for-app-service--sql--key-vault-with-claude.jpg)



As a .NET developer, setting up the foundational Azure resources for a new application – like an App Service for hosting, an Azure SQL Database for persistence, and a Key Vault for secrets – can be a repetitive and error-prone manual process. While you can write Bicep files from scratch, it often involves looking up syntax, resource types, and required properties, slowing down your initial development velocity. Claude Code can significantly accelerate this by generating Bicep code based on your requirements.

Let's say you need a basic Bicep template to provision these three core Azure services. You can prompt Claude Code with a clear request, specifying the resources and their basic configurations. For instance, you might ask Claude Code to "write Bicep code to create an Azure App Service plan and web app, a SQL server and database, and a Key Vault." The tool will then translate this natural language into the structured Bicep syntax.

Here's a command you might use to invoke Claude Code for this task:

```bash
claude --tool bicep --prompt "Create Bicep code for an Azure App Service, Azure SQL Database, and Azure Key Vault, with sensible defaults."
```

This command tells Claude Code to use its Bicep tool and provides a natural language prompt describing the desired infrastructure. Claude Code will then output the generated Bicep code directly, which you can then review, customize, and deploy using Azure CLI or other deployment methods. A crucial "gotcha" to be aware of is that while Claude Code provides a strong starting point, it may not always infer the exact networking, security, or scaling configurations you require for production. Always thoroughly review the generated code for compliance with your organization's security and operational standards.

**Try it:** Run the `claude` command above in your terminal and paste the resulting Bicep code into a `.bicep` file in your Azure development environment.

You can then integrate this Bicep code into your CI/CD pipeline using Azure Pipelines, GitHub Actions, or Azure DevOps, ensuring your infrastructure is consistently provisioned as your application evolves. Remember to adapt the parameters and resource names to match your specific project requirements, such as SKUs for the SQL database, pricing tiers for the App Service, and access policies for the Key Vault.
