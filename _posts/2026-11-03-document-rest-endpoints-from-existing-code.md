---
layout: post
title: "Document REST Endpoints from Existing Code"
date: 2026-11-03
type: how-to
summary: "Automatically generate an OpenAPI specification for undocumented REST controllers using Claude Code."
image: "/claude-daily-tips/assets/images/2026-11-03-document-rest-endpoints-from-existing-code.jpg"
tags:
  - claude-code
  - cli
  - dotnet
  - productivity
  - automation
---



![Document REST Endpoints from Existing Code](/claude-daily-tips/assets/images/2026-11-03-document-rest-endpoints-from-existing-code.jpg)



Many developers face the challenge of integrating with or understanding existing REST APIs that lack formal documentation. Whether inheriting a legacy codebase or working under tight deadlines, undocumented controllers become significant hurdles for efficient integration, automated testing, and onboarding new team members. Manually crafting OpenAPI (Swagger) specifications for these endpoints is a tedious, error-prone endeavor, often resulting in outdated or incomplete documentation that fails to reflect the API's actual behavior.

Claude Code offers a powerful solution to this problem by analyzing your controller code and intelligently inferring the necessary OpenAPI details. It leverages its understanding of common ASP.NET Core REST controller patterns, including attributes like `[ApiController]`, `[Route]`, `[HttpGet]`, `[HttpPost]`, and how request/response models and parameter attributes are used. This allows Claude to generate a solid foundational OpenAPI specification, acting as a significant head start for further manual refinement and enrichment.

The core mechanism involves instructing Claude to analyze your controller code and generate an OpenAPI specification. You can direct it to output in a specific format and to a designated file. It's crucial to understand that Claude's efficacy relies on inference and adherence to standard patterns. Highly custom routing, authorization attributes without explicit inline documentation, or deeply dynamic API behaviors might necessitate manual adjustments to the generated specification. For best results, focus on controllers that follow conventional ASP.NET Core conventions.

Consider this practical command to initiate the process:

```bash
claude --target ./Controllers/ProductsController.cs --language dotnet --task generate-openapi --output ./openapi/products.yaml
```

**Actionable Step:** Identify an undocumented REST controller within your .NET project. Execute the `claude` command above, modifying the `--target` and `--output` paths to match your project structure. After the command completes, carefully review the generated `products.yaml` file. You might be surprised to find that while common patterns are well-captured, custom middleware or complex dependency injection scenarios influencing routing might require manual annotation in the generated spec. This generated output is a starting point, not a final decree.
