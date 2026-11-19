from pydantic import BaseModel, Field, model_validator
from typing import Literal
class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    contato: str = ''
    observacoes: str = ''
class MaterialCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=60)
    descricao: str = Field(min_length=1, max_length=240)
    fabricante: str = Field(min_length=1, max_length=160)
    fornecedor_id: int
    unidade: Literal['Unidade','Peça','Caixa','Kg','Metro']
    saldo_inicial: int = Field(ge=0)
    estoque_minimo: int = Field(ge=0)
    estoque_maximo: int = Field(default=0, ge=0)  # 0 = sem limite máximo

    @model_validator(mode='after')
    def checar_limites(self):
        if self.estoque_maximo and self.estoque_maximo < self.estoque_minimo:
            raise ValueError('O estoque máximo não pode ser menor que o mínimo.')
        return self
class MovimentacaoCreate(BaseModel):
    material_id: int
    tipo: Literal['Entrada','Saída']
    quantidade: int = Field(gt=0)
    observacao: str = ''
class LimitesUpdate(BaseModel):
    estoque_minimo: int = Field(ge=0)
    estoque_maximo: int = Field(default=0, ge=0)  # 0 = sem limite máximo

    @model_validator(mode='after')
    def checar_limites(self):
        if self.estoque_maximo and self.estoque_maximo < self.estoque_minimo:
            raise ValueError('O estoque máximo não pode ser menor que o mínimo.')
        return self
