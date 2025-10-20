import asyncio
import shlex
from contextlib import AsyncExitStack
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ChatBot:
    """
    MCP (Model Context Protocol) ChatBot that connects to multiple MCP servers
    and provides a conversational interface.
    """

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.available_resources = []
        self.available_tools = []
        self.available_prompts = []
        self.sessions = {}

    async def cleanup(self):
        """Clean up resources and close all connections."""
        await self.exit_stack.aclose()

    async def connect_to_server(self, server_name, server_config):
        """Connect to a single MCP server and register its capabilities."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            await self._register_server_capabilities(session, server_name)

        except Exception as e:
            print(f"Error connecting to {server_name}: {e}")
            traceback.print_exc()

    async def connect_to_servers(self):
        """Load server configuration and connect to all configured MCP servers."""
        servers_data = {
            "mcpServers": {
                "mcp_server": {
                    "command": "fastmcp",
                    "args": [
                        "run",
                        "mcp_server.py",
                    ],
                },
            }
        }
        servers = servers_data.get("mcpServers")
        try:
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server config: {e}")
            traceback.print_exc()
            raise

    async def _register_server_capabilities(self, session, server_name):
        """Register tools, prompts and resources from a single server."""
        capabilities = [
            ("tools", session.list_tools, self._register_tools),
            ("prompts", session.list_prompts, self._register_prompts),
            ("resources", session.list_resources, self._register_resources),
        ]
        for capability_name, list_method, register_method in capabilities:
            try:
                response = await list_method()
                await register_method(response, session)
            except Exception as e:
                print(f"Server {server_name} doesn't support {capability_name}: {e}")

    async def _register_tools(self, response, session):
        """Register tools from server response."""
        for tool in response.tools:
            self.sessions[tool.name] = session
            self.available_tools.append(tool)

    async def _register_prompts(self, response, session):
        """Register prompts from server response."""
        if response and response.prompts:
            for prompt in response.prompts:
                self.sessions[prompt.name] = session
                self.available_prompts.append(
                    {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": prompt.arguments,
                    }
                )

    async def _register_resources(self, response, session):
        """Register resources from server response."""
        if response and response.resources:
            for resource in response.resources:
                self.sessions[resource.name] = session
                self.available_resources.append(resource)

    async def list_resources(self):
        """List all available resources."""
        if not self.available_resources:
            print("No resources available.")
            return
        print("\nAvailable resources:")
        for r in self.available_resources:
            print(f"- {r.name}: {r.description}")

    def _parse_command_arguments(self, query):
        """Parse command line with proper handling of quoted strings."""
        try:
            return shlex.split(query)
        except ValueError:
            print("Error parsing command. Check your quotes.")
            return None

    def _clean_quoted_value(self, value):
        """Remove surrounding quotes from argument values."""
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        return value

    def _parse_prompt_arguments(self, args_list):
        """Parse key=value arguments for prompt execution."""
        args = {}
        for arg in args_list:
            if "=" in arg:
                key, value = arg.split("=", 1)
                args[key] = self._clean_quoted_value(value)
        return args

    async def read_resource(self, resource_name, args):
        """Read MCP resource directly with given arguments."""
        resource = [r for r in self.available_resources if r.name == resource_name][0]
        session = self.sessions.get(resource_name)
        if not session:
            print(f"Resource '{resource_name}' not found.")
            return
        try:
            response = await session.read_resource(resource.uri)
            print(f"Response:")
            print(response.contents[0].text)
        except Exception as e:
            print(f"Error reading resource: {e}")

    async def process_query(self, query):
        """Process query with LLM"""
        tool_name = "execute_gpt4all"
        session = self.sessions.get(tool_name)
        if not session:
            print(f"Tool '{tool_name}' not found.")
            return
        try:
            response = await session.call_tool(tool_name, {"prompt": query})
            print(f"Response:")
            print(response.content[0].text)
        except Exception as e:
            print(f"Error calling tool: {e}")

    async def chat_loop(self):
        """Main interactive chat loop with command processing."""
        print("\nChatbot Started!")
        print("Commands:")
        print("  quit                           - Exit the chatbot")
        print("  @resources                     - List available resources")
        print("  @resource <name> <arg1=value1> - Get a resource with arguments")
        print("  /prompts                       - List available prompts")
        print("  /prompt <name> <arg1=value1>   - Execute a prompt with arguments")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if not query:
                    continue
                if query.lower() == "quit":
                    break
                # Handle resource requests (@command)
                if query.startswith("@"):
                    if query == "@resources":
                        await self.list_resources()
                    else:
                        parts = self._parse_command_arguments(query)
                        if len(parts) < 2:
                            print(
                                "Usage: @resource <name> <arg1=value1> <arg2=value2> ..."
                            )
                            continue
                        resource_name = parts[1]
                        args = self._parse_prompt_arguments(parts[2:])
                        await self.read_resource(resource_name, args)
                        continue
                else:
                    await self.process_query(query)
            except Exception as e:
                print(f"\nError in chat loop: {e}")
                traceback.print_exc()


async def main():
    """Main entry point for the MCP ChatBot application."""
    chatbot = ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
