# PDI Crew

Sistema de Análise de Desenvolvimento Profissional baseado em CrewAI

## Descrição

Este projeto utiliza a framework CrewAI para criar um sistema de análise de desenvolvimento profissional que:
1. Conduz uma entrevista interativa para coletar informações sobre o perfil profissional
2. Analisa os dados coletados para identificar pontos fortes e áreas de melhoria
3. Gera recomendações personalizadas para desenvolvimento profissional
4. Cria um plano de ação detalhado
5. Fornece uma interface interativa para visualização e acompanhamento do PDI

## Requisitos

- Python 3.10+
- Conda (recomendado para gerenciamento de ambiente)
- Node.js e npm (para o frontend)
- Chaves de API:
  - OpenAI API Key (para o ChatGPT)
  - Claude API Key (para o Claude)
  - Exa API Key (para pesquisa web)
  - Serper API Key (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/pdi_crew.git
cd pdi_crew
```

2. Crie e ative o ambiente conda:
```bash
conda create -n crewai_env python=3.10
conda activate crewai_env
```

3. Instale as dependências Python:
```bash
pip install -r config/requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
OPENAI_API_KEY=sua-chave-api
CLAUDE_API_KEY=sua-chave-api
EXA_API_KEY=sua-chave-api
SERPER_API_KEY=sua-chave-api
```

5. Instale as dependências do frontend:
```bash
cd frontend
npm install
npm run build
```

## Estrutura do Projeto

```
pdi_crew/
├── config/                    # Configurações do sistema
│   ├── agents.yaml           # Configuração dos agentes
│   ├── tasks.yaml            # Definição das tarefas
│   ├── requirements.txt      # Dependências Python
│   └── packages.txt          # Dependências do sistema
│
├── data/                     # Dados e recursos
│   └── conteudos_desenvolvimento.csv  # Base de conteúdos
│
├── src/                      # Código fonte principal
│   ├── assistants/          # Assistentes conversacionais
│   │   ├── __init__.py
│   │   ├── interview_assistant.py  # Assistente de entrevista
│   │   ├── pdi_assistant.py       # Chatbot PDI
│   │   └── docs/                  # Documentação
│   │       └── pdi_guide.md       # Guia do PDI
│   ├── components/
│   │   └── PDITracker.tsx
│   │
│   ├── tools/               # Ferramentas dos agentes
│   │   ├── __init__.py
│   │   ├── educational_content_tool.py
│   │   ├── exa_search_tool.py
│   │   └── serper_search_tool.py
│   │
│   ├── models/              # Modelos de dados
│   │   ├── __init__.py
│   │   └── pdi_models.py
│   │
│   ├── core/               # Lógica central
│   │   ├── __init__.py
│   │   ├── utils.py       # Utilitários gerais
│   │   └── helper.py      # Gerenciamento de APIs
│   │
│   └── web/               # Interface web
│       ├── __init__.py
│       ├── app.py        # App Streamlit principal
│       └── app_test.py   # App de testes
│
├── frontend/              # Interface React
│   ├── components/
│   │   └── PDITracker.tsx
│   ├── styles/
│   └── webpack.config.js
│
└── output/               # Saída gerada
```

## Componentes do Sistema

### Módulo `src/assistants/`
Contém os assistentes conversacionais baseados no framework de agents da OpenAI:

- **interview_assistant.py**:
  - Conduz a entrevista inicial
  - Coleta informações do usuário
  - Interface conversacional natural
  - Prepara dados para a crew

- **pdi_assistant.py**:
  - Chatbot pós-geração do PDI
  - Responde dúvidas sobre o plano
  - Acessa documentos gerados
  - Oferece explicações detalhadas

### Módulo `src/tools/`
Ferramentas utilizadas pelos agentes para pesquisa e análise:

- **educational_content_tool.py**:
  - Lê dados de `data/conteudos_desenvolvimento.csv`
  - Recomenda conteúdos internos
  - Integra recursos da empresa

- **exa_search_tool.py**:
  - Principal ferramenta de pesquisa
  - Busca conteúdos externos
  - Utiliza API da Exa

- **serper_search_tool.py**:
  - Alternativa de pesquisa
  - Backup para o Exa
  - Pesquisa via API Serper

### Módulo `src/core/`
Núcleo do sistema com utilitários e configurações:

- **utils.py**:
  - Funções utilitárias
  - Sequenciamento de tarefas
  - Lógica de geração do PDI

- **helper.py**:
  - Gerenciamento de APIs
  - Configurações sensíveis
  - Utilitários de segurança

### Módulo `src/web/`
Interface web do sistema:

- **app.py**:
  - Aplicação Streamlit principal
  - Integra todos os componentes
  - Gerencia fluxo completo

- **app_test.py**:
  - Versão de teste
  - Carrega dados existentes
  - Desenvolvimento rápido

### Módulo `src/models/`
Modelos de dados e validação:

- **pdi_models.py**:
  - Classes Pydantic
  - Validação de dados
  - Estruturas do PDI

### Frontend
Interface do usuário em React:

- **PDITracker.tsx**:
  - Visualização interativa
  - Progresso do PDI
  - Organização por trimestre

## Fluxo de Execução

1. **Entrevista Inicial**:
```bash
streamlit run src/web/app.py
```

2. **Modo Teste**:
```bash
streamlit run src/web/app_test.py
```

## Fluxo de Dados

1. **Coleta de Dados**:
   - Entrevista via `interview_assistant.py`
   - Dados salvos em `output/`

2. **Processamento**:
   - Análise pela crew
   - Uso das tools para pesquisa
   - Geração do PDI estruturado

3. **Visualização**:
   - Conversão para JSON
   - Renderização React
   - Interface interativa

## Desenvolvimento

Para adicionar novos componentes:

1. **Novos Assistentes**:
   - Criar em `src/assistants/`
   - Herdar padrões existentes
   - Atualizar `__init__.py`

2. **Novas Ferramentas**:
   - Adicionar em `src/tools/`
   - Seguir padrão das tools existentes
   - Registrar em `config/tasks.yaml`

3. **Novos Modelos**:
   - Definir em `src/models/`
   - Usar Pydantic
   - Manter validações

## Nota sobre SQLite e Streamlit Cloud

Para garantir a compatibilidade com o Streamlit Cloud, o projeto utiliza uma versão específica do SQLite. Isso é gerenciado através do seguinte código no início da aplicação:

```python
import sqlite3
import sys

if sqlite3.sqlite_version_info < (3, 35, 0):
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

Este código garante que a aplicação funcionará corretamente no ambiente do Streamlit Cloud.