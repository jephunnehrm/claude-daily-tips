---
layout: post
title: "Blazor Server Re-render Stalls After State Change? Try This"
date: 2026-07-31
type: troubleshooting
summary: "Diagnose and fix Blazor Server components stuck without re-rendering using Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-07-31-blazor-server-re-render-stalls-after-state-change.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
---



![Blazor Server Re-render Stalls After State Change? Try This](/claude-daily-tips/assets/images/dotnet-2026-07-31-blazor-server-re-render-stalls-after-state-change.jpg)



It's a frustrating moment for any ASP.NET Core developer: you change state in your Blazor Server component, expecting the UI to update, but... nothing happens. The component seems to have frozen, stubbornly refusing to re-render. This often occurs when Blazor's change detection mechanism fails to recognize a state modification, particularly with complex object graphs or asynchronous operations that don't properly signal back to the UI thread. Debugging these subtle issues can involve tedious breakpoints, manual UI refreshes, and a significant amount of guesswork.

The key to these rendering stalemates often lies in how Blazor's `ComponentBase` manages state updates and triggers re-renders. Unlike traditional web frameworks where DOM manipulation directly signals changes, Blazor Server relies on a robust internal change detection system. When you modify a property, especially one within a deeply nested object, Blazor might not inherently detect this mutation if the top-level reference hasn't changed. This is why direct property assignments on the component's own state variables are crucial, and why modifying nested properties within an existing object might go unnoticed by the framework.

Consider the common scenario of fetching data asynchronously. If you update a component property with the fetched data using `await` within an event handler or `OnInitializedAsync`, and this update isn't properly marshaled back to the UI thread, Blazor won't know to re-render. The underlying SignalR connection handles communication, but Blazor's component lifecycle still requires explicit notification. This is where understanding the implications of `async`/`await` on the UI thread becomes vital. Without proper synchronization, like ensuring asynchronous operations eventually lead to a `StateHasChanged()` call or an `InvokeAsync()` for UI updates, the UI can appear frozen.

A concrete example of this "gotcha" is modifying a `List<T>` directly. While `_items.Add("New Item")` seems straightforward, if `_items` itself was assigned in a way that Blazor's change detection doesn't track as a new assignment, the UI might not update. The framework primarily detects changes when a component's property is *reassigned* to a new value, thus creating a new reference. To reliably trigger a re-render in such cases, you need to either explicitly call `StateHasChanged()` after the modification, or, for scenarios where the list itself might not be tracked due to how it was initialized or passed, creating a new `List<T>` instance with the updated items ensures a distinct change is recognized by Blazor.

```csharp
// Example of a common rendering pitfall
public partial class MyComponent : ComponentBase
{
    private List<string> _items = new List<string>();

    protected override async Task OnInitializedAsync()
    {
        await Task.Delay(1000); // Simulate async data fetch
        var fetchedItems = await FetchDataAsync();

        // Potential issue: Modifying _items directly might not always trigger a re-render if Blazor's change detection
        // doesn't pick up the AddRange operation reliably, especially if _items was initialized
        // in a way that doesn't create a new reference for Blazor to track.
        _items.AddRange(fetchedItems);

        // To guarantee a re-render, explicitly notify Blazor:
        StateHasChanged();

        // Alternatively, for complex scenarios, re-assigning the list can be more robust:
        // var updatedItems = new List<string>(_items);
        // updatedItems.AddRange(fetchedItems);
        // _items = updatedItems;
        // StateHasChanged(); // Still good practice to explicitly call
    }

    private Task<IEnumerable<string>> FetchDataAsync()
    {
        // Simulate fetching data
        return Task.FromResult<IEnumerable<string>>(new[] { "Item A", "Item B" });
    }
}
```
