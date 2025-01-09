# SQLite3 version fix for Streamlit Cloud
import sqlite3
import sys
from pathlib import Path

if sqlite3.sqlite_version_info < (3, 35, 0):
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import streamlit.components.v1 as components
import os
import pathlib
from main import create_crew, load_config
import asyncio
from langchain_openai import ChatOpenAI 

# Set up page config
st.set_page_config(
    page_title="PDI Crew",
    page_icon="👥",
    layout="centered"
)

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()
AGENTS_CONFIG = str(BASE_DIR / 'config' / 'agents.yaml')
TASKS_CONFIG = str(BASE_DIR / 'config' / 'tasks.yaml')
OUTPUT_DIR = str(BASE_DIR / 'output')

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False
if 'interview_data' not in st.session_state:
    st.session_state.interview_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = None

def show_sidebar(generated_files):
    """Mostra a sidebar com navegação de documentos"""
    st.sidebar.subheader("📚 Documentos Gerados")
    
    # Mapeamento de nomes de arquivos para títulos amigáveis
    file_titles = {
        'analise_perfil.md': 'Análise do Perfil',
        'pdi.md': 'Plano de Desenvolvimento Individual',
        'final_summary.md': 'Sumário Executivo',
        'recomendacoes.md': 'Recomendações Educacionais',
        'technical_skills.md': 'Pesquisa de Habilidades Técnicas',
        'behavioral_skills.md': 'Pesquisa de Habilidades Comportamentais',
        'industry_trends.md': 'Pesquisa de Tendências da Indústria',
        'aggregated_research.md': 'Consolidação das Pesquisas'
    }
    
    # Criar lista de documentos disponíveis
    available_docs = []
    for file in generated_files:
        if file.exists():
            try:
                file_name = file.name
                if file_name in file_titles:
                    available_docs.append((file_titles[file_name], file))
            except Exception as e:
                st.error(f"Erro ao processar arquivo {file.name}: {str(e)}")
    
    if available_docs:
        # Criar opções para o dropdown
        doc_options = [title for title, _ in available_docs]
        selected_doc = st.sidebar.selectbox(
            "Escolha um documento para visualizar:",
            doc_options,
            key="doc_selector"
        )
        
        # Encontrar o arquivo correspondente
        selected_file = next(file for title, file in available_docs if title == selected_doc)
        
        # Atualizar o estado da sessão
        st.session_state.current_file = str(selected_file)
    
    # Adicionar botão de nova entrevista na sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Nova Entrevista", use_container_width=True):
        st.session_state.messages = []
        st.session_state.interview_complete = False
        st.session_state.interview_data = None
        st.rerun()

def show_file_content():
    """Mostra o conteúdo do arquivo atual"""
    try:
        # Mapeamento de nomes de arquivos para títulos
        file_titles = {
            'analise_perfil.md': 'Análise do Perfil',
            'pdi.md': 'Plano de Desenvolvimento Individual',
            'final_summary.md': 'Sumário Executivo',
            'recomendacoes.md': 'Recomendações Educacionais',
            'technical_skills.md': 'Pesquisa de Habilidades Técnicas',
            'behavioral_skills.md': 'Pesquisa de Habilidades Comportamentais',
            'industry_trends.md': 'Pesquisa de Tendências da Indústria',
            'aggregated_research.md': 'Consolidação das Pesquisas'
        }
        
        # Obter o nome do arquivo atual
        current_file = Path(st.session_state.current_file).name
        
        # Mostrar o título do documento
        if current_file in file_titles:
            st.title(f"📄 {file_titles[current_file]}")
        
        # Mostrar o conteúdo
        with open(st.session_state.current_file, 'r', encoding='utf-8') as f:
            content = f.read()
            st.markdown(content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")

def verify_api_key(api_key):
    """Verifica se a chave da API OpenAI é válida"""
    try:
        client = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini"
        )
        # Faz uma chamada simples para testar a API
        response = client.invoke("Olá")
        return True
    except Exception as e:
        st.error(f"Chave da API inválida!")
        return False

def initialize_llm():
    return ChatOpenAI(
        model="gpt-4o-2024-08-06"
    )

