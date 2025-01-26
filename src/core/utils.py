import yaml
import pathlib
import os
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from src.tools.educational_content_tool import ReadEducationalDBTool
from src.tools.serper_search_tool import SerperSearchTool
from src.tools.exa_search_tool import ExaSearchTool
from src.models.pdi_models import PDIConfig

def load_config(agents_file, tasks_file):
    """Carrega as configurações dos arquivos YAML"""
    with open(agents_file, 'r', encoding='utf-8') as f:
        agents_config = yaml.safe_load(f)
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_config = yaml.safe_load(f)
    
    return agents_config, tasks_config

def create_agents(agents_config):
    """Cria e retorna os agents individualmente configurados"""
    # Initialize tools
    educational_db_tool = ReadEducationalDBTool()
    serper_tool = SerperSearchTool()
    search_tool = ExaSearchTool()
    
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
        cache=True
    )

    final_writer = Agent(
        config=agents_config['final_writer'],
        verbose=True,
        tools=[],
        cache=True
    )

    professional_development_researcher = Agent(
        config=agents_config['professional_development_researcher'],
        verbose=True,
        tools=[search_tool],
        cache=True
    )

    content_organizer = Agent(
        config=agents_config['content_organizer'],
        verbose=True,
        tools=[],
        cache=True
    )
    
    return {
        'leitor_de_planilha': leitor_de_planilha,
        'analista_de_perfis': analista_de_perfis,
        'analista_conteudo_educacional': analista_conteudo_educacional,
        'pdi_specialist': pdi_specialist,
        'final_writer': final_writer,
        'professional_development_researcher': professional_development_researcher,
        'content_organizer': content_organizer
    }

def create_tasks(tasks_config, agents, interview_data=None):
    """Cria e retorna as tasks individualmente configuradas"""
    # Interpola os dados da entrevista nas descrições das tasks
    if interview_data:
        for task_name in ['analise_subjetiva_colaborador', 'recomendacao_conteudos',
                         'technical_skills_research', 'behavioral_skills_research',
                         'industry_trends_and_inspiration_research']:
            if task_name in tasks_config:
                tasks_config[task_name]['description'] = \
                    tasks_config[task_name]['description'].format(
                interview_data=interview_data
            )

    # Creating Tasks
    ler_planilha = Task(
        config=tasks_config['ler_planilha'],
        agent=agents['leitor_de_planilha']
    )

    analise_subjetiva_colaborador = Task(
        config=tasks_config['analise_subjetiva_colaborador'],
        agent=agents['analista_de_perfis'],
        context=[],  # Recebe apenas dados da entrevista via interpolação
        output_file='output/analise_perfil.md',
        async_execution=True
    )

    recomendacao_conteudos = Task(
        config=tasks_config['recomendacao_conteudos'],
        agent=agents['analista_conteudo_educacional'],
        context=[ler_planilha],
        output_file='output/recomendacoes.md',
        async_execution=True
    )

    technical_skills_research = Task(
        config=tasks_config['technical_skills_research'],
        agent=agents['professional_development_researcher'],
        output_file='output/technical_skills.md',
        async_execution=True
    )

    behavioral_skills_research = Task(
        config=tasks_config['behavioral_skills_research'],
        agent=agents['professional_development_researcher'],
        output_file='output/behavioral_skills.md',
        async_execution=True
    )

    industry_trends_research = Task(
        config=tasks_config['industry_trends_and_inspiration_research'],
        agent=agents['professional_development_researcher'],
        output_file='output/industry_trends.md',
        async_execution=True
    )

    aggregate_and_structure_research = Task(
        config=tasks_config['aggregate_and_structure_research'],
        agent=agents['content_organizer'],
        context=[
            technical_skills_research, 
            behavioral_skills_research, 
            industry_trends_research
        ],
        output_file='output/aggregated_research.md'
    )

    planejamento_estruturado_de_desenvolvimento_individual = Task(
        config=tasks_config['planejamento_estruturado_de_desenvolvimento_individual'],
        agent=agents['pdi_specialist'],
        context=[
            analise_subjetiva_colaborador,
            aggregate_and_structure_research
        ],
        output_file='output/pdi.md'
    )

    gerar_visualizacao = Task(
        description=tasks_config['gerar_visualizacao_pdi']['description'],
        expected_output=tasks_config['gerar_visualizacao_pdi']['expected_output'],
        agent=agents['pdi_specialist'],
        output_pydantic=PDIConfig,
        output_file='output/pdi.json',
        context=[
            planejamento_estruturado_de_desenvolvimento_individual
        ]
    )



    generate_final_summary = Task(
        config=tasks_config['generate_final_summary'],
        agent=agents['final_writer'],
        context=[
            analise_subjetiva_colaborador,
            recomendacao_conteudos,
            planejamento_estruturado_de_desenvolvimento_individual,
            aggregate_and_structure_research
        ],
        output_file='output/final_summary.md'
    )
    
    return [
        ler_planilha,
        analise_subjetiva_colaborador,
        recomendacao_conteudos,
        technical_skills_research,
        behavioral_skills_research,
        industry_trends_research,
        aggregate_and_structure_research,
        planejamento_estruturado_de_desenvolvimento_individual,
        gerar_visualizacao,
        generate_final_summary
    ]

async def create_crew(agents_config, tasks_config, interview_data=None, openai_api_key=None):
    """Cria e retorna a crew com agents e tasks configurados"""
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")
    
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Create agents and tasks
    agents = create_agents(agents_config)
    tasks = create_tasks(tasks_config, agents, interview_data)
    
    # Get list of agents
    agent_list = list(agents.values())
    
    # Create and return crew
    crew = Crew(
        agents=agent_list,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    return crew
