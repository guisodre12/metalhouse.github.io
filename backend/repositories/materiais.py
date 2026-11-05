from datetime import datetime
from backend.database.connection import connect
SQL = '''SELECT m.id,m.codigo,m.descricao,m.fabricante,m.fornecedor_id,f.nome fornecedor,m.unidade,m.saldo_atual,m.estoque_minimo FROM material m LEFT JOIN fornecedor f ON f.id=m.fornecedor_id'''
def listar(search=''):
    with connect() as db:
        if search.strip():
            term=f'%{search.strip()}%'; rows=db.execute(SQL+' WHERE m.codigo LIKE ? OR m.descricao LIKE ? OR m.fabricante LIKE ? ORDER BY m.codigo',(term,term,term))
        else: rows=db.execute(SQL+' ORDER BY m.codigo')
        return [dict(r) for r in rows]
def criar(d):
    with connect() as db:
        cur=db.execute('INSERT INTO material(codigo,descricao,fabricante,fornecedor_id,unidade,saldo_atual,estoque_minimo) VALUES(?,?,?,?,?,0,?)',(d.codigo.strip(),d.descricao.strip(),d.fabricante.strip(),d.fornecedor_id,d.unidade,d.estoque_minimo))
        mid=cur.lastrowid
        if d.saldo_inicial:
            db.execute("INSERT INTO movimentacao(material_id,tipo,quantidade,data_hora,observacao) VALUES(?,'Entrada',?,?, 'Estoque inicial')",(mid,d.saldo_inicial,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.execute('UPDATE material SET saldo_atual=? WHERE id=?',(d.saldo_inicial,mid))