def initialize_session_state():
    if 'llm' not in st.session_state:
        st.session_state.llm = initialize_llm()
        st.session_state.llm_messages = []
        system_prompt = """
        Você é um consultor profissional especializado em desenvolvimento de carreira e aprendizagem.
        Seu objetivo é conduzir uma entrevista natural e empática para coletar informações sobre um colaborador.
        Na condução de sua entrevista você deverá fazer perguntas curtas e claras até que tenha coletado 
        informações detalhadas sobre:

        1. Perfil Profissional:
        - Área de atuação atual e tempo de experiência
        - Principais responsabilidades e atividades diárias
        - Nível de senioridade e escopo de atuação

        2. Performance e Resultados:
        - Métricas quantitativas de performance (KPIs, metas atingidas, etc.)
        - Projetos relevantes concluídos ou em andamento
        - Impacto do seu trabalho na organização

        3. Desenvolvimento Profissional:
        - Desafios técnicos e não-técnicos enfrentados no dia a dia
        - Pontos fortes e competências já bem desenvolvidas
        - Áreas que gostaria de melhorar ou desenvolver
        - Preferências de formato de aprendizagem (cursos, leitura, vídeos, etc.)
        - Disponibilidade de tempo para estudos

        4. Aspirações e Objetivos:
        - Objetivos profissionais de curto prazo (6-12 meses)
        - Objetivos de carreira de longo prazo
        - Áreas de interesse para especialização
        - Habilidades que gostaria de adquirir ou aprimorar

        Conduza a entrevista de forma conversacional, fazendo perguntas de follow-up quando necessário 
        para obter informações mais específicas e detalhadas. NUNCA faça perguntas muito longas. 
        Tente, quando possível, fazer algum comentário curto e empático sobre a última resposta do entrevistado antes de fazer a pergunta seguinte 
        de modo a garantir uma conversa fluida e natural.

        IMPORTANTE:

        Quando você tiver coletado todas as informações necessárias, responda com o prefixo 
        [INTERVIEW_COMPLETE] seguido por um resumo estruturado das informações coletadas.

        Se o usuário responder [finalize] você deverá inventar a entrevista e responde com o prefixo [INTERVIEW_COMPLETE] 

        O resumo deve ser em formato de texto, organizado pelos tópicos acima, incluindo citações 
        relevantes das respostas do entrevistado e destacando pontos importantes para a 
        criação de um plano de desenvolvimento personalizado.
        """
        # Initialize messages with system prompt
        st.session_state.llm_messages = [{"role": "system", "content": system_prompt}]
        # Add initial message for display
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu consultor de desenvolvimento profissional. Vou fazer algumas perguntas para entender melhor seu perfil e objetivos. Poderia me contar um pouco sobre sua função atual e responsabilidades?"}]

def show_interview_interface():
    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if prompt := st.chat_input():
        # Add user message to chat history and LLM messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.llm_messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Get response from LLM
        response = asyncio.run(st.session_state.llm.ainvoke(st.session_state.llm_messages))
        response_content = response.content
        
        # Check if interview is complete
        if "[INTERVIEW_COMPLETE]" in response_content:
            # Extrai apenas a última mensagem do assistente, sem o marcador e o resumo
            last_message = response_content.split("[INTERVIEW_COMPLETE]")[0].strip()
            
            # Armazena os dados da entrevista e marca como completa
            st.session_state.interview_complete = True
            st.session_state.interview_data = response_content.split("[INTERVIEW_COMPLETE]")[1].strip()
            
            # Mostra apenas uma mensagem de conclusão
            st.chat_message("assistant").write("Obrigado pelas informações! Vou gerar sua análise de desenvolvimento profissional.")
            
            # Carrega configurações e executa a crew em segundo plano
            with st.spinner("Aguarde, estamos realizando o seu plano de desenvolvimento..."):
                agents_config, tasks_config = load_config(AGENTS_CONFIG, TASKS_CONFIG)
                crew = asyncio.run(create_crew(agents_config, tasks_config, st.session_state.interview_data, openai_api_key=st.session_state.openai_api_key))
                result = crew.kickoff()
            
            # Redireciona para a página principal
            st.session_state.current_page = 'main'
            st.rerun()
        else:
            # Adiciona resposta normal do assistente
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            st.chat_message("assistant").write(response_content)

def show_main_page():
    """Página principal do aplicativo"""
    st.title("🎯 PDI Crew - Plano de Desenvolvimento Individual")
    st.divider()
    
    # API Key input if not already set
    if not st.session_state.openai_api_key:
        api_key = st.text_input("🔑 OpenAI API Key", type="password")
        if api_key:
            # Verifica se a chave é válida antes de prosseguir
            if verify_api_key(api_key):
                st.session_state.openai_api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
                st.success("✅ API Key válida!")
                st.rerun()
        st.stop()

    if st.session_state.interview_complete:
        output_dir = BASE_DIR / 'output'
        generated_files = [
            output_dir / 'final_summary.md',  # Sumário Executivo
            output_dir / 'pdi.md',  # Plano de Desenvolvimento Individual
            output_dir / 'analise_perfil.md',  # Análise do Perfil
            output_dir / 'recomendacoes.md',  # Recomendações Educacionais
            output_dir / 'technical_skills.md',  # Pesquisa de Habilidades Técnicas
            output_dir / 'behavioral_skills.md',  # Pesquisa de Habilidades Comportamentais
            output_dir / 'industry_trends.md',  # Pesquisa de Tendências da Indústria
            output_dir / 'aggregated_research.md'  # Consolidação das Pesquisas
        ]
        
        # Mostrar a sidebar
        show_sidebar(generated_files)
        
        # Se é a primeira vez após completar a entrevista, mostrar o sumário executivo
        if 'current_file' not in st.session_state:
            st.session_state.current_file = str(output_dir / 'final_summary.md')
        
        # Mostrar o conteúdo do arquivo atual
        show_file_content()
    else:
        # Initialize LLM and messages if not exists
        initialize_session_state()
        
        # Show interview interface
        show_interview_interface()

def main():
    show_main_page()

if __name__ == "__main__":
    main()
