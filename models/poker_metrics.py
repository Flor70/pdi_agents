from typing import Dict, List
from pydantic import BaseModel, Field

class BasicMetrics(BaseModel):
    total_hands: int = Field(..., description="Número total de mãos jogadas")
    vpip: float = Field(..., description="Voluntarily Put Money In Pot - Porcentagem de vezes que o jogador coloca dinheiro no pote voluntariamente")
    pfr: float = Field(..., description="Pre-Flop Raise - Porcentagem de vezes que o jogador faz raise no pre-flop")
    bb_100: float = Field(..., description="Big Blinds ganhos por 100 mãos")
    three_bet_freq: float = Field(..., description="Frequência de 3-bet")

class PositionMetrics(BaseModel):
    bb_100: float = Field(..., description="Big Blinds ganhos por 100 mãos nesta posição")
    hands: int = Field(..., description="Número de mãos jogadas nesta posição")
    frequency: float = Field(..., description="Frequência de jogo nesta posição")

class GapMetrics(BaseModel):
    vpip_pfr_gap: float = Field(..., description="Diferença entre VPIP e PFR")
    pfr_3bet_gap: float = Field(..., description="Diferença entre PFR e frequência de 3-bet")

class PokerAnalysisResult(BaseModel):
    basic_metrics: BasicMetrics = Field(..., description="Métricas básicas de performance")
    position_metrics: Dict[str, PositionMetrics] = Field(..., description="Métricas por posição na mesa")
    gap_metrics: GapMetrics = Field(..., description="Métricas de gap entre diferentes estatísticas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "basic_metrics": {
                    "total_hands": 1000,
                    "vpip": 25.5,
                    "pfr": 20.3,
                    "bb_100": 5.2,
                    "three_bet_freq": 8.1
                },
                "position_metrics": {
                    "BTN": {
                        "bb_100": 8.5,
                        "hands": 150,
                        "frequency": 15.0
                    },
                    "SB": {
                        "bb_100": -2.3,
                        "hands": 100,
                        "frequency": 10.0
                    }
                },
                "gap_metrics": {
                    "vpip_pfr_gap": 5.2,
                    "pfr_3bet_gap": 12.2
                }
            }
        }
