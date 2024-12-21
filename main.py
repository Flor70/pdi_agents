#!/usr/bin/env python3

# Warning control
import warnings
warnings.filterwarnings('ignore')

import sys

# Load environment variables
from helper import load_env
load_env()

import os
import yaml
import pathlib
import asyncio
from crewai import Agent, Task, Crew, Process, LLM
from tools import CompleteInterviewTool
from interview_manager import InterviewManager
import json

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# Optional: Default model selection
OPENAI_MODEL_NAME ="gpt-4o-mini"

# Set Claude as LLM
def get_api_key(key_name):
    try:
        # Try to get from Streamlit secrets first
        import streamlit as st
        return st.secrets[key_name]
    except:
        # Fallback to environment variables
        return os.environ[key_name]

claude_llm = LLM( 
                 model="claude-3-5-haiku-20241022",
                 api_key=os.environ.get("CLAUDE_API_KEY"))

#claude-3-5-haiku-20241022
#claude-3-5-sonnet-20241022

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

async def create_crew(agents_config, tasks_config, interview_data=None):
    # Initialize interview tool
    interview_tool = CompleteInterviewTool()
    if interview_data:
        interview_tool.collected_data = interview_data
        # Interpola os dados da entrevista na descrição da task
        tasks_config['create_performance_report']['description'] = \
            tasks_config['create_performance_report']['description'].format(
                interview_data=interview_data
            )

    # Creating Agents
    report_creator_agent = Agent(
        config=agents_config['report_creator'],
        verbose=True,
        tools=[],
        cache=True,
        llm=claude_llm
    )

    educator_agent = Agent(
        config=agents_config['educator'],
        verbose=True,
        cache=True,
        llm=claude_llm
    )

    final_writer_agent = Agent(
        config=agents_config['final_writer'],
        verbose=True,
        llm=claude_llm,
        cache=True
    )

    # Creating Tasks
    create_performance_report = Task(
        config=tasks_config['create_performance_report'],
        agent=report_creator_agent,
        output_file='output/performance_report.md'
    )

    prepare_educational_content = Task(
        config=tasks_config['prepare_educational_content'],
        agent=educator_agent,
        context=[create_performance_report],
        output_file='output/educational_content.md'
    )

    generate_final_summary = Task(
        config=tasks_config['generate_final_summary'],
        agent=final_writer_agent,
        context=[create_performance_report, prepare_educational_content],
        output_file='output/final_summary.md'
    )

    # Creating Crew
    crew = Crew(
        agents=[
            report_creator_agent,
            educator_agent,
            final_writer_agent
        ],
        tasks=[
            create_performance_report,
            prepare_educational_content,
            generate_final_summary
        ],
        verbose=True,
        process=Process.sequential
    )

    return crew

async def main():
    # Load configurations
    agents_config = load_config('config/agents.yaml')
    tasks_config = load_config('config/tasks.yaml')

    # Inicializa e executa a entrevista
    interview_manager = InterviewManager()
    interview_data = await interview_manager.conduct_interview()

    if interview_data:
        # Create and run crew with interview data
        crew = await create_crew(agents_config, tasks_config, interview_data)
        result = crew.kickoff()

        print("\nCrew execution completed!")
        print("Results:", result)

        # Calculate and display costs
        costs = 0.150 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
        print(f"\nTotal costs: ${costs:.4f}")
        
        return result

if __name__ == "__main__":
    asyncio.run(main())
