#!/usr/bin/env python3

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from helper import load_env
load_env()

import os
import yaml
import pathlib
from crewai import Agent, Task, Crew, Process, LLM
from tools import PokerAnalysisTool
from models.poker_metrics import PokerAnalysisResult

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()
CSV_PATH = str(BASE_DIR / 'data' / 'Gui Report total.csv')

# Initialize tools
poker_analysis_tool = PokerAnalysisTool(CSV_PATH)

# Set Claude as LLM
claude_llm = LLM( 
                 model="claude-3-5-sonnet-20241022",
                 api_key=os.environ["ANTHROPIC_API_KEY"])

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def create_crew(agents_config, tasks_config):
    # Creating Agents
    metrics_analyst_agent = Agent(
        config=agents_config['metrics_analyst'],
        verbose=True,
        cache=True,
        tools=[poker_analysis_tool],
        llm=claude_llm
    )

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
    generate_metrics_summary = Task(
        config=tasks_config['generate_metrics_summary'],
        agent=metrics_analyst_agent,
        output_pydantic=PokerAnalysisResult,
        output_file='output/metrics_summary.md'
    )

    create_performance_report = Task(
        config=tasks_config['create_performance_report'],
        agent=report_creator_agent,
        context=[generate_metrics_summary],
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
        context=[
            generate_metrics_summary,
            create_performance_report,
            prepare_educational_content
        ],
        output_file='output/final_summary.md'
    )

    # Creating Crew
    crew = Crew(
        agents=[
            metrics_analyst_agent,
            report_creator_agent,
            educator_agent,
            final_writer_agent
        ],
        tasks=[
            generate_metrics_summary,
            create_performance_report,
            prepare_educational_content,
            generate_final_summary
        ],
        verbose=True,
        process=Process.sequential
    )

    return crew

def main():
    # Load configurations
    agents_config = load_config('config/agents.yaml')
    tasks_config = load_config('config/tasks.yaml')

    # Create and run crew
    crew = create_crew(agents_config, tasks_config)
    result = crew.kickoff()

    print("\nCrew execution completed!")
    print("Results:", result)

    # Calculate and display costs
    costs = 0.150 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
    print(f"\nTotal costs: ${costs:.4f}")
    
    return result

if __name__ == "__main__":
    main()
