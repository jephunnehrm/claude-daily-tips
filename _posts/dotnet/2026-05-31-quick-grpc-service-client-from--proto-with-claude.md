---
layout: post
title: "Quick gRPC Service/Client from .proto with Claude Code"
date: 2026-05-31
type: how-to
summary: "Quickly create boilerplate gRPC service and client code in .NET from a .proto file using Claude Code."
image: "/claude-daily-tips/assets/images/dotnet-2026-05-31-quick-grpc-service-client-from--proto-with-claude.jpg"
tags:
  - dotnet
  - csharp
  - claude-code
  - devtools
  - productivity
---



![Quick gRPC Service/Client from .proto with Claude Code](/claude-daily-tips/assets/images/dotnet-2026-05-31-quick-grpc-service-client-from--proto-with-claude.jpg)



Tired of the repetitive grind of generating gRPC service interfaces, message contracts, and client stubs from `.proto` files in .NET? Manually crafting these components is a known productivity drain, prone to errors, and a significant bottleneck when your API schemas evolve. Imagine the acceleration you could achieve if an AI could intimately understand your `.proto` definitions and directly produce the ready-to-use C# code. Claude Code excels at this, leveraging its understanding of your gRPC contracts to drastically reduce boilerplate.

The magic happens through the `claude` CLI. Once your gRPC service contract is defined in a `.proto` file, like a standard `Greeter` service, you can prompt Claude Code to generate the C# equivalents. This process is streamlined using a command that specifies your input `.proto` file, the desired output directory, and critically, the target language and mode. For gRPC, this means instructing Claude to produce C# code specifically for gRPC services and clients.

Here’s the command to kickstart this workflow. Assuming your `greeter.proto` resides in the project root and you want generated code within a `Protos` directory:

```bash
claude gen --input greeter.proto --output Protos --lang csharp --mode grpc
```

This command directs Claude Code to parse `greeter.proto` and generate C# code into the `Protos` folder, specifically configuring it for gRPC. The `--mode grpc` flag is paramount; it ensures that Claude generates the correct gRPC-specific interfaces (like `Greeter.GreeterBase`), well-defined message classes (e.g., `HelloReply`, `HelloRequest`), and efficient client stubs. This direct generation bypasses the intermediate steps often required by traditional tools.

A common pitfall when adopting AI-driven code generation for gRPC is dependency management and the integration of generated code. Ensure your `.csproj` file includes the necessary gRPC NuGet packages. For services, this is typically `Grpc.AspNetCore`, and for clients, `Grpc.Net.Client`. Additionally, if your `.proto` file relies on other schemas via `import` directives, Claude Code needs access to those dependencies. You might need to configure Claude to include additional input paths or ensure these imported files are discoverable within your project structure.
