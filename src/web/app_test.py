import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json
import asyncio
from src.assistants.linkedin_assistant import LinkedInAssistant

# Set up page config
st.set_page_config(
    page_title="PDI Crew - Test Mode",
    page_icon="🧪",
    layout="centered"
)

# Set up base directory and file paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
FRONTEND_DIR = BASE_DIR / "frontend"

# Mapeamento de títulos para arquivos
FILE_TITLES = {
    "📋 PDI Completo": "pdi.md",
    "👤 Análise de Perfil": "analise_perfil.md",
    "📚 Recomendações": "recomendacoes.md",
    "📊 Pesquisa Agregada": "aggregated_research.md",
    "💡 Competências Técnicas": "technical_skills.md",
    "🤝 Competências Comportamentais": "behavioral_skills.md",
    "🌟 Tendências da Indústria": "industry_trends.md",
    "📝 Resumo Final": "final_summary.md"
}

def show_sidebar():
    """Mostra a sidebar com os arquivos gerados"""
    st.sidebar.title("📑 Documentos")
    
    # Botão para visualização do PDI
    if st.sidebar.button("📊 Visualização do PDI"):
        st.session_state.current_page = 'pdi_tracker'
        st.rerun()
        
    # Botão para LinkedIn Post Creator
    if st.sidebar.button("📱 LinkedIn Post"):
        st.session_state.current_page = 'linkedin'
        st.rerun()
    
    st.sidebar.divider()
    
    # Lista de documentos
    for title, filename in FILE_TITLES.items():
        if st.sidebar.button(title):
            st.session_state.current_file = str(OUTPUT_DIR / filename)
            st.session_state.current_page = 'document'
            st.rerun()

def show_file_content():
    """Mostra o conteúdo do arquivo atual"""
    if not st.session_state.current_file:
        return
        
    file_path = Path(st.session_state.current_file)
    if not file_path.exists():
        st.error(f"Arquivo não encontrado: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    st.markdown(content)

def show_pdi_tracker():
    """Mostra a interface de visualização do PDI"""
    st.title("📊 Visualização do PDI")
    
    # Verifica se o arquivo JSON existe
    pdi_json_path = OUTPUT_DIR / 'pdi.json'
    if not pdi_json_path.exists():
        st.info("Arquivo pdi.json não encontrado na pasta output.")
        return
        
    try:
        # Lê o arquivo JSON
        with open(pdi_json_path, 'r', encoding='utf-8') as f:
            pdi_data = f.read()
        
        # Caminho para o componente React compilado
        component_path = FRONTEND_DIR / "dist" / "pdi-tracker.js"
        if not component_path.exists():
            st.error("Componente de visualização não encontrado. Execute 'npm run build' no diretório frontend.")
            return
            
        # Lê o conteúdo do arquivo JS
        with open(component_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            
        # Renderiza o componente React
        components.html(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>PDI Tracker</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 16px;
                        font-family: system-ui, -apple-system, sans-serif;
                    }}
                </style>
            </head>
            <body>
                <div id="pdi-tracker-root"></div>
                <script>{js_content}</script>
                <script>
                    const pdiConfig = {pdi_data};
                    window.renderPDITracker(
                        document.getElementById('pdi-tracker-root'),
                        pdiConfig,
                        600
                    );
                </script>
            </body>
            </html>
            """,
            height=600,
            scrolling=True
        )
            
    except Exception as e:
        st.error(f"Erro ao carregar a visualização do PDI: {str(e)}")

def show_linkedin_interface():
    """Interface do chat para criação de posts do LinkedIn"""
    if st.session_state.linkedin_assistant is None:
        st.session_state.linkedin_assistant = LinkedInAssistant("test-key")  # Usando uma chave de teste
        st.session_state.linkedin_assistant.initialize_assistant()
        try:
            st.session_state.linkedin_assistant.upload_pdi_documents(OUTPUT_DIR)
        except ValueError as e:
            st.error(str(e))
            return
    
    st.title("📱 LinkedIn Post Creator")
    st.markdown("Este assistente irá criar um post do LinkedIn celebrando o início do seu PDI. O post será criado automaticamente e você pode pedir ajustes conforme necessário.")
    
    # Display chat messages
    for message in st.session_state.linkedin_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Digite sua mensagem"):
        st.session_state.linkedin_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = asyncio.run(st.session_state.linkedin_assistant.get_response(prompt))
            st.session_state.linkedin_messages.append({"role": "assistant", "content": response})
            st.write(response)

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'document'
    if 'current_file' not in st.session_state:
        st.session_state.current_file = str(OUTPUT_DIR / 'pdi.md')
    if 'linkedin_assistant' not in st.session_state:
        st.session_state.linkedin_assistant = None
    if 'linkedin_messages' not in st.session_state:
        st.session_state.linkedin_messages = []
    
    # Show sidebar
    show_sidebar()
    
    # Show appropriate page
    if st.session_state.current_page == 'pdi_tracker':
        show_pdi_tracker()
    elif st.session_state.current_page == 'linkedin':
        show_linkedin_interface()
    else:
        show_file_content()

if __name__ == "__main__":
    main()
