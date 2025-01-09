import os
import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SerperSearchInput(BaseModel):
    """Input schema for SerperSearchTool."""
    query: str = Field(..., description="The search query to be executed")
    num_results: int = Field(default=10, description="Number of results to return")

class SerperSearchTool(BaseTool):
    name: str = "Search the internet"
    description: str = """
    Search the internet for information about a specific topic. 
    Returns formatted results with titles, links, and descriptions.
    
    Args:
        query: The search query to execute
        num_results: Optional. Number of results to return (default: 10)
    """
    args_schema: Type[BaseModel] = SerperSearchInput

    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute a web search using the Serper API."""
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError("SERPER_API_KEY environment variable not set")

        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query,
            'num': num_results
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json()

            # Format the results
            formatted_results = []
            if 'organic' in results:
                for item in results['organic']:
                    title = item.get('title', 'No title')
                    link = item.get('link', 'No link')
                    snippet = item.get('snippet', 'No description')
                    formatted_results.append(f"Title: {title}\nLink: {link}\nDescription: {snippet}\n")

            return "\n---\n".join(formatted_results) if formatted_results else "No results found."

        except requests.exceptions.RequestException as e:
            return f"Error performing search: {str(e)}"

    async def _arun(self, query: str, num_results: int = 10) -> str:
        """Run async search with the provided query."""
        return self._run(query, num_results)
