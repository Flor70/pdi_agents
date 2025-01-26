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
    link: Optional[str] = None  
    plataforma: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    tags: Optional[List[str]] = None


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