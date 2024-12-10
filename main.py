#!/usr/bin/env python3

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from helper import load_env
load_env()

import os
import yaml
from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    PDFSearchTool,
    CSVSearchTool
)

pdf_tool = PDFSearchTool('data/Kill Everyone_ Advanced Strategies for No-Limit Hold Em Poker Tournaments and Sit-n-Gos - PDF Room.pdf')
csv_tool = CSVSearchTool('data/Gui Report total.csv')

# Set OpenAI Model
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o'


def load_configs():
    # Define file paths for YAML configurations
    files = {
        'agents': 'config/agents.yaml',
        'tasks': 'config/tasks.yaml'
    }

    # Load configurations from YAML files
    configs = {}
    for config_type, file_path in files.items():
        with open(file_path, 'r') as file:
            configs[config_type] = yaml.safe_load(file)

    return configs['agents'], configs['tasks']

def create_crew(agents_config, tasks_config):
    # Creating Agents
    metrics_analyst_agent = Agent(
        config=agents_config['metrics_analyst'],
        verbose=True,
        cache=True,
        tools=[
            csv_tool
        ]
    )

    report_creator_agent = Agent(
        config=agents_config['report_creator'],
        verbose=True,
        tools=[
            pdf_tool
        ]
    )

    educator_agent = Agent(
        config=agents_config['educator'],
        verbose=True,
        tools=[
            pdf_tool
        ]
    )

    final_writer_agent = Agent(
        config=agents_config['final_writer'],
        verbose=True
    )


    # Creating Tasks
    generate_metrics_summary = Task(
        config=tasks_config['generate_metrics_summary'],
        agent=metrics_analyst_agent,
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
    agents_config, tasks_config = load_configs()

    # Create and run the crew
    crew = create_crew(agents_config, tasks_config)
    result = crew.kickoff()
    print(result)

    # Calculate and display costs
    costs = 0.150 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
    print(f"\nTotal costs: ${costs:.4f}")
    
    return result

if __name__ == "__main__":
    main()
