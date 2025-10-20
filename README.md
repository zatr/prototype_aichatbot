# AI chatbot prototype
This prototype uses the FastMCP library and GPT4ALL local LLM. An example API is provided and setup as a resource for the MCP server. GPT4ALL is setup as a tool.


## Getting started
1. Install requirements

    ```
    pip install -r requirements.txt
    ```

2. Run the API server

    ```
    python3 api.py
    ```

3. Run the MCP Client, which provides the chatbot

    ```
    python3 mcp_client.py
    ```

    You should see something like this in your terminal:
    ```
    Chatbot Started!
    Commands:
        quit                           - Exit the chatbot
        @resources                     - List available resources
        @resource <name> <arg1=value1> - Get a resource with arguments
        /prompts                       - List available prompts
        /prompt <name> <arg1=value1>   - Execute a prompt with arguments

    Query:
    ```

4. Use the chatbot prompt to list resources:
    ```
    Query: @resources

    Available resources:
    - api_test: Call the test endpoint of our Flask API
    - api_get_data: Call the get data endpoint of our Flask API
    ```

5. Use the chatbot prompt to get data from the API:
    ```
    Query: @resource api_get_data
    Response:
    {
    "A": "Data 1",
    "B": "Data 2",
    "C": "Data 3"
    }
    ```

6. Use the chatbot prompt to learn about the MCP server with the GPT4ALL local LLM:
    ```
    Query: What is a MCP server?
    Response:
    A great question!

    In the context of Large Language Models (LLMs) and their deployment, an MCP (Model Control Protocol) server plays a crucial role in managing and controlling the interactions between multiple models, users, or applications.
    ```
