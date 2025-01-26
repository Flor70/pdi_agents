from openai import OpenAI
from src.core.utils import load_config, create_crew
from pathlib import Path
import asyncio
import streamlit as st

class InterviewAssistant:
    def __init__(self, openai_api_key):
        """
        Inicializa o assistente de entrevista.
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.thread = None
        self.messages = []
        
    def initialize_assistant(self):
        """Inicializa o assistente com instruções para conduzir a entrevista"""
        self.assistant = self.client.beta.assistants.create(
            name="PDI Interviewer",
            instructions="""Você é um consultor profissional especializado em desenvolvimento de carreira e aprendizagem.
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

            Se o usuário responder [finalize] você deverá inventar a entrevista, incluindo nome e empresa do colaborador fictício, e responde com o prefixo [INTERVIEW_COMPLETE] 

            O resumo deve ser em formato de texto, organizado pelos tópicos acima, incluindo citações 
            relevantes das respostas do entrevistado e destacando pontos importantes para a 
            criação de um plano de desenvolvimento personalizado.""",
            model="gpt-4o"
        )
        
        # Criar thread inicial
        self.thread = self.client.beta.threads.create()
        
        # Mensagem inicial
        self.messages = [{
            "role": "assistant",
            "content": '''Sou um consultor de inteligencia artificial criado pelo templo para criar e acompanhar planos personalizados e detalhados para voce. Fui programado com conteúdos e metodologias de desenvolvimento gamificado e baseado em desafios para maximizar sua aprendizagem e ganho de habilidades.

Faremos uma entrevista com duração de alguns minutos e na sequência vou preparar uma análise além de recomendações e um calendário de desenvolvimento.

Primeiro, poderia me contar qual o seu nome e empresa que você trabalha?'''
        }]
        
    async def get_response(self, user_message):
        """Obtém resposta do assistente para a mensagem do usuário"""
        # Adiciona a mensagem do usuário ao thread
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message
        )
        
        # Cria um run
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        
        # Aguarda a conclusão do run
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run.status == 'completed':
                break
        
        # Obtém a resposta do assistente
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        
        # Retorna a última mensagem do assistente
        for msg in messages.data:
            if msg.role == "assistant":
                response = msg.content[0].text.value
                self.messages.append({"role": "assistant", "content": response})
                return response
                
        return "Não foi possível gerar uma resposta."

    def process_interview_completion(self, response, session_state):
        """Processa a conclusão da entrevista e inicia a crew"""
        if isinstance(response, str) and "[INTERVIEW_COMPLETE]" in response:
            session_state.interview_complete = True
            session_state.interview_data = response.split("[INTERVIEW_COMPLETE]")[1].strip()
            
            # Inicializa e executa a crew
            with st.spinner("🚀 Iniciando a criação do seu PDI personalizado... \n\n" + 
                          "Este processo envolve várias etapas de análise e pode levar alguns minutos. " +
                          "Estamos trabalhando para criar um plano detalhado e sob medida para você! 😊"):
                agents_config = str(Path(__file__).parent.parent.parent / 'config' / 'agents.yaml')
                tasks_config = str(Path(__file__).parent.parent.parent / 'config' / 'tasks.yaml')
                agents_config, tasks_config = load_config(agents_config, tasks_config)
                crew = asyncio.run(create_crew(agents_config, tasks_config, session_state.interview_data, openai_api_key=session_state.openai_api_key))
                result = crew.kickoff()
            
            session_state.current_page = 'main'
            session_state.current_file = str(Path(__file__).parent / 'docs' / 'pdi_guide.md')
            return True
            
        return False
