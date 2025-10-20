import requests
import json
from fastmcp import FastMCP
from gpt4all import GPT4All


mcp = FastMCP("MCP server")
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
API_BASE_URL = "http://127.0.0.1:5000"


@mcp.resource("api://test")
def api_test() -> str:
    """Call the test endpoint of our Flask API"""
    response = requests.get(f"{API_BASE_URL}/test")
    print(response)
    if response.ok:
        return response.text
    return "API request failed"


@mcp.resource("api://get_data")
def api_get_data() -> str:
    """Call the get data endpoint of our Flask API"""
    response = requests.get(f"{API_BASE_URL}/get_data")
    if response.ok:
        return response.text
    return "API request failed"


@mcp.tool
def execute_gpt4all(prompt: str) -> str:
    """Generate a response using the GPT4All model

    Args:
        prompt (str): The input prompt for the model.
    Returns:
        str: The generated response from the model."""
    with model.chat_session():
        return model.generate(prompt, max_tokens=50)


if __name__ == "__main__":
    mcp.run()
