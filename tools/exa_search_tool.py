import os
from exa_py import Exa
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class ExaSearchInput(BaseModel):
    """Input schema for ExaSearchTool."""
    query: str = Field(..., description="The search query to be executed")
    num_results: int = Field(default=10, description="Number of results to return")

class ExaSearchTool(BaseTool):
    name: str = "Semantic search using Exa"
    description: str = """
    Performs a semantic search using Exa's API and returns formatted results.
    Uses neural search with autoprompt for improved query understanding.
    
    Args:
        query: The search query string
        num_results: Optional. Number of results to return (default: 3)
    """
    args_schema: Type[BaseModel] = ExaSearchInput

    def _run(self, query: str, num_results: int = 3) -> str:
        """Execute a semantic search using the Exa API."""
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            raise ValueError("EXA_API_KEY environment variable not set")

        try:
            exa = Exa(api_key)
            response = exa.search_and_contents(
                query,
                type="neural",
                use_autoprompt=True,
                num_results=num_results,
                highlights=True
            )

            # Format results in a clean, readable way
            formatted_results = []
            for idx, result in enumerate(response.results, 1):
                formatted_result = (
                    f"\n--- Result {idx} ---\n"
                    f"Title: {result.title}\n"
                    f"URL: {result.url}\n"
                    f"Highlights:\n"
                )
                
                # Add highlights with proper formatting
                for highlight in result.highlights:
                    formatted_result += f"• {highlight}\n"
                
                formatted_results.append(formatted_result)

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error performing search: {str(e)}"
