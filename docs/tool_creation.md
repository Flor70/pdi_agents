Creating your own Tools
Developers can craft custom tools tailored for their agent’s needs or utilize pre-built options.

There are two main ways for one to create a CrewAI tool:

​
Subclassing BaseTool
Code

from crewai.tools import BaseTool


class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "Clear description for what this tool is useful for, your agent will need this information to use it."

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "Result from custom tool"
​
Utilizing the tool Decorator
Code

from crewai.tools import tool
@tool("Name of my tool")
def my_tool(question: str) -> str:
    """Clear description for what this tool is useful for, your agent will need this information to use it."""
    # Function logic here
    return "Result from your custom tool"
​
Structured Tools
The StructuredTool class wraps functions as tools, providing flexibility and validation while reducing boilerplate. It supports custom schemas and dynamic logic for seamless integration of complex functionalities.

​
Example:
Using StructuredTool.from_function, you can wrap a function that interacts with an external API or system, providing a structured interface. This enables robust validation and consistent execution, making it easier to integrate complex functionalities into your applications as demonstrated in the following example:


from crewai.tools.structured_tool import CrewStructuredTool
from pydantic import BaseModel

# Define the schema for the tool's input using Pydantic
class APICallInput(BaseModel):
    endpoint: str
    parameters: dict

# Wrapper function to execute the API call
def tool_wrapper(*args, **kwargs):
    # Here, you would typically call the API using the parameters
    # For demonstration, we'll return a placeholder string
    return f"Call the API at {kwargs['endpoint']} with parameters {kwargs['parameters']}"

# Create and return the structured tool
def create_structured_tool():
    return CrewStructuredTool.from_function(
        name='Wrapper API',
        description="A tool to wrap API calls with structured input.",
        args_schema=APICallInput,
        func=tool_wrapper,
    )

# Example usage
structured_tool = create_structured_tool()

# Execute the tool with structured input
result = structured_tool._run(**{
    "endpoint": "https://example.com/api",
    "parameters": {"key1": "value1", "key2": "value2"}
})
print(result)  # Output: Call the API at https://example.com/api with parameters {'key1': 'value1', 'key2': 'value2'}
​
Custom Caching Mechanism
Tools can optionally implement a cache_function to fine-tune caching behavior. This function determines when to cache results based on specific conditions, offering granular control over caching logic.

Code

from crewai.tools import tool

@tool
def multiplication_tool(first_number: int, second_number: int) -> str:
    """Useful for when you need to multiply two numbers together."""
    return first_number * second_number

def cache_func(args, result):
    # In this case, we only cache the result if it's a multiple of 2
    cache = result % 2 == 0
    return cache

multiplication_tool.cache_function = cache_func

writer1 = Agent(
        role="Writer",
        goal="You write lessons of math for kids.",
        backstory="You're an expert in writing and you love to teach kids but you know nothing of math.",
        tools=[multiplication_tool],
        allow_delegation=False,
    )
    #...
​
Conclusion
Tools are pivotal in extending the capabilities of CrewAI agents, enabling them to undertake a broad spectrum of tasks and collaborate effectively. When building solutions with CrewAI, leverage both custom and existing tools to empower your agents and enhance the AI ecosystem. Consider utilizing error handling, caching mechanisms, and the flexibility of tool arguments to optimize your agents’ performance and capabilities.


How to Guides
Create Custom Tools
Comprehensive guide on crafting, using, and managing custom tools within the CrewAI framework, including new functionalities and error handling.

​
Creating and Utilizing Tools in CrewAI
This guide provides detailed instructions on creating custom tools for the CrewAI framework and how to efficiently manage and utilize these tools, incorporating the latest functionalities such as tool delegation, error handling, and dynamic tool calling. It also highlights the importance of collaboration tools, enabling agents to perform a wide range of actions.

​
Subclassing BaseTool
To create a personalized tool, inherit from BaseTool and define the necessary attributes, including the args_schema for input validation, and the _run method.

Code

from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "What this tool does. It's vital for effective utilization."
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, argument: str) -> str:
        # Your tool's logic here
        return "Tool's result"
​
Using the tool Decorator
Alternatively, you can use the tool decorator @tool. This approach allows you to define the tool’s attributes and functionality directly within a function, offering a concise and efficient way to create specialized tools tailored to your needs.

Code

from crewai.tools import tool

@tool("Tool Name")
def my_simple_tool(question: str) -> str:
    """Tool description for clarity."""
    # Tool logic here
    return "Tool output"
​
Defining a Cache Function for the Tool
To optimize tool performance with caching, define custom caching strategies using the cache_function attribute.

Code

@tool("Tool with Caching")
def cached_tool(argument: str) -> str:
    """Tool functionality description."""
    return "Cacheable result"

def my_cache_strategy(arguments: dict, result: str) -> bool:
    # Define custom caching logic
    return True if some_condition else False

cached_tool.cache_function = my_cache_strategy
By adhering to these guidelines and incorporating new functionalities and collaboration tools into your tool creation and management processes, you can leverage the full capabilities of the CrewAI framework, enhancing both the development experience and the efficiency of your AI agents.

