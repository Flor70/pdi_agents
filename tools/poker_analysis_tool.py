from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd
import numpy as np
import os
import pathlib

class PokerAnalysisInput(BaseModel):
    """Input schema for PokerAnalysisTool."""
    csv_path: str = Field(None, description="Não é necessário fornecer um caminho - a ferramenta já está configurada com o arquivo correto")

class PokerAnalysisTool(BaseTool):
    name: str = "Poker Game Analysis Tool"
    description: str = """Esta ferramenta já está configurada com o arquivo CSV correto. 
    Basta chamá-la sem nenhum parâmetro para analisar os dados e obter as métricas.
    
    IMPORTANTE: NÃO é necessário fornecer um caminho de arquivo - a ferramenta já sabe qual arquivo usar.
    
    Exemplo de uso:
    ```python
    # Correto - apenas chame a ferramenta
    result = tool._run()
    
    # Incorreto - não tente fornecer um caminho
    result = tool._run(csv_path="algum/caminho")
    ```
    
    A ferramenta retornará um dicionário com as seguintes métricas:
    - Total de mãos jogadas
    - VPIP (Voluntarily Put Money In Pot)
    - PFR (Pre-Flop Raise)
    - BB/100 (Big Blinds por 100 mãos)
    - Frequência de 3-bet
    - Métricas por posição
    - Gaps entre diferentes estatísticas"""
    
    args_schema: Type[BaseModel] = PokerAnalysisInput
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    csv_path: str = Field(None, description="Caminho para o arquivo CSV")
    
    def __init__(self, csv_path: str):
        super().__init__()
        self.csv_path = str(pathlib.Path(csv_path).resolve())
        if not os.path.exists(self.csv_path):
            raise ValueError(f"Arquivo CSV não encontrado: {self.csv_path}")

    def _run(self, csv_path: str = None) -> dict:
        try:
            # Sempre usar o caminho definido no construtor
            file_path = self.csv_path
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                return {
                    'error': True,
                    'message': f"Arquivo não encontrado: {file_path}"
                }
            
            # Ler o arquivo CSV
            df = pd.read_csv(file_path)
            
            # Calcular métricas básicas
            total_hands = len(df)
            
            # VPIP
            vpip_hands = df[~df['PF Act'].isin(['F', 'X'])].shape[0]
            vpip = (vpip_hands / total_hands * 100)
            
            # PFR
            pfr_hands = df[df['PF Act'].str.contains('R', na=False)].shape[0]
            pfr = (pfr_hands / total_hands * 100)
            
            # BB/100 geral
            total_bb = df['All-In Adj BB'].sum()
            bb_100 = (total_bb / total_hands) * 100
            
            # BB/100 por posição
            bb_by_position = df.groupby('Position').agg({
                'All-In Adj BB': lambda x: (x.sum() / len(x)) * 100,
                'Hand #': 'count'
            }).round(2).to_dict('index')
            
            # 3-bet frequency
            three_bet_opportunities = df[df['Facing PF Action'].str.contains('R', na=False)].shape[0]
            three_bet_hands = df[df['PF Act'].str.contains('RR', na=False)].shape[0]
            three_bet_freq = (three_bet_hands / three_bet_opportunities * 100) if three_bet_opportunities > 0 else 0
            
            # Distribuição de mãos por posição
            position_distribution = (df['Position'].value_counts() / total_hands * 100).to_dict()
            
            # Construir resultado
            results = {
                'basic_metrics': {
                    'total_hands': total_hands,
                    'vpip': round(vpip, 2),
                    'pfr': round(pfr, 2),
                    'bb_100': round(bb_100, 2),
                    'three_bet_freq': round(three_bet_freq, 2),
                },
                'position_metrics': {
                    position: {
                        'bb_100': stats['All-In Adj BB'],
                        'hands': int(stats['Hand #']),
                        'frequency': round(position_distribution.get(position, 0), 2)
                    }
                    for position, stats in bb_by_position.items()
                },
                'gap_metrics': {
                    'vpip_pfr_gap': round(vpip - pfr, 2),
                    'pfr_3bet_gap': round(pfr - three_bet_freq, 2)
                }
            }
            
            return results
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Erro ao analisar dados: {str(e)}"
            }

    def _clean_value(self, value):
        """Função auxiliar para limpar valores numéricos"""
        if isinstance(value, str):
            return float(value.replace('%', ''))
        return value
