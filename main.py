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
from crewai import Agent, Task, Crew, Process
from tools import CompleteInterviewTool
from tools.educational_content_tool import ReadEducationalDBTool
from interview_manager import InterviewManager

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()

# Optional: Default model selection
OPENAI_MODEL_NAME ="gpt-4o-2024-08-06"

def load_config(agents_file, tasks_file):
    """
    Load configuration files for agents and tasks.
    
    Args:
        agents_file: Path to the agents configuration file
        tasks_file: Path to the tasks configuration file
    
    Returns:
        Tuple containing agents and tasks configurations
    """
    with open(agents_file, 'r') as f:
        agents_config = yaml.safe_load(f)
    
    with open(tasks_file, 'r') as f:
        tasks_config = yaml.safe_load(f)
    
    return agents_config, tasks_config

async def create_crew(agents_config, tasks_config, interview_data=None, openai_api_key=None):
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")
    
    os.environ["OPENAI_API_KEY"] = openai_api_key

    # Initialize tools
    educational_db_tool = ReadEducationalDBTool()
    
    if interview_data:
        # Interpola os dados da entrevista nas descrições das tasks
        for task_name in ['analise_subjetiva_colaborador', 'recomendacao_conteudos']:
            if task_name in tasks_config:
                tasks_config[task_name]['description'] = \
                    tasks_config[task_name]['description'].format(
                        interview_data=interview_data
                    )

    # Creating Agents
    leitor_de_planilha = Agent(
        config=agents_config['leitor_de_planilha'],
        verbose=True,
        tools=[educational_db_tool],
        cache=True
    )

    analista_de_perfis = Agent(
        config=agents_config['analista_de_perfis'],
        verbose=True,
        tools=[],
        cache=True
    )

    analista_conteudo_educacional = Agent(
        config=agents_config['analista_conteudo_educacional'],
        verbose=True,
        tools=[],
        cache=True
    )

    pdi_specialist = Agent(
        config=agents_config['pdi_specialist'],
        verbose=True,
        tools=[],
        cache=True
    )

    final_writer = Agent(
        config=agents_config['final_writer'],
        verbose=True,
        tools=[],
        cache=True
    )

    # Creating Tasks
    ler_planilha = Task(
        config=tasks_config['ler_planilha'],
        agent=leitor_de_planilha,
    )

    analise_subjetiva_colaborador = Task(
        config=tasks_config['analise_subjetiva_colaborador'],
        agent=analista_de_perfis,
        context=[],  # Recebe apenas dados da entrevista via interpolação
        output_file='output/analise_perfil.md',
        async_execution=True
    )

    recomendacao_conteudos = Task(
        config=tasks_config['recomendacao_conteudos'],
        agent=analista_conteudo_educacional,
        context=[ler_planilha],
        output_file='output/recomendacoes.md',
        async_execution=True
    )

    planejamento_estruturado_de_desenvolvimento_individual = Task(
        config=tasks_config['planejamento_estruturado_de_desenvolvimento_individual'],
        agent=pdi_specialist,
        context=[analise_subjetiva_colaborador, recomendacao_conteudos],
        output_file='output/pdi.md',
    )

    generate_final_summary = Task(
        config=tasks_config['generate_final_summary'],
        agent=final_writer,
        context=[
            analise_subjetiva_colaborador,
            recomendacao_conteudos,
            planejamento_estruturado_de_desenvolvimento_individual
        ],
        output_file='output/final_summary.md',
    )

    # Creating Crew
    crew = Crew(
        agents=[
            leitor_de_planilha,
            analista_de_perfis,
            analista_conteudo_educacional,
            pdi_specialist,
            final_writer
        ],
        tasks=[
            ler_planilha,
            analise_subjetiva_colaborador,
            recomendacao_conteudos,
            planejamento_estruturado_de_desenvolvimento_individual,
            generate_final_summary
        ],
        process=Process.sequential,
        verbose=True
    )

    return crew

async def main():
    # Load configurations
    config_dir = pathlib.Path(__file__).parent / 'config'
    agents_config, tasks_config = load_config(config_dir / 'agents.yaml', config_dir / 'tasks.yaml')

    # Inicializa e executa a entrevista
    interview_manager = InterviewManager()
    interview_data = await interview_manager.conduct_interview()

    if interview_data:
        # Create and run crew with interview data
        crew = await create_crew(agents_config, tasks_config, interview_data, openai_api_key=os.environ.get("OPENAI_API_KEY"))
        result = crew.kickoff()

        print("\nCrew execution completed!")
        print("Results:", result)

        # Calculate and display costs
        costs = 0.150 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
        print(f"\nTotal costs: ${costs:.4f}")
        
        return result

if __name__ == "__main__":
    asyncio.run(main())
