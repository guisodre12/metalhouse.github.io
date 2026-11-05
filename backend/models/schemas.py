from pydantic import BaseModel, Field
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
class MovimentacaoCreate(BaseModel):
    material_id: int
    tipo: Literal['Entrada','Saída']
    quantidade: int = Field(gt=0)
    observacao: str = ''
