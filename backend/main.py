from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database.connection import init_db
from backend.routes.api import router
app=FastAPI(title='DDA Metalúrgica API')
app.include_router(router)
@app.on_event('startup')
def startup(): init_db()
dist=Path(__file__).resolve().parents[1]/'frontend'/'dist'
if dist.exists():
    app.mount('/assets',StaticFiles(directory=dist/'assets'),name='assets')
    @app.get('/')
    def home(): return FileResponse(dist/'index.html')
