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

def show_file_content(file_path):
    file_name = os.path.basename(file_path)
    if file_name == 'performance_report.md':
        title = 'Relatório de Performance'
    elif file_name == 'pdi.md':
        title = 'Plano de Desenvolvimento Individual'
    elif file_name == 'final_summary.md':
        title = 'Sumário Executivo'
    elif file_name == 'plano_de_aprendizagem.md':
        title = 'Plano de Aprendizagem'
    else:
        title = file_name
    
    st.title(f"📄 {title}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Remove o cabeçalho YAML se existir
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2]
            
            # Renderiza o conteúdo como markdown
            st.markdown(content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")
        return None
    
    if st.button("← Voltar"):
        st.session_state.current_page = 'main'
        st.rerun()

def process_analysis_files():
    output_dir = BASE_DIR / 'output'
    
    # Process final summary
    final_summary_path = output_dir / 'final_summary.md'
    if final_summary_path.exists():
        try:
            with open(final_summary_path, 'r', encoding='utf-8') as f:
                summary_content = f.read()
                st.markdown(summary_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error reading final summary: {str(e)}")
    
    # Get all generated markdown files
    generated_files = [
        output_dir / 'pdi.md',
        output_dir / 'performance_report.md',
        output_dir / 'plano_de_aprendizagem.md'
    ]
    
    if any(f.exists() for f in generated_files):
        st.subheader("📚 Documentos Detalhados")
        
        cols = st.columns(2)
        for idx, file in enumerate(generated_files):
            if file.exists():
                try:
                    cols[idx % 2].button(
                        f"📄 {file.name}",
                        key=f"btn_{file.name}",
                        on_click=lambda f=file: (
                            setattr(st.session_state, 'current_page', 'file_content'),
                            setattr(st.session_state, 'current_file', str(f)),
                        )
                    )
                except Exception as e:
                    st.error(f"Error processing file {file.name}: {str(e)}")
    
    # Add New Interview button
    if st.button("🔄 Nova Entrevista"):
        st.session_state.messages = []
        st.session_state.interview_complete = False
        st.session_state.interview_data = None
        st.rerun()

def show_main_page():
    st.title("👥 PDI Crew - Análise de Desenvolvimento Profissional")
    
    # API Key input if not already set
    if 'openai_api_key' not in st.session_state:
        api_key = st.text_input("🔑 OpenAI API Key", type="password")
        if api_key:
            st.session_state.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
            st.rerun()
        st.stop()

    if st.session_state.interview_complete:
        process_analysis_files()
    else:
        # Initialize LLM and messages if not exists
        if 'llm' not in st.session_state:
            st.session_state.llm = ChatOpenAI(
                model="gpt-4o-2024-08-06"
            )
            system_prompt = """
            Você é um consultor profissional conduzindo uma entrevista.
            Seu objetivo é coletar naturalmente informações sobre:
            - Área de atuação e responsabilidades
            - Métricas quantitativas de performance
            - Desafios enfrentados
            - Pontos fortes
            - Objetivos profissionais

            Quando você tiver coletado todas as informações necessárias, responda com o prefixo 
            [INTERVIEW_COMPLETE] seguido por um resumo estruturado das informações coletadas.
            O resumo deve ser em formato de texto, organizado por tópicos, incluindo citações 
            relevantes das respostas do entrevistado.
            """
            # Initialize messages with system prompt
            st.session_state.llm_messages = [{"role": "system", "content": system_prompt}]
            # Add initial message for display
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Olá! Sou seu consultor de desenvolvimento profissional. Vou fazer algumas perguntas para entender melhor seu perfil e objetivos. Poderia me contar um pouco sobre sua função atual e responsabilidades?"
            })

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
                    crew = asyncio.run(create_crew(agents_config, tasks_config, st.session_state.interview_data))
                    result = crew.kickoff()
                
                # Redireciona para a página principal
                st.session_state.current_page = 'main'
                st.rerun()
            else:
                # Adiciona resposta normal do assistente
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                st.chat_message("assistant").write(response_content)

def main():
    if st.session_state.current_page == 'file_content' and st.session_state.current_file:
        show_file_content(st.session_state.current_file)
    else:
        show_main_page()

if __name__ == "__main__":
    main()
