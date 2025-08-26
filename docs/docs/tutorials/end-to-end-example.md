# End-to-End Example: From REST API to Virtual Server

This tutorial will walk you through a complete, end-to-end example of how to use the MCP Gateway to wrap an existing REST API, create a virtual server, and expose it to your clients.

We will use the [Public Cat Facts API](https://catfact.ninja/) as our example REST service.

## Prerequisites

- The MCP Gateway is running and accessible.
- You have a valid authentication token for the gateway.

## Step 1: Register the REST API as a Tool

First, we need to register the Cat Facts API as a tool in the gateway. We will use the `/tools` endpoint for this.

The Cat Facts API has an endpoint at `https://catfact.ninja/fact` that returns a random cat fact. It's a simple GET request with no parameters.

Here's the `curl` command to register this API as a tool:

```bash
curl -X POST http://localhost:4444/tools \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "get_cat_fact",
    "description": "Returns a random cat fact.",
    "url": "https://catfact.ninja/fact",
    "integration_type": "REST",
    "request_type": "GET",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}'
```

Replace `YOUR_TOKEN` with your actual authentication token.

If the request is successful, you will get a JSON response with the details of the newly created tool. Make a note of the `id` of the tool from the response.

## Step 2: Create a Virtual Server

Next, we'll create a virtual server to house our new cat fact tool. A virtual server acts as a container for a specific set of tools, resources, and prompts.

We'll use the `/servers` endpoint to create the virtual server.

```bash
curl -X POST http://localhost:4444/servers \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "animal_facts_server",
    "description": "A server for getting interesting facts about animals."
}'
```

This will create a new, empty virtual server. Make a note of the `id` of the server from the response.

## Step 3: Associate the Tool with the Virtual Server

Now, we need to link our new tool to our new virtual server. We do this by updating the virtual server and providing a list of associated tool IDs.

We'll use the `PUT` method on the `/servers/{server_id}` endpoint.

```bash
curl -X PUT http://localhost:4444/servers/YOUR_SERVER_ID \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "associated_tools": ["YOUR_TOOL_ID"]
}'
```

Replace `YOUR_SERVER_ID` with the ID of the server you created in Step 2, and `YOUR_TOOL_ID` with the ID of the tool you created in Step 1.

## Step 4: Invoke the Tool Through the Virtual Server

Now that our tool is associated with our virtual server, we can invoke it through the server's endpoint. The gateway exposes a dedicated endpoint for each virtual server.

The endpoint for invoking a tool on a virtual server is `/servers/{server_id}/mcp`. We will send a JSON-RPC request to this endpoint.

```bash
curl -X POST http://localhost:4444/servers/YOUR_SERVER_ID/mcp \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "get_cat_fact",
    "params": {}
}'
```

Replace `YOUR_SERVER_ID` with the ID of your virtual server.

The gateway will receive this request, look up the `get_cat_fact` tool associated with the specified virtual server, and invoke the underlying REST API. The response from the Cat Facts API will be wrapped in a JSON-RPC response and returned to you.

The response should look something like this:

```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "{\"fact\":\"A cat can spend five or more hours a day grooming itself.\",\"length\":55}"
            }
        ]
    }
}
```

Congratulations! You have successfully wrapped a REST API, created a virtual server, and invoked the tool through the MCP Gateway.
