from backend.database.connection import connect
def listar():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM fornecedor ORDER BY nome')]
def criar(d):
    with connect() as db:
        db.execute('INSERT INTO fornecedor(nome,contato,observacoes) VALUES(?,?,?)',(d.nome.strip(),d.contato.strip(),d.observacoes.strip()))
