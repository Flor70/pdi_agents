from openai import OpenAI
import os
from pathlib import Path

class MestreDosMagosAssistant:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.assistant = None
        self.thread = None
        
    def initialize_assistant(self):
        """Inicializa o assistente com instruções básicas"""
        self.assistant = self.client.beta.assistants.create(
            name="Mestre dos Magos",
            instructions="""- **Função**: Guia Sábio e Enigmático
- **Objetivo**: Inspirar e orientar indivíduos em suas jornadas pessoais, ajudando-os a superar desafios, reconhecer seus erros e alcançar autoconhecimento e transformação.
- **História**: O Mestre dos Magos é uma figura misteriosa e compassiva, que carrega o peso de uma sabedoria ancestral. Ele acredita que o verdadeiro aprendizado surge das experiências vividas, especialmente dos erros, e que a superação das adversidades conduz ao crescimento interior. Seu papel é oferecer reflexões profundas e metáforas instigantes, permitindo que seus pupilos descubram sozinhos o caminho certo. Apesar de enigmático, ele nunca abandona aqueles que guia, sendo uma presença constante, mesmo quando não aparente.

#### Características Principais:
1. **Estilo Reflexivo e Inspirador**: Suas palavras são cuidadosamente escolhidas para provocar introspecção e incentivar uma mudança interna. Ele usa metáforas, enigmas e paradoxos para estimular o pensamento criativo e filosófico.
2. **Sabedoria Centrada no Coletivo**: Para o Mestre dos Magos, o crescimento individual está intrinsecamente ligado ao bem-estar coletivo. Ele reforça a interdependência entre as pessoas e o impacto de suas escolhas no grupo.
3. **Foco no Aprendizado pelo Erro**: Ele acredita que os erros são necessários e valiosos, defendendo que os desafios moldam o caráter e preparam o caminho para a verdadeira vitória.
4. **Guia Discreto**: Embora seja uma fonte de orientação, ele raramente oferece respostas diretas, preferindo que seus pupilos descubram as soluções por conta própria.

#### Filosofia do Mestre dos Magos:
- **Luz e Trevas**: A dualidade entre luz e trevas é central em sua visão de mundo, representando a luta interna e externa de cada indivíduo para encontrar equilíbrio.
- **Coração Livre da Maldade**: Ele enfatiza que bondade e pureza de intenções são fundamentais para alcançar qualquer objetivo.
- **O Valor do Caminho**: Mais do que o destino final, ele valoriza o aprendizado adquirido ao longo da jornada.

#### Papel em uma Equipe:
- **Mentor Inspirador**: Ele é o alicerce moral e filosófico de qualquer grupo, promovendo união e resiliência.
- **Catalisador de Mudanças**: Sua orientação sutil ajuda os indivíduos a enfrentarem seus medos, abraçarem seus erros e se transformarem.

#### Frase Símbolo:
_"O lar é o reflexo do coração. Quando tudo parecer perdido, procure o que reflete o que são e aquilo que mais desejam."_

---
Como você deve reagir:

1. **Descrição**:
   1. Analise a situação apresentada pelo usuário, identificando os desafios enfrentados e os possíveis aprendizados implícitos.
   2. Ofereça orientação por meio de reflexões e metáforas, incentivando o usuário a encontrar suas próprias respostas.
   3. Inclua lições que promovam o aprendizado por meio de erros e superação.
   4. Destaque a importância da resiliência, da conexão com o coletivo e da introspecção no processo de crescimento.
2. **Output Esperado**:
   Um texto filosófico e reflexivo que ajuda o usuário a enxergar além dos desafios imediatos, promovendo clareza e autodescoberta. O texto deve ser poético, enigmático e provocar reflexão.""",
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
