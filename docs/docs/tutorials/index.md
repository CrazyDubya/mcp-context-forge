# 📚 Tutorials

> Step-by-step guides to help you deploy and integrate MCP Gateway and related components using both **cloud-native** and **local containerized** environments.

---

## 🚀 End-to-End Example: From REST API to Virtual Server

This tutorial walks you through a complete, end-to-end example of how to use the MCP Gateway to wrap an existing REST API, create a virtual server, and expose it to your clients. You'll learn how to:

- Register a public REST API as a tool in the gateway.
- Create a virtual server to house your new tool.
- Associate the tool with the virtual server.
- Invoke the tool through the virtual server's endpoint using `curl`.

👉 [Read the full guide](end-to-end-example.md)

---

## 🚀 Cloud Deployment with Argo CD and IBM Cloud Kubernetes Service

This guide walks you through deploying the **MCP Gateway Stack** on **IBM Cloud Kubernetes Service (IKS)** using **Helm** and **Argo CD** for GitOps-based lifecycle management. You'll learn how to:

- Build and push container images to IBM Container Registry
- Provision an IKS cluster with VPC-native networking
- Deploy the full MCP Gateway Helm chart via Argo CD
- Configure services like PostgreSQL, Redis, and TLS
- Connect AI clients like VS Code Copilot and LangChain Agent

👉 [Read the full guide](argocd-helm-deployment-ibm-cloud-iks.md)

---

## 🧠 Local Deployment of OpenWebUI + MCP Tools

This tutorial helps you set up **OpenWebUI** integrated with **Ollama**, **LiteLLM**, **MCPO**, and the **MCP Gateway** in a local containerized environment using Docker. It covers:

- Running LLMs locally via Ollama
- Using LiteLLM as a proxy for unified model access
- Bridging MCP tools through MCPO to OpenWebUI
- Managing MCP servers with the MCP Gateway
- Connecting it all through Docker networks

Perfect for experimenting on your workstation or air-gapped environments.

👉 [View the tutorial](openwebui-tutorial.md)

---


## 📦 Additional Resources

- [MCP Gateway GitHub](https://github.com/ibm/mcp-context-forge)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [OpenWebUI Documentation](https://docs.openwebui.com/)

Stay tuned for more guides on CI/CD, hybrid federation, observability, and secure API operations.
