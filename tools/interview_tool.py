import json
from crewai.tools import BaseTool
from typing import Literal, Optional

class CompleteInterviewTool(BaseTool):
    name: Literal["complete_interview"] = "complete_interview"
    description: str = """
    Use SOMENTE quando você tiver coletado todas as informações necessárias sobre:
    - Área de atuação e responsabilidades
    - Métricas quantitativas de performance
    - Desafios enfrentados
    - Pontos fortes
    - Objetivos profissionais
    
    Você deve passar todas as informações coletadas em formato JSON.
    """
    collected_data: Optional[str] = None

    def _run(self, collected_info: str) -> str:
        if self.collected_data is None:
            self.collected_data = collected_info
        
        return """
        Entrevista finalizada com sucesso. Todas as informações foram coletadas.
        Você deve agradecer ao usuário e informar que a análise começará agora.
        """
