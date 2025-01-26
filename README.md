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

## Notas de Implementação

### Fix do SQLite3 para Streamlit Cloud

O Streamlit Cloud requer uma versão específica do SQLite3 (>= 3.35.0) para funcionar corretamente. Para garantir a compatibilidade, implementamos um fix que substitui o módulo SQLite3 padrão pelo pysqlite3. Aqui está o passo a passo para manter este fix funcionando:

1. **Dependência no requirements.txt**:
   ```
   pysqlite3-binary>=0.5.2
   ```
   - O pacote deve estar listado no arquivo `requirements.txt` na **raiz** do projeto
   - O nome do pacote no pip é `pysqlite3-binary`, mas o módulo Python é `pysqlite3`

2. **Implementação do Fix**:
   O fix deve ser implementado no início do arquivo principal (`app.py`), antes de qualquer outro código que possa usar SQLite:
   ```python
   import os
   import sys
   from pathlib import Path
   import sqlite3

   # SQLite3 version fix for Streamlit Cloud
   try:
       import pysqlite3
       sys.modules['sqlite3'] = pysqlite3
   except ImportError:
       pass
   ```

3. **Pontos Importantes**:
   - O fix deve ser executado antes de qualquer importação que possa usar SQLite3
   - Use `import pysqlite3` (não `pysqlite3-binary`)
   - Use atribuição direta ao `sys.modules` em vez de `pop()`
   - Coloque em um bloco try/except para evitar erros caso o módulo não esteja disponível

4. **Problemas Comuns**:
   - Se o erro `ModuleNotFoundError: No module named 'pysqlite3'` aparecer, verifique se:
     - O pacote está listado no `requirements.txt` na raiz do projeto
     - O nome do pacote está correto (`pysqlite3-binary`)
   - Se o erro `AttributeError: module 'pysqlite3-binary' has no attribute 'sqlite_version_info'` aparecer:
     - Use `import pysqlite3` em vez de tentar importar `pysqlite3-binary`
     - Remova a verificação de versão do SQLite3

5. **Testando Localmente**:
   - O fix é necessário apenas no Streamlit Cloud
   - Localmente, o código continuará funcionando mesmo sem o pysqlite3 instalado
   - Para testar o comportamento do Streamlit Cloud localmente, instale o `pysqlite3-binary`

Este fix é necessário porque o Streamlit Cloud usa uma versão do Python que vem com uma versão mais antiga do SQLite3. Ao substituir o módulo SQLite3 padrão pelo pysqlite3, garantimos que temos acesso a recursos mais recentes do SQLite3 necessários para o funcionamento correto da aplicação.

### Frontend no Streamlit Cloud

Para que o frontend React funcione corretamente no Streamlit Cloud, o diretório `frontend/dist` contendo o build do componente React é incluído diretamente no repositório. Isso elimina a necessidade de instalar Node.js e npm no Streamlit Cloud.

#### Estrutura do Frontend
```
frontend/
├── components/         # Componentes React
├── dist/              # Build gerado (commitar este diretório)
├── styles/            # Estilos CSS
├── package.json       # Dependências npm
└── webpack.config.js  # Configuração do build
```

#### Desenvolvimento Local
Para desenvolver e testar localmente:
```bash
cd frontend
npm install
npm run build
```

O build gerado em `frontend/dist` deve ser commitado para o repositório para garantir que o Streamlit Cloud possa encontrar os componentes React.

#### Problemas Comuns
- Se o erro "Componente de visualização não encontrado" aparecer:
  - Verifique se o diretório `frontend/dist` existe e está commitado no repositório
  - Confirme que o arquivo `frontend/dist/pdi-tracker.js` está presente
  - Execute `npm run build` localmente e commite as alterações se necessário