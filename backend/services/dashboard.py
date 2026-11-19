from backend.database.connection import connect
def dados():
    with connect() as db:
        total=db.execute('SELECT COUNT(*) AS n FROM material').fetchone()['n']
        crit=db.execute('SELECT COUNT(*) AS n FROM material WHERE saldo_atual<=estoque_minimo OR (estoque_maximo>0 AND saldo_atual>estoque_maximo)').fetchone()['n']
        mov=db.execute('SELECT COUNT(*) AS n FROM movimentacao').fetchone()['n']
        baixo=[dict(r) for r in db.execute('SELECT codigo,descricao,saldo_atual,estoque_minimo,estoque_maximo,unidade FROM material WHERE saldo_atual<=estoque_minimo OR (estoque_maximo>0 AND saldo_atual>estoque_maximo) ORDER BY saldo_atual')]
        recentes=[dict(r) for r in db.execute('SELECT v.id,m.codigo,m.descricao material,v.tipo,v.quantidade,v.data_hora,v.observacao FROM movimentacao v JOIN material m ON m.id=v.material_id ORDER BY v.id DESC LIMIT 6')]
        resumo=[dict(r) for r in db.execute('SELECT tipo,CAST(SUM(quantidade) AS INTEGER) AS quantidade FROM movimentacao GROUP BY tipo')]
        return {'total_materiais':total,'estoque_critico':crit,'total_movimentacoes':mov,'estoque_baixo':baixo,'movimentacoes_recentes':recentes,'resumo_movimentacoes':resumo}
