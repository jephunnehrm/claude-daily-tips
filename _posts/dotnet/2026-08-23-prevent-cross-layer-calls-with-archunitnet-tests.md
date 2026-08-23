---
layout: post
title: "Prevent Cross-Layer Calls with ArchUnitNET Tests"
date: 2026-08-23
type: how-to
summary: "Automatically enforce Clean Architecture layer boundaries in your .NET projects using Claude Code and ArchUnitNET."
image: "/claude-daily-tips/assets/images/dotnet-2026-08-23-prevent-cross-layer-calls-with-archunitnet-tests.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
  - devtools
---



![Prevent Cross-Layer Calls with ArchUnitNET Tests](/claude-daily-tips/assets/images/dotnet-2026-08-23-prevent-cross-layer-calls-with-archunitnet-tests.jpg)



As .NET applications scale, maintaining clear architectural boundaries—like Presentation, Application, Domain, and Infrastructure—becomes a significant challenge. Developers often struggle to prevent accidental cross-layer dependencies, such as API controllers (Presentation) reaching directly into repository implementations (Infrastructure). This can lead to tightly coupled code, making refactoring, testing, and understanding the system's structure increasingly difficult. Automated architectural testing, particularly with ArchUnitNET, provides a robust solution to enforce these boundaries proactively.

ArchUnitNET, a .NET port of the well-regarded Java library, empowers developers to define and enforce architectural rules directly within their C# codebase. By writing tests that specifically assert expected dependencies (or lack thereof) between different parts of your application, you can catch violations at build time, long before they manifest as runtime issues or become deeply entrenched. The utility of this approach is amplified when leveraging AI coding assistants like Claude Code, which can significantly accelerate the creation of these tests by generating boilerplate code and suggesting appropriate architectural rules, effectively translating your design intent into verifiable C# assertions.

Consider enforcing a core Clean Architecture principle: the Application layer should exclusively depend on the Domain layer, eschewing direct contact with the Infrastructure layer. The following ArchUnitNET test, readily drafted with AI assistance, exemplifies this:

```csharp
using ArchUnitNET.Core;
using ArchUnitNET.Fluent;
using static ArchUnitNET.Fluent.ArchRuleDefinition;

// Assuming your project has assemblies named 'YourApp.Presentation', 'YourApp.Application',
// 'YourApp.Domain', and 'YourApp.Infrastructure'

public class LayerDependencyTests
{
    private static readonly Architecture Architecture = new ArchLoader()
        .LoadAssemblies(
            typeof(YourApp.Presentation.Controllers.SomeController).Assembly,
            typeof(YourApp.Application.UseCases.SomeUseCase).Assembly,
            typeof(YourApp.Domain.Entities.SomeEntity).Assembly,
            typeof(YourApp.Infrastructure.Repositories.SomeRepository).Assembly
        )
        .Build();

    [Fact]
    public void ApplicationLayer_ShouldOnlyDependOnDomainLayer()
    {
        var applicationLayer = Architecture.Layers.Single(l => l.Name == "Application");
        var domainLayer = Architecture.Layers.Single(l => l.Name == "Domain");
        var infrastructureLayer = Architecture.Layers.Single(l => l.Name == "Infrastructure");

        // Explicitly define layers using assembly predicates for robustness
        var application = Target.Assembly(typeof(YourApp.Application.UseCases.SomeUseCase).Assembly);
        var domain = Target.Assembly(typeof(YourApp.Domain.Entities.SomeEntity).Assembly);
        var infrastructure = Target.Assembly(typeof(YourApp.Infrastructure.Repositories.SomeRepository).Assembly);

        Sut(application).Should().OnlyDependOn(domain)
            .Because("the Application layer orchestrates use cases and should not have direct knowledge of infrastructure concerns.")
            .Check(Architecture);

        Sut(application).Should().NotDependOn(infrastructure)
            .Because("the Application layer must be isolated from infrastructure details.")
            .Check(Architecture);
    }
}
```

A common hurdle with ArchUnitNET involves accurately mapping your project's assembly structure to defined architectural layers. The `Layer("LayerName")` predicate relies on naming conventions that might not precisely match your project's assembly names. In such scenarios, the rules can fail unexpectedly. A more robust approach, as demonstrated, is to define your layers using `Target.Assembly()` with specific types from those assemblies, ensuring your architectural boundaries are clearly and reliably identified, independent of simple naming patterns.

**Try it:** Ask Claude Code to "Write an ArchUnitNET test for a .NET Core application to ensure the 'Presentation' layer does not directly reference types within the 'Domain' layer."
