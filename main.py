#!/usr/bin/env python3

# Warning control
import warnings
warnings.filterwarnings('ignore')

import os
import pathlib
import asyncio
from dotenv import load_dotenv
from interview_assistant import InterviewAssistant
from utils import load_config, create_crew

# Set up base directory and file paths
BASE_DIR = pathlib.Path(__file__).parent.absolute()

async def main():
    """Função principal para execução via linha de comando"""
    # Load configurations
    load_dotenv()
    os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
    os.environ["EXA_API_KEY"] = os.getenv("EXA_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    # Inicializa e executa a entrevista
    interview_assistant = InterviewAssistant(openai_api_key)
    interview_assistant.initialize_assistant()
    
    print("\nIniciando entrevista...\n")
    
    while True:
        user_input = input("\nVocê: ")
        response = await interview_assistant.get_response(user_input)
        print(f"\nAssistente: {response}")
        
        if "[INTERVIEW_COMPLETE]" in response:
            interview_data = response.split("[INTERVIEW_COMPLETE]")[1].strip()
            print("\nEntrevista concluída! Gerando plano de desenvolvimento...\n")
            
            # Carrega configurações e executa a crew
            agents_config, tasks_config = load_config(
                BASE_DIR / 'config' / 'agents.yaml',
                BASE_DIR / 'config' / 'tasks.yaml'
            )
            crew = await create_crew(agents_config, tasks_config, interview_data, openai_api_key)
            result = crew.kickoff()
            
            print("\nCrew execution completed!")
            print("Results:", result)
            break
    
    print("\nProcesso finalizado com sucesso!\n")

if __name__ == "__main__":
    asyncio.run(main())
