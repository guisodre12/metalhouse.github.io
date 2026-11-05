# DDA Metalúrgica — React + TypeScript + FastAPI + SQLite

Projeto modular para controle de estoque de pastilhas industriais.

## Estrutura
- `backend/database`: conexão e inicialização do SQLite.
- `backend/models`: schemas de validação.
- `backend/repositories`: consultas e persistência SQL.
- `backend/services`: indicadores e regras agregadas.
- `backend/routes`: endpoints REST.
- `frontend/src/components`: componentes visuais reutilizáveis.
- `frontend/src/pages`: telas por funcionalidade.
- `frontend/src/services.ts`: comunicação com a API e exportação CSV.
- `frontend/src/types.ts`: tipos TypeScript.

## Sobre Node.js
O backend é Python puro (FastAPI + sqlite3). React com TypeScript precisa de uma etapa de compilação do frontend; para isso, Node/npm é usado **somente no build**, não como backend nem como servidor em produção. Depois de gerar `frontend/dist`, o FastAPI serve os arquivos estáticos.

## Instalação
1. Python 3.10+: `python -m venv .venv` e ative o ambiente.
2. `pip install -r requirements.txt`
3. Build do frontend: `cd frontend && npm install && npm run build && cd ..`
4. `python run.py`
5. Acesse `http://127.0.0.1:8000`.

Desenvolvimento: rode `uvicorn backend.main:app --reload` e, em outro terminal, `cd frontend && npm run dev` (Vite encaminha `/api` para o FastAPI).

## Banco existente
A estrutura mantém as tabelas `fornecedor`, `material` e `movimentacao` do projeto Streamlit. Copie seu `dda_metalurgica.db` para `data/dda_metalurgica.db` antes de iniciar. Também é possível definir `DB_PATH` com o caminho do banco existente.

## Funcionalidades
Dashboard, cadastro de materiais e fornecedores, consulta e pesquisa, entradas e saídas com validação de saldo, histórico com filtro de datas, relatórios e exportação CSV.
