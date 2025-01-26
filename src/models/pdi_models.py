from pydantic import BaseModel, field_validator
from typing import List, Optional
from enum import Enum
from datetime import datetime
import re

class TipoAtividade(str, Enum):
    CURSO = "curso"
    MENTORIA = "mentoria"
    PROJETO = "projeto"
    WORKSHOP = "workshop"
    LEITURA = "leitura"
    OUTRO = "outro"

class AtividadeEducacional(BaseModel):
    id: str
    titulo: str
    descricao: str
    trimestre: int
    tipo: TipoAtividade
    link: str  
    plataforma: str
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    tags: Optional[List[str]] = None
    prerequisitos: Optional[List[str]] = None

    # @field_validator('link')
    # @classmethod
    # def validate_url(cls, v):
    #     url_pattern = re.compile(
    #         r'^https?://'  
    #         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  
    #         r'localhost|'  
    #         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  
    #         r'(?::\d+)?'  
    #         r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
    #     if not url_pattern.match(v):
    #         raise ValueError('URL inválida')
    #     return v

    @field_validator('trimestre')
    @classmethod
    def validate_trimestre(cls, v):
        if not 1 <= v <= 4:
            raise ValueError('Trimestre deve estar entre 1 e 4')
        return v

class PDIConfig(BaseModel):
    titulo: str = "Plano de Desenvolvimento Individual"
    subtitulo: Optional[str] = None
    colaborador: str
    periodo: str
    atividades: List[AtividadeEducacional]