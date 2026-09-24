---
layout: post
title: "Test Blazor Wizard Steps with Playwright & Claude Code"
date: 2026-09-24
type: how-to
summary: "Reliably test multi-step Blazor wizards from end-to-end using Playwright and Claude Code assistance."
image: "/claude-daily-tips/assets/images/dotnet-2026-09-24-test-blazor-wizard-steps-with-playwright---claude.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - automation
---



![Test Blazor Wizard Steps with Playwright & Claude Code](/claude-daily-tips/assets/images/dotnet-2026-09-24-test-blazor-wizard-steps-with-playwright---claude.jpg)



Testing multi-step wizard components in Blazor applications is a common challenge. Manually verifying each step, input validation, and state transitions across different stages is tedious and prone to errors. While end-to-end testing with Playwright offers a powerful solution for these scenarios, crafting comprehensive tests, especially for intricate UI flows, can still be a substantial undertaking. This is where AI-powered coding assistants like Claude Code can significantly streamline your test development, helping to generate robust Playwright test code.

To implement these tests, ensure you have Playwright for .NET installed. Add the `Microsoft.Playwright.NUnit` and `Microsoft.Playwright` NuGet packages to your test project. Consider a typical Blazor wizard with steps for user details, address, and payment. We aim to test the complete user journey, including form submissions, data validation, and seamless progression between stages.

Let's leverage Claude Code to generate a Playwright test for a straightforward two-step wizard. Imagine a scenario where the first step captures a username and the second collects an email. You can prompt Claude Code to generate the C# code for a Playwright test that navigates through these steps, populates data, and asserts the final state. For instance, a prompt like: "Generate a Playwright end-to-end test in C# for a Blazor wizard with two steps. Step 1 requires a username, and Step 2 requires an email. The test should fill in a username, advance to the next step, input an email, and then confirm successful navigation to the final completion page." Claude Code will then produce C# code utilizing the Playwright API to automate interactions with your Blazor component.

```csharp
using Microsoft.Playwright;
using NUnit.Framework;
using System.Threading.Tasks;

namespace BlazorWizardTests;

[TestFixture]
public class WizardTests
{
    private IPage _page;
    private IBrowser _browser;

    [SetUp]
    public async Task Setup()
    {
        var playwright = await Playwright.CreateAsync();
        _browser = await playwright.Chromium.LaunchAsync(new BrowserTypeLaunchOptions
        {
            Headless = true // Set to false to observe test execution
        });
        _page = await _browser.NewPageAsync();
        // Replace with your Blazor wizard's actual starting URL
        await _page.GotoAsync("http://localhost:5000/wizard");
    }

    [TearDown]
    public async Task Teardown()
    {
        await _browser.CloseAsync();
    }

    [Test]
    public async Task CanCompleteTwoStepWizard()
    {
        // Step 1: Enter Username
        await _page.FillAsync("#username", "testuser"); // Assuming an input with id="username"
        await _page.ClickAsync("button:has-text('Next')"); // Assuming a button with text 'Next'

        // Wait for the next step's elements to be visible (adjust selector/timeout as needed)
        await _page.WaitForSelectorAsync("#email");

        // Step 2: Enter Email
        await _page.FillAsync("#email", "testuser@example.com"); // Assuming an input with id="email"
        await _page.ClickAsync("button:has-text('Finish')"); // Assuming a button with text 'Finish'

        // Verify completion message (adjust selector/text as needed)
        await _page.WaitForSelectorAsync("text='Wizard Completed!'");
        var completionMessage = await _page.TextContentAsync("text='Wizard Completed!'");
        Assert.That(completionMessage, Is.Not.Null.Or.Empty);
    }
}
```

A critical consideration when automating Blazor applications is handling asynchronous operations. Blazor components, particularly those involving server-side rendering or sophisticated state management, require time to update their UI. Playwright tests must incorporate explicit waits—such as `WaitForSelectorAsync`, `WaitForNavigationAsync`, or `Page.WaitForLoadStateAsync`—to ensure elements are rendered and interactive before attempting any actions. Avoid relying on fixed `Task.Delay`, as this leads to brittle and unreliable tests. Always wait for specific, observable conditions to be met.

**Challenge:** Utilize Claude Code to help generate a Playwright test that verifies an error message is displayed when a required field in your Blazor wizard is intentionally left blank.
