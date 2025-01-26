from openai import OpenAI
import os
from pathlib import Path

class PDIAssistant:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.thread = None
        
    def initialize_assistant(self):
        """Inicializa o assistente com instruções básicas"""
        self.assistant = self.client.beta.assistants.create(
            name="PDI Consultant",
            instructions="""Você é um consultor profissional especializado em analisar e explicar Planos de Desenvolvimento Individual (PDIs).
            Use o contexto fornecido para responder perguntas sobre o perfil do colaborador, plano de desenvolvimento e descobertas da pesquisa.
            Sempre baseie suas respostas nas informações presentes nos documentos fornecidos.""",
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
                    "content": "Aqui está o contexto dos documentos PDI:\n\n" + "\n".join(context)
                }]
            )
        else:
            raise ValueError("Nenhum documento PDI encontrado no diretório especificado")
                
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
