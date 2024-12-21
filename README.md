# PDI Crew

Sistema de Análise de Desenvolvimento Profissional baseado em CrewAI

## Descrição

Este projeto utiliza a framework CrewAI para criar um sistema de análise de desenvolvimento profissional que:
1. Conduz uma entrevista interativa para coletar informações sobre o perfil profissional
2. Analisa os dados coletados para identificar pontos fortes e áreas de melhoria
3. Gera recomendações personalizadas para desenvolvimento profissional
4. Cria um plano de ação detalhado

## Requisitos

- Python 3.10+
- Conda (recomendado para gerenciamento de ambiente)
- Chaves de API:
  - OpenAI API Key (para o ChatGPT)
  - Claude API Key (para o Claude)

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

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
OPENAI_API_KEY=sua-chave-api
CLAUDE_API_KEY=sua-chave-api
```

## Uso

Execute o programa principal:
```bash
python main.py
```

O sistema irá:
1. Iniciar uma entrevista interativa
2. Coletar informações sobre seu perfil profissional
3. Gerar análises e recomendações
4. Criar relatórios detalhados na pasta `output/`

## Estrutura do Projeto

```
pdi_crew/
├── config/
│   ├── agents.yaml     # Configuração dos agentes
│   └── tasks.yaml      # Definição das tarefas
├── tools/
│   └── interview_tool.py  # Ferramenta de entrevista
├── models/
│   └── poker_metrics.py   # Modelos de dados
├── main.py               # Programa principal
├── interview_manager.py  # Gerenciador de entrevistas
└── requirements.txt      # Dependências do projeto
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
