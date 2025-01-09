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
    
    Métricas Básicas:
    - Total de mãos jogadas
    - VPIP (Voluntarily Put Money In Pot)
    - PFR (Pre-Flop Raise)
    - Total de fichas ganhas
    - BB/100 (Big Blinds por 100 mãos)
    - Total de BB ganhos
    
    Métricas de Pré-Flop:
    - Frequência de 3-bet
    - Frequência de 4-bet
    - Razão de 4-bet
    - Frequência de Call em 3-bet
    
    Métricas de Steal:
    - Frequência de Fold to Steal
    - Frequência de 3-bet Steal
    - Frequência de Cold Call
    - Frequência de Squeeze
    
    Métricas Pós-Flop:
    - WTSD (Went to Showdown)
    - WSD (Won at Showdown)
    - WWSF (Won When Saw Flop)
    - Frequência de C-bet no Flop
    - Frequência de C-bet no Turn
    - Frequência de C-bet no River
    
    Métricas por Posição:
    - BB/100 por posição
    - Distribuição de mãos por posição
    
    Estatísticas Detalhadas:
    - Oportunidades e realizações de 3-bet e 4-bet
    - Situações de steal e defesa contra steal
    - Dados de showdown e pós-flop
    - Oportunidades e realizações de squeeze
    - Contagem de cold calls"""
    
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
            pfr = (df['Preflop Raise'].sum() / total_hands * 100)

            # Chips Won

            def clean_chips_won(value):
                if pd.isna(value):
                    return 0
                try:
                    # Remove vírgulas e converte para float
                    return float(str(value).replace(',', ''))
                except (ValueError, AttributeError):
                    return 0
            total_chips_won = df['Chips Won'].apply(clean_chips_won).sum()

            
            # BB/100 geral e BB Won
            total_allin_adj_bb = df['All-In Adj BB'].sum()
            bb_100 = (total_allin_adj_bb / total_hands) * 100
            total_bb_won = df['BB Won'].sum()
            
            # BB/100 por posição
            bb_by_position = df.groupby('Position').agg({
                'All-In Adj BB': lambda x: (x.sum() / len(x)) * 100,
                'Hand #': 'count'
            }).round(2).to_dict('index')
            
            # 3-bet metrics
            three_bet_opportunities = df[df['Facing PF Action'].str.contains('Raise', na=False)].shape[0]
            three_bet_hands = df[df['PF Act'].str.contains('RR', na=False)].shape[0]
            three_bet_freq = (three_bet_hands / three_bet_opportunities * 100) if three_bet_opportunities > 0 else 0
            
            # 4-bet metrics
            four_bet_opportunities = df[df['Facing PF Action'].str.contains('3Bet', na=False)].shape[0]
            four_bet_hands = df[df['PF Act'].str.contains('RRR', na=False)].shape[0]
            four_bet_freq = (four_bet_hands / four_bet_opportunities * 100) if four_bet_opportunities > 0 else 0
            four_bet_ratio = (four_bet_hands / three_bet_hands * 100) if three_bet_hands > 0 else 0
            
            # Call 3-bet metrics
            facing_three_bet = df[df['Facing PF Action'].str.contains('3Bet', na=False)].shape[0]
            call_three_bet = df[(df['Facing PF Action'].str.contains('3Bet', na=False)) & 
                              (df['PF Act'].str.contains('C', na=False))].shape[0]
            call_three_bet_freq = (call_three_bet / facing_three_bet * 100) if facing_three_bet > 0 else 0
            
            # Cold Call e Squeeze metrics
            cold_calls = df[df['CC 2Bet PF'] == 'Yes'].shape[0]
            cold_call_opportunities = df[df['Facing PF Action'].str.contains('Raise', na=False)].shape[0]
            cold_call_freq = (cold_calls / cold_call_opportunities * 100) if cold_call_opportunities > 0 else 0
            
            squeeze_attempts = df[df['Preflop Squeeze'] == 'Yes'].shape[0]
            squeeze_opportunities = df[df['Facing PF Action'].str.contains('Raise.*Caller', na=False)].shape[0]
            squeeze_freq = (squeeze_attempts / squeeze_opportunities * 100) if squeeze_opportunities > 0 else 0
            
            # Steal metrics
            steal_attempts = df[(df['SB'] | df['BB']) & 
                              (df['Facing PF Action'].str.contains('Raise', na=False))].shape[0]
            fold_to_steal = df[(df['SB'] | df['BB']) & 
                              (df['Facing PF Action'].str.contains('Raise', na=False)) &
                              (df['PF Act'] == 'F')].shape[0]
            fold_to_steal_freq = (fold_to_steal / steal_attempts * 100) if steal_attempts > 0 else 0
            
            threeb_steal_attempts = df[(df['SB'] | df['BB']) & 
                                     (df['Facing PF Action'].str.contains('Raise', na=False)) &
                                     (df['PF Act'].str.contains('RR', na=False))].shape[0]
            threeb_steal_freq = (threeb_steal_attempts / steal_attempts * 100) if steal_attempts > 0 else 0
            
            # Showdown metrics
            wtsd = df['Showdown'].sum()
            saw_flop = df['Saw Flop'].sum()
            wtsd_freq = (wtsd / saw_flop * 100) if saw_flop > 0 else 0
            
            won_at_showdown = df[(df['Showdown']) & (df['Winner'] == df['Player Name'])].shape[0]
            wsd_freq = (won_at_showdown / wtsd * 100) if wtsd > 0 else 0
            
            won_with_flop = df[(df['Saw Flop']) & (df['Winner'] == df['Player Name'])].shape[0]
            wwsf_freq = (won_with_flop / saw_flop * 100) if saw_flop > 0 else 0
            
            # Continuation bet metrics
            flop_cbet_opportunities = df[(df['Preflop Raise']) & (df['Saw Flop'])].shape[0]
            flop_cbets = df[(df['Preflop Raise']) & (df['F Act'].str.contains('B', na=False))].shape[0]
            flop_cbet_freq = (flop_cbets / flop_cbet_opportunities * 100) if flop_cbet_opportunities > 0 else 0
            
            turn_cbet_opportunities = df[(df['Preflop Raise']) & (df['Saw Turn'])].shape[0]
            turn_cbets = df[(df['Preflop Raise']) & (df['T Act'].str.contains('B', na=False))].shape[0]
            turn_cbet_freq = (turn_cbets / turn_cbet_opportunities * 100) if turn_cbet_opportunities > 0 else 0
            
            river_cbet_opportunities = df[(df['Preflop Raise']) & (df['Saw River'])].shape[0]
            river_cbets = df[(df['Preflop Raise']) & (df['R Act'].str.contains('B', na=False))].shape[0]
            river_cbet_freq = (river_cbets / river_cbet_opportunities * 100) if river_cbet_opportunities > 0 else 0
            
            # Distribuição de mãos por posição
            position_distribution = (df['Position'].value_counts() / total_hands * 100).to_dict()
            
            # Construir resultado
            results = {
                'basic_metrics': {
                    'total_hands': total_hands,
                    'vpip': round(vpip, 2),
                    'pfr': round(pfr, 2),
                    'total_chips_won': total_chips_won,
                    'bb_100': round(bb_100, 2),
                    'total_bb_won': round(total_bb_won, 2),
                },
                'preflop_metrics': {
                    'three_bet_frequency': round(three_bet_freq, 2),
                    'four_bet_frequency': round(four_bet_freq, 2),
                    'four_bet_ratio': round(four_bet_ratio, 2),
                    'call_three_bet_frequency': round(call_three_bet_freq, 2),
                },
                'steal_metrics': {
                    'fold_to_steal_frequency': round(fold_to_steal_freq, 2),
                    'three_bet_steal_frequency': round(threeb_steal_freq, 2),
                    'cold_call_frequency': round(cold_call_freq, 2),
                    'squeeze_frequency': round(squeeze_freq, 2)
                },
                'postflop_metrics': {
                    'wtsd_frequency': round(wtsd_freq, 2),
                    'wsd_frequency': round(wsd_freq, 2),
                    'wwsf_frequency': round(wwsf_freq, 2),
                    'flop_cbet_frequency': round(flop_cbet_freq, 2),
                    'turn_cbet_frequency': round(turn_cbet_freq, 2),
                    'river_cbet_frequency': round(river_cbet_freq, 2)
                },
                'position_metrics': {
                    'bb_by_position': bb_by_position,
                    'position_distribution': position_distribution
                },
                'stats': {
                    'three_bet_opportunities': three_bet_opportunities,
                    'three_bet_hands': three_bet_hands,
                    'four_bet_opportunities': four_bet_opportunities,
                    'four_bet_hands': four_bet_hands,
                    'facing_three_bet': facing_three_bet,
                    'call_three_bet': call_three_bet,
                    'saw_flop': saw_flop,
                    'went_to_showdown': wtsd,
                    'won_at_showdown': won_at_showdown,
                    'squeeze_attempts': squeeze_attempts,
                    'squeeze_opportunities': squeeze_opportunities,
                    'cold_calls': cold_calls,
                    'steal_attempts': steal_attempts,
                    'fold_to_steal': fold_to_steal
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
