from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from langchain_core.tools import StructuredTool
from langchain_core.utils.function_calling import BaseModel

from pydantic import BaseModel


from pydantic import BaseModel

class WebSearchInput(BaseModel):
    query: str

def web_search_tool(query: str) -> str:
    # Implement the web search logic here
    return f"Results for: {query}"

web_search_tool_definition = {
    "name": "web_search_tool",
    "description": "Search the internet for relevant information.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query to retrieve information."},
        },
        "required": ["query"],
    },
    "function": web_search_tool,  # Reference to the actual function
}

@tool
def web_search_tool(k=3):
    """Search the internet"""
    return TavilySearchResults(k=k)

def get_web_search_tool(k=3):
    return TavilySearchResults(k=k)