import streamlit as st
import streamlit.components.v1 as components
import os
from main import create_crew, load_config
import tempfile
import glob
import pathlib
import json
import plotly.graph_objects as go
from tools import PokerAnalysisTool

# Set up page config
st.set_page_config(
    page_title="Poker Analysis",
    page_icon="🎲",
    layout="centered"
)

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()
AGENTS_CONFIG = str(BASE_DIR / 'config' / 'agents.yaml')
TASKS_CONFIG = str(BASE_DIR / 'config' / 'tasks.yaml')

# Development mode flag
DEV_MODE = False

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'last_api_key' not in st.session_state:
    st.session_state.last_api_key = ""
if 'analysis_costs' not in st.session_state:
    st.session_state.analysis_costs = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = True

def ensure_top_position():
    if st.session_state.scroll_to_top:
        js = '''
            <script>
                window.scrollTo(0, 0);
                var body = window.document.querySelector("body");
                body.scrollTop = 0;
                window.parent.document.querySelector('iframe').contentWindow.scrollTo(0, 0);
            </script>
        '''
        st.components.v1.html(js, height=0)
        st.session_state.scroll_to_top = False

def show_file_content(file_path):
    st.session_state.scroll_to_top = True
    ensure_top_position()
    
    file_name = os.path.basename(file_path)
    if file_name == 'performance_report.md':
        title = 'Relatório de Performance'
    elif file_name == 'educational_content.md':
        title = 'Plano de Estudos'
    elif file_name == 'final_summary.md':
        title = 'Sumário Executivo'
    elif file_name == 'matrics_summary.md':
        title = 'Métricas de Desempenho'
    else:
        title = file_name
    st.title(f"📄 {title}")
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            st.markdown(content)
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
    
    if st.button("← Back to Analysis"):
        st.session_state.current_page = 'main'
        st.session_state.scroll_to_top = True
        st.rerun()

def show_main_page():
    st.session_state.scroll_to_top = True
    ensure_top_position()
    
    st.title("🎲 Poker Performance Analysis")
    
    # Add a dev mode indicator
    if DEV_MODE:
        st.info("🛠️ Development Mode: Using existing files from output directory")
    
    if st.session_state.analysis_complete:
        process_analysis_files()
    else:
        first_analysis()


 

def process_analysis_files():
    output_dir = BASE_DIR / 'output'
    
    # Process metrics summary first
    metrics_path = output_dir / 'metrics_summary.md'
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics_content = f.read()
            try:
                metrics_data = json.loads(metrics_content)
                
                # Display basic metrics
                st.subheader("📊 Performance Metrics")
                basic = metrics_data['basic_metrics']
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Hands", f"{basic['total_hands']:,}")
                with col2:
                    st.metric("VPIP", f"{basic['vpip']}%")
                with col3:
                    st.metric("PFR", f"{basic['pfr']}%")
                with col4:
                    st.metric("BB/100", f"{basic['bb_100']:.2f}")
                
                # Position Performance
                st.subheader("📍 Position Performance")
                position_data = metrics_data['position_metrics']
                positions = list(position_data.keys())
                bb_100_values = [position_data[pos]['bb_100'] for pos in positions]
                
                fig = go.Figure(data=[
                    go.Bar(name='BB/100', y=positions, x=bb_100_values, orientation='h')
                ])
                fig.update_layout(height=300, margin=dict(t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
            except json.JSONDecodeError:
                st.error("Error parsing metrics data")
    
    # Process final summary
    final_summary_path = output_dir / 'final_summary.md'
    if final_summary_path.exists():
        with open(final_summary_path, 'r') as f:
            summary_content = f.read()
            st.markdown(summary_content)
    
    # Get all generated markdown files
    generated_files = list(output_dir.glob("*.md"))
    
    if generated_files:
        st.subheader("Poker Analysis Results")
        
        cols = st.columns(2)
        for idx, file in enumerate(generated_files):
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
    
    # Add New Analysis button at the end
    st.button("🔄 New Analysis", on_click=reset_analysis)
    
    # Display costs if available
    if 'analysis_costs' in st.session_state and st.session_state.analysis_costs is not None:
        st.caption(f"💰 Analysis cost: ${st.session_state.analysis_costs:.4f}")

def first_analysis():
    # API Key input
    api_key = st.text_input("🔑 Enter your Anthropic API Key", 
                           value=st.session_state.last_api_key,
                           type="password", 
                           help="Your API key will not be stored and will only be used for this analysis session")

    # File upload section
    uploaded_file = st.file_uploader("📤 Upload your poker session CSV file", type=['csv'])

    if uploaded_file is not None and api_key:
        # Save uploaded file temporarily
        temp_dir = BASE_DIR / 'data'
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        
        
        if st.button("Run Analysis", type="primary"):
            with st.spinner("Running poker analysis... This might take a few minutes."):
                try:
                    # Set the API key for this session
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    st.session_state.last_api_key = api_key
                    
                    # Load configurations and create crew
                    agents_config = load_config(AGENTS_CONFIG)
                    tasks_config = load_config(TASKS_CONFIG)
                    crew = create_crew(agents_config, tasks_config, str(temp_path))
                    crew.kickoff()
                    
                    # Calculate and store costs in session state
                    costs = 0.150 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
                    st.session_state.analysis_costs = costs
                    
                    st.session_state.analysis_complete = True
                    process_analysis_files()
                        
                except Exception as e:
                    st.error(f"An error occurred during the analysis: {str(e)}")
                    
                finally:
                    # Clean up
                    if temp_path.exists():
                        os.remove(temp_path)
                    # Clear API key from environment
                    os.environ.pop("ANTHROPIC_API_KEY", None)
    elif not api_key:
        st.warning("👆 Please enter your Anthropic API Key to proceed")
    elif not uploaded_file:
        st.info("👆 Please upload your poker session CSV file to begin the analysis")
    else:
        process_analysis_files()
        if st.button("🔄 New Analysis"):
            reset_analysis()

def reset_analysis():
    st.session_state.analysis_complete = False
    st.session_state.uploaded_file = None
    st.session_state.analysis_costs = None
    st.rerun()

def main():
    if st.session_state.current_page == 'main':
        show_main_page()
    elif st.session_state.current_page == 'file_content':
        show_file_content(st.session_state.current_file)

if __name__ == "__main__":
    main()

if DEV_MODE:
    main()
