import os, sqlite3
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv('DB_PATH', BASE_DIR / 'data' / 'dda_metalurgica.db'))
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn
def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS fornecedor(id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL,contato TEXT,observacoes TEXT);
        CREATE TABLE IF NOT EXISTS material(id INTEGER PRIMARY KEY AUTOINCREMENT,codigo TEXT NOT NULL UNIQUE,descricao TEXT NOT NULL,fabricante TEXT NOT NULL,fornecedor_id INTEGER,unidade TEXT NOT NULL,saldo_atual INTEGER NOT NULL DEFAULT 0,estoque_minimo INTEGER NOT NULL,FOREIGN KEY(fornecedor_id) REFERENCES fornecedor(id));
        CREATE TABLE IF NOT EXISTS movimentacao(id INTEGER PRIMARY KEY AUTOINCREMENT,material_id INTEGER NOT NULL,tipo TEXT NOT NULL CHECK(tipo IN ('Entrada','Saída')),quantidade INTEGER NOT NULL CHECK(quantidade>0),data_hora TEXT NOT NULL,observacao TEXT,FOREIGN KEY(material_id) REFERENCES material(id));
        ''')
