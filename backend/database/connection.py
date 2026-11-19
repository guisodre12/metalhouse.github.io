import os, sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv('DB_PATH', BASE_DIR / 'data' / 'dda_metalurgica.db'))
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
USE_PG = bool(DATABASE_URL)

if USE_PG:
    import psycopg
    from psycopg.rows import dict_row
    IntegrityError = (sqlite3.IntegrityError, psycopg.errors.IntegrityError)
else:
    IntegrityError = (sqlite3.IntegrityError,)


class _PgDB:
    """Mesma interface usada com o sqlite3: db.execute(sql, params) com placeholders '?'."""
    def __init__(self):
        self.conn = psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=15)

    def execute(self, sql, params=()):
        return self.conn.execute(sql.replace('?', '%s'), tuple(params))

    def executescript(self, sql):
        for stmt in [x.strip() for x in sql.split(';') if x.strip()]:
            self.conn.execute(stmt)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
        return False


class _SqliteDB:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys = ON')

    def execute(self, sql, params=()):
        return self.conn.execute(sql, params)

    def executescript(self, sql):
        self.conn.executescript(sql)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
        return False


def connect():
    return _PgDB() if USE_PG else _SqliteDB()


def init_db():
    pk = 'SERIAL PRIMARY KEY' if USE_PG else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    with connect() as db:
        db.executescript(f'''
        CREATE TABLE IF NOT EXISTS fornecedor(id {pk},nome TEXT NOT NULL,contato TEXT,observacoes TEXT);
        CREATE TABLE IF NOT EXISTS material(id {pk},codigo TEXT NOT NULL UNIQUE,descricao TEXT NOT NULL,fabricante TEXT NOT NULL,fornecedor_id INTEGER,unidade TEXT NOT NULL,saldo_atual INTEGER NOT NULL DEFAULT 0,estoque_minimo INTEGER NOT NULL,estoque_maximo INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(fornecedor_id) REFERENCES fornecedor(id));
        CREATE TABLE IF NOT EXISTS movimentacao(id {pk},material_id INTEGER NOT NULL,tipo TEXT NOT NULL CHECK(tipo IN ('Entrada','Saída')),quantidade INTEGER NOT NULL CHECK(quantidade>0),data_hora TEXT NOT NULL,observacao TEXT,FOREIGN KEY(material_id) REFERENCES material(id));
        ''')
        # Bancos criados antes do estoque máximo ganham a coluna automaticamente.
        if USE_PG:
            db.execute('ALTER TABLE material ADD COLUMN IF NOT EXISTS estoque_maximo INTEGER NOT NULL DEFAULT 0')
        elif 'estoque_maximo' not in [r['name'] for r in db.execute('PRAGMA table_info(material)')]:
            db.execute('ALTER TABLE material ADD COLUMN estoque_maximo INTEGER NOT NULL DEFAULT 0')
