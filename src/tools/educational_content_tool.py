import pandas as pd
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from pathlib import Path

class EducationalContentInput(BaseModel):
    """Input schema for ReadEducationalDBTool."""
    query: str = Field(
        None, 
        description="Não é necessário fornecer nenhum parâmetro - a ferramenta já está configurada com o arquivo correto"
    )

class ReadEducationalDBTool(BaseTool):
    name: str = "read_educational_db"
    description: str = """
    Retorna o catálogo completo de conteúdos educacionais disponíveis para recomendação.
    
    IMPORTANTE: NÃO é necessário fornecer nenhum parâmetro - a ferramenta já sabe qual arquivo usar.
    
    Exemplo de uso:
    ```python
    # Correto - apenas chame a ferramenta
    result = tool._run()
    
    # Incorreto - não tente fornecer parâmetros
    result = tool._run(query="alguma coisa")
    ```
    """
    args_schema: Type[BaseModel] = EducationalContentInput

    def _run(self, query: str = None) -> str:
        try:
            # Define o caminho do arquivo
            content_file = Path(__file__).parent.parent.parent / 'data' / 'conteudos_desenvolvimento.csv'
            
            # Verifica se o arquivo existe
            if not content_file.exists():
                return "Erro: Arquivo de conteúdos não encontrado."
            
            # Lê o arquivo CSV
            df = pd.read_csv(content_file)
            
            # Formata cada linha como um item estruturado
            content_list = []
            for _, row in df.iterrows():
                content = (
                    f"Nome: {row['nome_do_conteudo']}\n"
                    f"Tipo: {row['tipo']}\n"
                    f"Área: {row['area_do_conhecimento']}\n"
                    f"Nível: {row['nivel']}\n"
                    f"Descrição: {row['descricao']}\n"
                    "---"
                )
                content_list.append(content)
            
            return "\n".join(content_list)
            
        except Exception as e:
            return "Erro ao ler a base de dados de conteúdos. Por favor, verifique se o arquivo CSV existe e está acessível."
