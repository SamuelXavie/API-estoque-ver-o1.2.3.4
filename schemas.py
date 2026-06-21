"""
schemas.py
─────────────────────────────────────────────────────────────
Modelos Pydantic para a API de Estoque.
Tabelas cobertas (escopo do grupo de Estoque):
  - estoque
  - local_fisico
  - movimentacao_estoque
"""

from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import uuid


class MovimentacaoTipo(str, Enum):
    entrada = "entrada"
    saida = "saida"


# ══════════════════════════════════════════════════════════════
#  ESTOQUE
# ══════════════════════════════════════════════════════════════

class EstoqueBase(BaseModel):
    produto_id:        uuid.UUID     = Field(..., description="ID do produto (gerenciado pelo grupo de Produtos)")
    local_id:          uuid.UUID     = Field(..., description="ID do local físico onde está armazenado")
    quantidade:        int           = Field(..., ge=0, description="Quantidade atual em estoque")
    quantidade_minima: Optional[int] = Field(0,   ge=0, description="Nível mínimo antes de alertar reposição")
    quantidade_maxima: Optional[int] = Field(None, ge=0, description="Capacidade máxima do local para este item")

class EstoqueCriar(EstoqueBase):
    pass

class EstoqueAtualizar(BaseModel):
    produto_id:        Optional[uuid.UUID] = None
    local_id:          Optional[uuid.UUID] = None
    quantidade:        Optional[int]       = Field(None, ge=0)
    quantidade_minima: Optional[int]       = Field(None, ge=0)
    quantidade_maxima: Optional[int]       = Field(None, ge=0)

class EstoqueResposta(EstoqueBase):
    id:         uuid.UUID = Field(..., description="ID único do registro de estoque")
    created_at: datetime  = Field(..., description="Data de criação do registro")

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════
#  LOCAL FÍSICO
# ══════════════════════════════════════════════════════════════

class LocalFisicoBase(BaseModel):
    nome:      str           = Field(..., max_length=100, description="Nome do local (ex: Prateleira A-1, Galpão 2)")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do local")
    ativo:     bool          = Field(True, description="Local está em uso?")

class LocalFisicoCriar(LocalFisicoBase):
    pass

class LocalFisicoAtualizar(BaseModel):
    nome:      Optional[str]  = Field(None, max_length=100)
    descricao: Optional[str]  = None
    ativo:     Optional[bool] = None

class LocalFisicoResposta(LocalFisicoBase):
    id:         uuid.UUID = Field(..., description="ID único do local físico")
    created_at: datetime  = Field(..., description="Data de criação do registro")

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════
#  MOVIMENTAÇÃO DE ESTOQUE
# ══════════════════════════════════════════════════════════════

class MovimentacaoBase(BaseModel):
    estoque_id: uuid.UUID         = Field(..., description="ID do registro de estoque movimentado")
    tipo:       MovimentacaoTipo  = Field(..., description="Tipo da movimentação: 'entrada' ou 'saida'")
    quantidade: int               = Field(..., gt=0, description="Quantidade movimentada (sempre positivo)")
    observacao: Optional[str]     = Field(None, description="Motivo ou observação da movimentação")

    @validator("tipo", pre=True)
    def normalize_tipo(cls, value):
        # CORRIGIDO: sem este check, quando o Pydantic passa um MovimentacaoTipo
        # já instanciado (ex: em respostas ou revalidações internas), o validator
        # ignorava o isinstance(str) e caía direto no raise ValueError.
        if isinstance(value, MovimentacaoTipo):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "entrada":
                return MovimentacaoTipo.entrada
            if normalized in ("saida", "saída"):
                return MovimentacaoTipo.saida
        raise ValueError("Tipo deve ser 'entrada' ou 'saida'.")

class MovimentacaoCriar(MovimentacaoBase):
    pass

class MovimentacaoAtualizar(BaseModel):
    # Movimentações raramente são editadas; disponibilizamos PUT apenas
    # para correção de observação ou tipo, nunca da quantidade já registrada.
    tipo:       Optional[MovimentacaoTipo] = None
    observacao: Optional[str] = None

class MovimentacaoResposta(MovimentacaoBase):
    id:         uuid.UUID = Field(..., description="ID único da movimentação")
    created_at: datetime  = Field(..., description="Data/hora da movimentação")

    class Config:
        from_attributes = True
