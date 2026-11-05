from datetime import datetime
from backend.database.connection import connect
def listar(inicio=None,fim=None):
    sql='''SELECT v.id,m.codigo,m.descricao material,v.tipo,v.quantidade,v.data_hora,v.observacao FROM movimentacao v JOIN material m ON m.id=v.material_id WHERE 1=1'''; args=[]
    if inicio: sql+=' AND date(v.data_hora)>=date(?)'; args.append(inicio)
    if fim: sql+=' AND date(v.data_hora)<=date(?)'; args.append(fim)
    sql+=' ORDER BY v.id DESC'
    with connect() as db: return [dict(r) for r in db.execute(sql,args)]
def criar(d):
    with connect() as db:
        row=db.execute('SELECT saldo_atual FROM material WHERE id=?',(d.material_id,)).fetchone()
        if not row: raise ValueError('Material não encontrado.')
        saldo=row['saldo_atual']
        if d.tipo=='Saída' and d.quantidade>saldo: raise ValueError('Estoque insuficiente para realizar a saída.')
        novo=saldo+d.quantidade if d.tipo=='Entrada' else saldo-d.quantidade
        db.execute('INSERT INTO movimentacao(material_id,tipo,quantidade,data_hora,observacao) VALUES(?,?,?,?,?)',(d.material_id,d.tipo,d.quantidade,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),d.observacao.strip()))
        db.execute('UPDATE material SET saldo_atual=? WHERE id=?',(novo,d.material_id))
        return novo
