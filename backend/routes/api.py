import sqlite3
from fastapi import APIRouter, HTTPException
from backend.models.schemas import FornecedorCreate,MaterialCreate,MovimentacaoCreate
from backend.repositories import fornecedores,materiais,movimentacoes
from backend.services.dashboard import dados
router=APIRouter(prefix='/api')
@router.get('/dashboard')
def dashboard(): return dados()
@router.get('/fornecedores')
def get_fornecedores(): return fornecedores.listar()
@router.post('/fornecedores',status_code=201)
def post_fornecedor(d:FornecedorCreate):
    try: fornecedores.criar(d); return {'message':'Fornecedor cadastrado com sucesso!'}
    except Exception as e: raise HTTPException(400,str(e))
@router.get('/materiais')
def get_materiais(search:str=''): return materiais.listar(search)
@router.post('/materiais',status_code=201)
def post_material(d:MaterialCreate):
    try:
        if d.fornecedor_id not in [x['id'] for x in fornecedores.listar()]: raise ValueError('Selecione um fornecedor válido.')
        materiais.criar(d); return {'message':'Material cadastrado com sucesso!'}
    except ValueError as e: raise HTTPException(400,str(e))
    except sqlite3.IntegrityError: raise HTTPException(409,'Já existe um material com esse código.')
@router.get('/movimentacoes')
def get_mov(inicio:str|None=None,fim:str|None=None): return movimentacoes.listar(inicio,fim)
@router.post('/movimentacoes',status_code=201)
def post_mov(d:MovimentacaoCreate):
    try: return {'message':'Movimentação registrada com sucesso!','novo_saldo':movimentacoes.criar(d)}
    except ValueError as e: raise HTTPException(400,str(e))
@router.get('/relatorios')
def relatorios():
    ms=materiais.listar(); d=dados()
    return {'materiais':ms,'resumo_movimentacoes':d['resumo_movimentacoes'],'total_estoque':sum(x['saldo_atual'] for x in ms),'materiais_criticos':sum(x['saldo_atual']<=x['estoque_minimo'] for x in ms)}
