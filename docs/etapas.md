Vou explicar a organização atual do projeto e detalhar o plano de implementação das novas funcionalidades. Esta será uma implementação em etapas, permitindo testes e validações a cada passo.

### Organização Atual do Projeto

O projeto está agora estruturado da seguinte forma, com os novos arquivos e diretórios adicionados:

```
pdi_crew/
├── config/
│   ├── agents.yaml     # Configuração dos agentes
│   └── tasks.yaml      # Definição das tarefas
├── tools/
│   ├── interview_tool.py  # Ferramenta de entrevista
│   └── pdi_visualizer_tool.py   # (Será criado na Etapa 1)
├── models/
│   ├── poker_metrics.py   # Modelos originais
│   └── pdi_models.py      # Novos modelos para o PDI
├── frontend/
│   ├── components/
│   │   └── PDITracker.tsx # Componente React do PDI
│   └── types/
│       └── pdi.ts         # Tipos TypeScript
├── main.py               # Programa principal
├── interview_manager.py  # Gerenciador de entrevistas
└── requirements.txt      # Dependências do projeto
```

Os novos arquivos adicionados têm as seguintes responsabilidades:

- `models/pdi_models.py`: Define a estrutura de dados do PDI usando Pydantic
- `frontend/components/PDITracker.tsx`: Componente React para visualização do PDI
- `frontend/types/pdi.ts`: Tipos TypeScript que espelham os modelos Pydantic

### Plano de Implementação

Vamos dividir a implementação em etapas bem definidas:

#### Etapa 1: Criação da PDIVisualizerTool

Seu assistente deverá criar o arquivo `tools/pdi_visualizer_tool.py`. Esta tool precisa:

1. Implementar a interface básica de uma CrewAI tool
2. Receber e validar dados usando os modelos Pydantic de `pdi_models.py`
3. Gerar a visualização do PDI integrando com o componente React

A tool deve ter:
- Método principal para criar a visualização
- Validação robusta dos dados de entrada
- Tratamento de erros adequado
- Documentação clara das entradas e saídas esperadas

Após a implementação, você poderá testar a tool isoladamente antes de prosseguir.

#### Etapa 2: Criação da Nova Task para o PDI Specialist

Nesta etapa, seu assistente deverá:

1. Adicionar uma nova task no arquivo `config/tasks.yaml`
2. A task deve:
   - Receber como contexto as saídas das tasks existentes
   - Utilizar a PDIVisualizerTool para gerar a interface
   - Produzir um output estruturado que será usado pela task seguinte

Esta etapa pode ser testada verificando se a task está:
- Recebendo corretamente o contexto das outras tasks
- Processando as informações adequadamente
- Gerando um output bem estruturado

#### Etapa 3: Adaptação da Task de Planejamento Estruturado

Seu assistente precisará modificar a task existente para:

1. Aceitar o novo input gerado na Etapa 2
2. Manter a compatibilidade com os inputs existentes
3. Integrar as informações do JSON na construção do PDI
4. Garantir que o output final inclua tanto o PDI tradicional quanto as informações para a interface

Esta etapa pode ser validada verificando se:
- O PDI mantém sua qualidade original
- As informações do JSON estão sendo corretamente incorporadas
- O output final está completo e bem estruturado

#### Etapa 4: Integração com Streamlit

Esta é a etapa final, onde seu assistente deverá:

1. Adicionar um botão no sidebar do Streamlit
2. Criar uma nova página/view para a interface do PDI
3. Implementar a lógica para:
   - Carregar os dados do PDI
   - Renderizar o componente React
   - Gerenciar o estado da interface
   - Persistir as informações de progresso

#### Etapas Adicionais Identificadas

1. **Gestão de Estado**:
   - Implementar persistência do progresso das atividades
   - Criar mecanismos de backup dos dados

2. **Segurança**:
   - Validação de dados em todas as camadas
   - Proteção contra inputs maliciosos

3. **Usabilidade**:
   - Feedback visual de carregamento
   - Mensagens de erro amigáveis
   - Tooltips e ajudas contextuais

4. **Testes**:
   - Testes unitários para a tool
   - Testes de integração para o fluxo completo
   - Testes de interface

### Próximos Passos

Para começar, sugiro que seu assistente inicie com a Etapa 1, criando a PDIVisualizerTool. Após a implementação, você poderá revisar e testar antes de prosseguir para as próximas etapas.

Para a Etapa 1, seu assistente precisará:

1. Criar o arquivo `pdi_visualizer_tool.py`
2. Implementar a estrutura básica da tool
3. Adicionar a lógica de validação usando os modelos Pydantic
4. Implementar a geração da visualização
5. Adicionar tratamento de erros
6. Documentar a implementação

Gostaria que eu detalhasse algum aspecto específico de qualquer uma das etapas?