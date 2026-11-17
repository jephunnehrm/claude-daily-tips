---
layout: post
title: "Efficient Blazor Lists with Claude Code Virtualization"
date: 2026-11-17
type: how-to
summary: "Use Claude Code to quickly create a Blazor virtualized list for improved performance with large data sets."
image: "assets/images/placeholder.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - productivity
---



![Efficient Blazor Lists with Claude Code Virtualization](assets/images/placeholder.jpg)



Displaying large collections of data in Blazor applications often results in sluggish performance, characterized by slow loading times, UI unresponsiveness, and excessive memory consumption. A well-established solution to this common pain point is implementing virtual scrolling. This technique renders only the items currently visible within the user's viewport, dramatically reducing the DOM size and improving perceived performance. However, manually building robust virtual scrolling for complex data models or dynamic data sources can be a time-consuming and error-prone endeavor.

Leveraging large language models like Claude Code can significantly streamline the creation of virtualized Blazor lists. Instead of meticulously crafting the intricate UI virtualization logic from scratch, you can prompt Claude Code to generate the foundational components. This accelerates the process by providing a starting point for rendering subsets of your data and managing the logic for fetching additional items as the user scrolls. By offloading this complex UI pattern generation, developers can dedicate more time to core application logic and business requirements.

Consider this conceptual prompt: "Generate a Blazor component for a virtualized list that displays 1000 mock user objects, loading more items when the user scrolls near the end." Claude Code can assist in producing code that utilizes a `div` with scrollbar functionality, intelligently rendering a defined number of items above and below the current viewport. While the exact output can vary, the aim is to obtain a functional Blazor component that efficiently handles large datasets.

A crucial limitation to acknowledge, regardless of whether you use AI-generated code or manual implementation, is the management of dynamically changing data. If your underlying collection undergoes modifications (insertions, deletions, or reordering) *after* the initial rendering, the virtualization logic may require substantial adjustments to accurately reflect these changes and maintain viewport integrity. Furthermore, the efficiency of your data fetching strategy, particularly when interacting with external APIs for real-time updates or pagination, is paramount to the overall success of the virtualized list.

```csharp
@using Microsoft.AspNetCore.Components

<div @ref="_scrollContainer" style="height: 400px; overflow-y: auto;" @onscroll="HandleScroll">
    <div style="height: @(TotalItemCount * ItemHeight)px; position: relative;">
        @foreach (var item in VisibleItems)
        {
            <div style="position: absolute; top: @(GetItemTopPosition(item))px; height: @ItemHeight px;">
                @ItemTemplate(item)
            </div>
        }
    </div>
</div>

@code {
    [Parameter] public List<T> AllItems { get; set; } = new List<T>();
    [Parameter] public RenderFragment<T> ItemTemplate { get; set; }
    [Parameter] public int ItemHeight { get; set; } = 30; // Assume a fixed item height for simplicity
    [Parameter] public int ItemsToRender { get; set; } = 10; // Number of items to render beyond viewport

    private List<T> VisibleItems { get; set; } = new List<T>();
    private ElementReference _scrollContainer;
    private int _startIndex = 0;

    private int TotalItemCount => AllItems.Count;

    protected override void OnInitialized()
    {
        UpdateVisibleItems();
    }

    private async Task HandleScroll()
    {
        var scrollTop = await GetScrollTopAsync();
        var newStartIndex = (int)(scrollTop / ItemHeight) - ItemsToRender;
        newStartIndex = Math.Max(0, newStartIndex);

        if (newStartIndex != _startIndex)
        {
            _startIndex = newStartIndex;
            UpdateVisibleItems();
            StateHasChanged();
        }
    }

    private void UpdateVisibleItems()
    {
        var viewportHeight = 400; // Hardcoded for example, should be dynamic
        var itemsInViewport = (int)(viewportHeight / ItemHeight);
        var endIndex = Math.Min(_startIndex + itemsInViewport + 2 * ItemsToRender, TotalItemCount);

        VisibleItems.Clear();
        if (_startIndex < TotalItemCount)
        {
            for (int i = _startIndex; i < endIndex; i++)
            {
                VisibleItems.Add(AllItems[i]);
            }
        }
    }

    private double GetItemTopPosition(T item)
    {
        var index = AllItems.IndexOf(item);
        return index * ItemHeight;
    }

    private async Task<double> GetScrollTopAsync()
    {
        if (_scrollContainer.Id == null) return 0;
        return await _scrollContainer.GetElementInfoAsync("scrollTop");
    }

    // Extension method to get element property, you'd need to implement this or use a library
    // For a real-world scenario, you might use JS interop for more robust element property access.
    // Example stub:
    // public static class ElementReferenceExtensions
    // {
    //     public static async Task<double> GetElementInfoAsync(this ElementReference element, string propertyName)
    //     {
    //         // Implement JS interop to get element.propertyName
    //         return 0;
    //     }
    // }
}
```
