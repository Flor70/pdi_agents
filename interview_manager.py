from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
import json
import asyncio
import os

class InterviewManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4o-2024-08-06",
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        self.interview_complete = False
        self.collected_data = None
    
    async def conduct_interview(self):
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
        
        messages = [{"role": "system", "content": system_prompt}]
        
        while not self.interview_complete:
            # Recebe input do usuário
            user_input = input("\nVocê: ")
            messages.append({"role": "user", "content": user_input})
            
            # Obtém resposta do LLM
            response = await self.llm.ainvoke(messages)
            messages.append({"role": "assistant", "content": response.content})
            
            # Verifica se a entrevista está completa
            if "[INTERVIEW_COMPLETE]" in response.content:
                self.interview_complete = True
                # Extrai o resumo da entrevista
                summary = response.content.split("[INTERVIEW_COMPLETE]")[1].strip()
                self.collected_data = summary
                
                # Retorna apenas a parte da mensagem sem o resumo
                clean_response = response.content.split("[INTERVIEW_COMPLETE]")[0]
                print("\nConsultor:", clean_response)
                return self.collected_data
            
            print("\nConsultor:", response.content)
        
        return None
