from backend.database.connection import connect
def dados():
    with connect() as db:
        total=db.execute('SELECT COUNT(*) FROM material').fetchone()[0]
        crit=db.execute('SELECT COUNT(*) FROM material WHERE saldo_atual<=estoque_minimo').fetchone()[0]
        mov=db.execute('SELECT COUNT(*) FROM movimentacao').fetchone()[0]
        baixo=[dict(r) for r in db.execute('SELECT codigo,descricao,saldo_atual,estoque_minimo,unidade FROM material WHERE saldo_atual<=estoque_minimo ORDER BY saldo_atual')]
        recentes=[dict(r) for r in db.execute('SELECT v.id,m.codigo,m.descricao material,v.tipo,v.quantidade,v.data_hora,v.observacao FROM movimentacao v JOIN material m ON m.id=v.material_id ORDER BY v.id DESC LIMIT 6')]
        resumo=[dict(r) for r in db.execute('SELECT tipo,SUM(quantidade) quantidade FROM movimentacao GROUP BY tipo')]
        return {'total_materiais':total,'estoque_critico':crit,'total_movimentacoes':mov,'estoque_baixo':baixo,'movimentacoes_recentes':recentes,'resumo_movimentacoes':resumo}
