Tools
Understanding and leveraging tools within the CrewAI framework for agent collaboration and task execution.

​
Introduction
CrewAI tools empower agents with capabilities ranging from web searching and data analysis to collaboration and delegating tasks among coworkers. This documentation outlines how to create, integrate, and leverage these tools within the CrewAI framework, including a new focus on collaboration tools.

​
What is a Tool?
A tool in CrewAI is a skill or function that agents can utilize to perform various actions. This includes tools from the CrewAI Toolkit and LangChain Tools, enabling everything from simple searches to complex interactions and effective teamwork among agents.

​
Key Characteristics of Tools
Utility: Crafted for tasks such as web searching, data analysis, content generation, and agent collaboration.
Integration: Boosts agent capabilities by seamlessly integrating tools into their workflow.
Customizability: Provides the flexibility to develop custom tools or utilize existing ones, catering to the specific needs of agents.
Error Handling: Incorporates robust error handling mechanisms to ensure smooth operation.
Caching Mechanism: Features intelligent caching to optimize performance and reduce redundant operations.
​
Using CrewAI Tools
To enhance your agents’ capabilities with crewAI tools, begin by installing our extra tools package:


pip install 'crewai[tools]'
Here’s an example demonstrating their use:

Code

import os
from crewai import Agent, Task, Crew
# Importing crewAI tools
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

# Set up API keys
os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API key
os.environ["OPENAI_API_KEY"] = "Your Key"

# Instantiate tools
docs_tool = DirectoryReadTool(directory='./blog-posts')
file_tool = FileReadTool()
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()

# Create agents
researcher = Agent(
    role='Market Research Analyst',
    goal='Provide up-to-date market analysis of the AI industry',
    backstory='An expert analyst with a keen eye for market trends.',
    tools=[search_tool, web_rag_tool],
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='Craft engaging blog posts about the AI industry',
    backstory='A skilled writer with a passion for technology.',
    tools=[docs_tool, file_tool],
    verbose=True
)

# Define tasks
research = Task(
    description='Research the latest trends in the AI industry and provide a summary.',
    expected_output='A summary of the top 3 trending developments in the AI industry with a unique perspective on their significance.',
    agent=researcher
)

write = Task(
    description='Write an engaging blog post about the AI industry, based on the research analyst’s summary. Draw inspiration from the latest blog posts in the directory.',
    expected_output='A 4-paragraph blog post formatted in markdown with engaging, informative, and accessible content, avoiding complex jargon.',
    agent=writer,
    output_file='blog-posts/new_post.md'  # The final blog post will be saved here
)

# Assemble a crew with planning enabled
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=True,
    planning=True,  # Enable planning feature
)

# Execute tasks
crew.kickoff()
​
Available CrewAI Tools
Error Handling: All tools are built with error handling capabilities, allowing agents to gracefully manage exceptions and continue their tasks.
Caching Mechanism: All tools support caching, enabling agents to efficiently reuse previously obtained results, reducing the load on external resources and speeding up the execution time. You can also define finer control over the caching mechanism using the cache_function attribute on the tool.
Here is a list of the available tools and their descriptions:

Tool	Description
BrowserbaseLoadTool	A tool for interacting with and extracting data from web browsers.
CodeDocsSearchTool	A RAG tool optimized for searching through code documentation and related technical documents.
CodeInterpreterTool	A tool for interpreting python code.
ComposioTool	Enables use of Composio tools.
CSVSearchTool	A RAG tool designed for searching within CSV files, tailored to handle structured data.
DALL-E Tool	A tool for generating images using the DALL-E API.
DirectorySearchTool	A RAG tool for searching within directories, useful for navigating through file systems.
DOCXSearchTool	A RAG tool aimed at searching within DOCX documents, ideal for processing Word files.
DirectoryReadTool	Facilitates reading and processing of directory structures and their contents.
EXASearchTool	A tool designed for performing exhaustive searches across various data sources.
FileReadTool	Enables reading and extracting data from files, supporting various file formats.
FirecrawlSearchTool	A tool to search webpages using Firecrawl and return the results.
FirecrawlCrawlWebsiteTool	A tool for crawling webpages using Firecrawl.
FirecrawlScrapeWebsiteTool	A tool for scraping webpages URL using Firecrawl and returning its contents.
GithubSearchTool	A RAG tool for searching within GitHub repositories, useful for code and documentation search.
SerperDevTool	A specialized tool for development purposes, with specific functionalities under development.
TXTSearchTool	A RAG tool focused on searching within text (.txt) files, suitable for unstructured data.
JSONSearchTool	A RAG tool designed for searching within JSON files, catering to structured data handling.
LlamaIndexTool	Enables the use of LlamaIndex tools.
MDXSearchTool	A RAG tool tailored for searching within Markdown (MDX) files, useful for documentation.
PDFSearchTool	A RAG tool aimed at searching within PDF documents, ideal for processing scanned documents.
PGSearchTool	A RAG tool optimized for searching within PostgreSQL databases, suitable for database queries.
Vision Tool	A tool for generating images using the DALL-E API.
RagTool	A general-purpose RAG tool capable of handling various data sources and types.
ScrapeElementFromWebsiteTool	Enables scraping specific elements from websites, useful for targeted data extraction.
ScrapeWebsiteTool	Facilitates scraping entire websites, ideal for comprehensive data collection.
WebsiteSearchTool	A RAG tool for searching website content, optimized for web data extraction.
XMLSearchTool	A RAG tool designed for searching within XML files, suitable for structured data formats.
YoutubeChannelSearchTool	A RAG tool for searching within YouTube channels, useful for video content analysis.
YoutubeVideoSearchTool	A RAG tool aimed at searching within YouTube videos, ideal for video data extraction.
​
