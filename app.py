import streamlit as st
import os
from main import create_crew, load_config
import tempfile
import glob
import pathlib
import json
import plotly.graph_objects as go
from tools import PokerAnalysisTool

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()
AGENTS_CONFIG = str(BASE_DIR / 'config' / 'agents.yaml')
TASKS_CONFIG = str(BASE_DIR / 'config' / 'tasks.yaml')

# Development mode flag
DEV_MODE = False  

st.set_page_config(
    page_title="Poker Analysis",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 Poker Performance Analysis")

# Add a dev mode indicator
if DEV_MODE:
    st.info("🛠️ Development Mode: Using existing files from output directory")

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
    
    # File downloads
    generated_files = list(output_dir.glob('*.md'))
    if generated_files:
        st.subheader("Poker Analysis Results")
        
        cols = st.columns(2)
        for idx, file in enumerate(generated_files):
            try:
                with open(file, "rb") as f:
                    file_content = f.read()
                    cols[idx % 2].download_button(
                        label=f"📥 {file.name}",
                        data=file_content,
                        file_name=file.name,
                        mime="text/markdown"
                    )
            except Exception as e:
                st.error(f"Error processing file {file.name}: {str(e)}")

# File upload section
uploaded_file = st.file_uploader(" Upload your poker session CSV file", type=['csv'])

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_dir = BASE_DIR / 'data'
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / uploaded_file.name
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File uploaded successfully: {uploaded_file.name}")
    
    # Initialize tool with uploaded file
    poker_analysis_tool = PokerAnalysisTool(str(temp_path))
    
    if st.button("Run Analysis", type="primary"):
        with st.spinner("Running poker analysis... This might take a few minutes."):
            try:
                # Load configurations and create crew
                agents_config = load_config(AGENTS_CONFIG)
                tasks_config = load_config(TASKS_CONFIG)
                crew = create_crew(agents_config, tasks_config)
                crew.kickoff()
                process_analysis_files()
                    
            except Exception as e:
                st.error(f"An error occurred during the analysis: {str(e)}")
                
            finally:
                # Clean up temporary file
                if temp_path.exists():
                    os.remove(temp_path)
else:
    if DEV_MODE:
        process_analysis_files()
    st.info(" Please upload your poker session CSV file to begin the analysis")
