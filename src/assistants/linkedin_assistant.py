from openai import OpenAI
import os
from pathlib import Path

class LinkedInAssistant:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.thread = None
        
    def initialize_assistant(self):
        """Inicializa o assistente com instruções para criar posts do LinkedIn"""
        self.assistant = self.client.beta.assistants.create(
            name="LinkedIn Post Creator",
            instructions="""Você é um especialista em criar posts engajantes para o LinkedIn, focado em desenvolvimento profissional.
            
            Diretrizes para criação de posts:
            1. Tom profissional mas pessoal
            2. Celebre o início da jornada de desenvolvimento
            3. Destaque os principais objetivos do PDI
            4. Use emojis de forma moderada e profissional
            5. Inclua hashtags relevantes
            6. Mantenha o texto conciso (até 1300 caracteres)
            7. Termine com um call-to-action sutil
            
            Ao receber o contexto do PDI, crie imediatamente um post personalizado sem necessidade de solicitação adicional.
            Adapte o conteúdo baseado nas informações do colaborador e seus objetivos de desenvolvimento.""",
            model="gpt-4o"
        )
        
    def upload_pdi_documents(self, output_dir):
        """Lê o conteúdo dos documentos PDI e cria uma mensagem com o contexto"""
        files_to_read = [
            'aggregated_research.md',
            'analise_perfil.md',
            'pdi.md'
        ]
        
        context = []
        for filename in files_to_read:
            file_path = Path(output_dir) / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"Conteúdo de {filename}:\n\n{content}\n\n")
        
        if context:
            # Criar thread com o contexto
            self.thread = self.client.beta.threads.create(
                messages=[{
                    "role": "user",
                    "content": "Aqui está o contexto dos documentos PDI:\n\n" + "\n".join(context) + 
                    "\n\nPor favor, crie um post do LinkedIn celebrando o início desta jornada de desenvolvimento profissional. Você deve falar como o colaborador, em primeira pessoa."
                }]
            )
            
            # Gerar o post automaticamente
            return self.generate_initial_post()
        else:
            raise ValueError("Nenhum documento PDI encontrado no diretório especificado")
            
    def generate_initial_post(self):
        """Gera o post inicial do LinkedIn automaticamente"""
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
                return msg.content[0].text.value
                
        return "Não foi possível gerar o post do LinkedIn."
        
    def create_thread(self):
        """Cria um novo thread se ainda não existir"""
        if self.thread is None:
            self.thread = self.client.beta.threads.create()
        return self.thread
        
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
                return msg.content[0].text.value
                
        return "Não foi possível gerar uma resposta."
