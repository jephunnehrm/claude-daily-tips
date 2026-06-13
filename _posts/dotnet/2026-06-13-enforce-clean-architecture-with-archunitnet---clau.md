---
layout: post
title: "Enforce Clean Architecture with ArchUnitNET & Claude Code"
date: 2026-06-13
type: how-to
summary: "Automatically verify layer dependencies in your .NET Core applications using ArchUnitNET tests, guided by Claude Code."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - automation
---



![Enforce Clean Architecture with ArchUnitNET & Claude Code](assets/images/placeholder.jpg)



As .NET developers tackling increasingly complex applications, the insidious creep of architectural drift is a constant threat. Manually ensuring that, for instance, your core business logic remains isolated from UI concerns becomes a fragile, time-consuming endeavor as the codebase expands. This is precisely where automated architectural testing becomes indispensable. ArchUnitNET, a robust .NET port of the lauded Java ArchUnit, empowers you to codify and enforce these critical architectural boundaries. However, translating abstract architectural principles into effective ArchUnitNET code can present an initial learning curve.

This is where Claude Code can act as a powerful accelerator for your architectural testing adoption. By articulating your desired architectural rules in plain English, Claude Code can generate the foundational ArchUnitNET C# code. For example, you can prompt it with: "Create an ArchUnitNET test that prevents the 'Domain' project from depending on the 'Web' project." Claude Code, with its understanding of .NET project structures and common architectural paradigms, can translate this intent into executable C# leveraging ArchUnitNET's expressive fluent API.

Consider the common Clean Architecture principle of isolating the `Domain` layer. To enforce that `Domain` should have no direct dependencies on `Infrastructure` or `Presentation`, you would typically house ArchUnitNET tests in a dedicated test project. After describing this rule to Claude Code, you might receive code similar to this:

```csharp
using ArchUnitNET.Domain;
using ArchUnitNET.xUnit;
using Xunit;

// Assuming your projects follow a common naming convention for assembly markers
using MyProject.Domain;
using MyProject.Infrastructure;
using MyProject.Application;
using MyProject.Web;

namespace MyProject.Tests.Architecture;

public class LayerDependenciesTests
{
    // Load all relevant assemblies to build the architectural model.
    // AssemblyMarker types are placeholders to reference the assemblies.
    private static readonly Architecture Architecture = new ArchLoader().LoadAssemblies(
        typeof(DomainAssemblyMarker).Assembly,
        typeof(InfrastructureAssemblyMarker).Assembly,
        typeof(ApplicationAssemblyMarker).Assembly,
        typeof(WebAssemblyMarker).Assembly
    ).Build();

    private static readonly ArchRuleLibrary Rules = new ArchRuleLibrary(Architecture);

    [Fact]
    public void Domain_ShouldNotDependOnInfrastructureOrPresentation()
    {
        // Define the layers based on your project's logical structure.
        var domainLayer = Architecture.Layers.Single(l => l.Name == "Domain");
        var infrastructureLayer = Architecture.Layers.Single(l => l.Name == "Infrastructure");
        var presentationLayer = Architecture.Layers.Single(l => l.Name == "Presentation");

        // Enforce the rule: Domain layer should not be nested within or depend on Infrastructure or Presentation.
        // Check this rule across all assemblies that are part of your main project namespace ("MyProject.").
        Rules.LayerShouldNotBeNestedInLayer(domainLayer, infrastructureLayer)
             .Or(domainLayer, presentationLayer)
             .Check(Architecture.Assemblies.Where(a => a.FullName.StartsWith("MyProject.")));
    }
}

// Placeholder types to reference assemblies. Ensure these exist in their respective projects.
public class DomainAssemblyMarker {}
public class InfrastructureAssemblyMarker {}
public class ApplicationAssemblyMarker {}
public class WebAssemblyMarker {}
```

While powerful, it's crucial to understand that ArchUnitNET, and by extension Claude Code's output, primarily analyzes *assembly and namespace dependencies*. It doesn't inherently grasp the *semantic intent* of every method call. If your architecture relies on subtle indirect dependencies or specific polymorphic usage patterns that violate your intended rules, you may need to manually refine your ArchUnitNET code to account for these nuances. Furthermore, accurate architectural rule enforcement hinges on correctly configuring the `ArchLoader` to include all relevant assemblies in your solution.

**Try it:** Describe a layer dependency rule you want to enforce in your .NET project to Claude Code, e.g., "Ensure the Application layer only depends on the Domain layer."
