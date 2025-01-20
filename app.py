# SQLite3 version fix for Streamlit Cloud
import sqlite3
import sys
from pathlib import Path
import pathlib

if sqlite3.sqlite_version_info < (3, 35, 0):
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import streamlit.components.v1 as components
import os
import asyncio
from pdi_assistant import PDIAssistant
from interview_assistant import InterviewAssistant
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
if 'pdi_assistant' not in st.session_state:
    st.session_state.pdi_assistant = None
if 'interview_assistant' not in st.session_state:
    st.session_state.interview_assistant = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Mapeamento de nomes de arquivos para títulos em português
FILE_TITLES = {
    'final_summary.md': 'Resumo Executivo',
    'pdi.md': 'Plano de Desenvolvimento',
    'analise_perfil.md': 'Análise do Perfil',
    'recomendacoes.md': 'Recomendações de Estudo',
    'technical_skills.md': 'Competências Técnicas',
    'behavioral_skills.md': 'Competências Comportamentais',
    'industry_trends.md': 'Tendências do Mercado',
    'aggregated_research.md': 'Pesquisa Consolidada'
}

def show_sidebar(generated_files):
    """Mostra a sidebar com os arquivos gerados"""
    with st.sidebar:
        st.title("🗂️ Navegação")
        
        # Botão para voltar ao guia
        if st.button("📚 Guia do PDI"):
            st.session_state.current_page = 'main'
            st.session_state.current_file = str(BASE_DIR / 'docs' / 'pdi_guide.md')
            st.rerun()
        
        # Botão para chat
        if st.button("💬 Consultor PDI Bot"):
            st.session_state.current_page = 'chat'
            st.rerun()
        
        st.divider()
        
        # Lista de documentos
        st.subheader("📑 Documentos Gerados")
        for file in generated_files:
            if file.exists():
                # Obtém o nome do arquivo e seu título correspondente
                file_name = file.name
                display_name = FILE_TITLES.get(file_name, file_name)
                
                if st.button(f"📄 {display_name}"):
                    st.session_state.current_file = str(file)
                    st.session_state.current_page = 'main'
                    st.rerun()

def show_file_content():
    """Mostra o conteúdo do arquivo atual"""
    try:
        if 'current_file' not in st.session_state or st.session_state.current_file is None:
            st.session_state.current_file = str(BASE_DIR / 'docs' / 'pdi_guide.md')
            
        file_path = st.session_state.current_file
        if not os.path.exists(file_path):
            st.error(f"Arquivo não encontrado: {file_path}")
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            st.markdown(content)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")
        st.session_state.current_file = str(BASE_DIR / 'docs' / 'pdi_guide.md')
        st.rerun()

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
    """Inicializa o estado da sessão para a entrevista"""
    if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
        st.session_state.interview_assistant = InterviewAssistant(st.session_state.openai_api_key)
        st.session_state.interview_assistant.initialize_assistant()
        st.session_state.messages = st.session_state.interview_assistant.messages

def show_generic_chat_interface(title, description, assistant, messages_key="chat_messages"):
    """Interface genérica de chat que pode ser usada com diferentes assistentes"""
    # Verifica se o assistente está inicializado
    if assistant is None:
        st.error("Erro: Assistente não inicializado corretamente")
        return
        
    st.title(title)
    st.markdown(description)
    
    # Inicializa mensagens se necessário
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
    
    # Display chat messages
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Digite sua mensagem"):
        # Add user message to chat history
        st.session_state[messages_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            # Verifica se não está em processo de criação do PDI
            if not (hasattr(assistant, 'process_interview_completion') and "[INTERVIEW_COMPLETE]" in prompt):
                with st.spinner("Pensando..."):
                    response = asyncio.run(assistant.get_response(prompt))
            else:
                response = asyncio.run(assistant.get_response(prompt))
            
            # Verifica se é uma resposta de conclusão de entrevista
            if hasattr(assistant, 'process_interview_completion'):
                if assistant.process_interview_completion(response, st.session_state):
                    st.rerun()
            
            st.session_state[messages_key].append({"role": "assistant", "content": response})
            st.write(response)

def show_interview_interface():
    """Interface do chat para entrevista"""
    show_generic_chat_interface(
        title="🎤 Entrevista PDI",
        description="""
        A seguir vamos começar uma entrevista para conhecer melhor o seu perfil.
        Por favor, responda as perguntas do nosso assistente para que possamos construir um PDI personalizado para você.
        """,
        assistant=st.session_state.interview_assistant,
        messages_key="messages"
    )

def show_chat_interface():
    """Interface do chat para consulta do PDI"""
    show_generic_chat_interface(
        title="💬 Consultor PDI Bot",
        description="""
        Olá! Sou seu consultor especializado no Plano de Desenvolvimento Individual.
        Posso responder perguntas sobre o perfil do colaborador, recomendações e plano de desenvolvimento.
        Como posso ajudar?
        """,
        assistant=st.session_state.pdi_assistant,
        messages_key="chat_messages"
    )

def show_main_page():
    """Página principal do aplicativo"""
    st.title("✨ Templo PDI Bot")
    st.divider()
    
    # API Key input if not already set
    if not st.session_state.openai_api_key:
        api_key = st.text_input("🔑 OpenAI API Key", type="password")
        if api_key:
            # Verifica se a chave é válida antes de prosseguir
            if verify_api_key(api_key):
                st.session_state.openai_api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
                initialize_session_state()
                st.success("✅ API Key válida!")
                st.rerun()
        st.stop()
    
    # Garante que o assistente está inicializado
    if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
        initialize_session_state()
        st.rerun()
    
    if st.session_state.interview_complete:
        output_dir = BASE_DIR / 'output'
        generated_files = [output_dir / filename for filename in FILE_TITLES.keys()]
        
        # Mostrar a sidebar
        show_sidebar(generated_files)
        
        # Inicializa o PDI Assistant se necessário
        if st.session_state.current_page == 'chat' and (
            'pdi_assistant' not in st.session_state or 
            st.session_state.pdi_assistant is None
        ):
            st.session_state.pdi_assistant = PDIAssistant(st.session_state.openai_api_key)
            st.session_state.pdi_assistant.initialize_assistant()
            st.session_state.pdi_assistant.upload_pdi_documents(output_dir)
            st.session_state.pdi_assistant.create_thread()
        
        # Mostrar a interface apropriada
        if st.session_state.current_page == 'chat':
            show_chat_interface()
        else:
            # Se é a primeira vez após completar a entrevista, mostrar o guia
            if 'current_file' not in st.session_state:
                st.session_state.current_file = str(BASE_DIR / 'docs' / 'pdi_guide.md')
            
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