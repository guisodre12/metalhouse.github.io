import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database.connection import init_db
from backend.routes.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # SEED_DEMO=true: carrega dados de exemplo quando o banco está vazio (útil na Render gratuita).
    if os.getenv('SEED_DEMO', '').strip().lower() in ('1', 'true', 'sim', 'yes'):
        try:
            from backend.seed import popular_se_vazio
            popular_se_vazio()
        except Exception as e:  # nunca impede a API de subir
            print('Aviso: não foi possível carregar os dados de exemplo:', e)
    yield


app = FastAPI(title='MetalHouse API', lifespan=lifespan)

# Origens autorizadas a chamar a API (separe várias por vírgula na variável CORS_ORIGINS).
# O GitHub Pages usa apenas o domínio (sem o nome do repositório) como origem.
DEFAULT_ORIGINS = 'https://guisodre12.github.io,http://localhost:5173,http://127.0.0.1:5173'
origins = [o.strip() for o in os.getenv('CORS_ORIGINS', DEFAULT_ORIGINS).split(',') if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)


@app.get('/health')
def health():
    return {'status': 'ok'}


# Se o frontend estiver compilado em frontend/dist, o FastAPI também o serve (uso local).
dist = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
if dist.exists():
    app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')

    @app.get('/')
    def home():
        return FileResponse(dist / 'index.html')
else:
    @app.get('/')
    def home():
        return {'app': 'MetalHouse API', 'docs': '/docs'}
