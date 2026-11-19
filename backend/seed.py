"""Popula o banco com dados de exemplo (fictícios) para demonstração.

Uso (na raiz do projeto):
    python -m backend.seed            # só popula se o banco estiver vazio
    python -m backend.seed --reset    # APAGA tudo e popula de novo (pede confirmação)

Para popular o banco do Neon, defina DATABASE_URL antes:
    DATABASE_URL='postgresql://...' python -m backend.seed
Sem DATABASE_URL, usa o SQLite local.
"""
import argparse
import random
from datetime import datetime, timedelta

from backend.database.connection import connect, init_db, USE_PG

FORNECEDORES = [
    ('Ferramentas Sul Distribuidora', '(21) 3000-0101 · vendas@ferramentassul.example', 'Prazo médio de entrega: 3 dias úteis.'),
    ('Usinagem Total Comercial', '(21) 3000-0102 · contato@usinagemtotal.example', 'Entrega expressa para São Gonçalo e Niterói.'),
    ('ToolBrasil Suprimentos', '(11) 3000-0103 · pedidos@toolbrasil.example', 'Pedido mínimo de 5 caixas.'),
    ('Metal Insumos RJ', '(21) 3000-0104 · atendimento@metalinsumos.example', 'Itens importados: prazo de aproximadamente 10 dias.'),
]

# código, descrição, fabricante, índice do fornecedor, unidade, mínimo, máximo (0 = sem limite), saldo final
MATERIAIS = [
    ('CNMG 120408-PM', 'Pastilha de torneamento CNMG 120408 para aço', 'Sandvik Coromant', 0, 'Caixa', 10, 60, 38),
    ('DNMG 150608-PF', 'Pastilha de torneamento DNMG 150608 para acabamento', 'Sandvik Coromant', 0, 'Caixa', 8, 40, 6),
    ('WNMG 080408-NMX', 'Pastilha WNMG 080408 para desbaste pesado', 'Kennametal', 1, 'Caixa', 10, 50, 55),
    ('TNMG 160408-UR', 'Pastilha TNMG 160408 de uso geral', 'Iscar', 2, 'Caixa', 12, 70, 44),
    ('VCMT 160408-F1', 'Pastilha VCMT 160408 para copiar', 'Seco Tools', 2, 'Caixa', 6, 30, 18),
    ('CCMT 09T304-PF', 'Pastilha CCMT 09T304 para acabamento fino', 'Mitsubishi Materials', 3, 'Caixa', 8, 40, 8),
    ('APMT 1135PDER', 'Pastilha de fresamento APMT 1135', 'Walter', 1, 'Caixa', 5, 25, 14),
    ('SNMG 120412-MR', 'Pastilha SNMG 120412 para ferro fundido', 'Tungaloy', 3, 'Caixa', 6, 36, 29),
    ('DCMT 11T304-SM', 'Pastilha DCMT 11T304 para mandrilamento', 'Korloy', 2, 'Caixa', 5, 30, 3),
    ('N123G2-0300', 'Pastilha de canal (bedame) 3 mm', 'Iscar', 2, 'Unidade', 20, 120, 75),
    ('16ER 1.5 ISO', 'Pastilha de rosca externa 16ER, passo 1,5', 'Sandvik Coromant', 0, 'Unidade', 15, 80, 90),
    ('SEHT 1204AFN', 'Pastilha para fresa de facear SEHT 1204', 'Kennametal', 1, 'Caixa', 4, 0, 11),
    ('RCMT 1204M0', 'Pastilha redonda RCMT 1204', 'Walter', 3, 'Caixa', 4, 24, 20),
    ('TPMT 110304', 'Pastilha TPMT 110304 para pequenos diâmetros', 'Seco Tools', 2, 'Caixa', 6, 36, 2),
]

OBS_ENTRADA = ['Compra NF {n} - {f}', 'Recebimento do pedido {n}', 'Reposição de estoque', 'Compra NF {n} - {f}']
OBS_SAIDA = ['Consumo OP {n} - Torno CNC', 'Consumo OP {n} - Centro de usinagem', 'Troca de pastilha - Setor Usinagem', 'Requisição da manutenção', 'Consumo OP {n} - Fresadora']
FMT = '%Y-%m-%d %H:%M:%S'


def gerar_movimentos(rng, agora, nome_forn, alvo, cap):
    """Histórico coerente: nunca fica negativo e termina exatamente no saldo alvo."""
    movs = []
    inicio = agora - timedelta(days=45)
    saldo = rng.randint(max(1, int(cap * 0.6)), cap)
    movs.append((inicio, 'Entrada', saldo, 'Estoque inicial'))
    n_ops = rng.randint(6, 10)
    instantes = sorted(inicio + timedelta(seconds=rng.randint(86400, int((agora - inicio).total_seconds()) - 2 * 86400)) for _ in range(n_ops))
    for ts in instantes:
        if saldo > 0 and rng.random() < 0.65:
            q = rng.randint(1, max(1, min(saldo, -(-cap // 5))))
            saldo -= q
            movs.append((ts, 'Saída', q, rng.choice(OBS_SAIDA).format(n=rng.randint(2000, 2999))))
        else:
            q = rng.randint(max(1, cap // 10), max(2, cap // 3))
            saldo += q
            movs.append((ts, 'Entrada', q, rng.choice(OBS_ENTRADA).format(n=rng.randint(1000, 9999), f=nome_forn)))
    diff = alvo - saldo
    if diff:
        ts = agora - timedelta(hours=rng.randint(2, 30))
        if diff > 0:
            movs.append((ts, 'Entrada', diff, rng.choice(OBS_ENTRADA).format(n=rng.randint(1000, 9999), f=nome_forn)))
        else:
            movs.append((ts, 'Saída', -diff, rng.choice(OBS_SAIDA).format(n=rng.randint(2000, 2999))))
    return movs


def limpar(db):
    if USE_PG:
        db.execute('TRUNCATE movimentacao, material, fornecedor RESTART IDENTITY CASCADE')
    else:
        for t in ('movimentacao', 'material', 'fornecedor'):
            db.execute(f'DELETE FROM {t}')
        try:
            db.execute('DELETE FROM sqlite_sequence')
        except Exception:
            pass


def popular(db):
    """Insere fornecedores, materiais e movimentações de exemplo usando a conexão aberta."""
    rng = random.Random(2026)
    agora = datetime.now().replace(microsecond=0)
    forn_ids = [db.execute('INSERT INTO fornecedor(nome,contato,observacoes) VALUES(?,?,?) RETURNING id', f).fetchone()['id'] for f in FORNECEDORES]

    todos = []
    for cod, desc, fab, fi, un, mn, mx, alvo in MATERIAIS:
        mid = db.execute(
            'INSERT INTO material(codigo,descricao,fabricante,fornecedor_id,unidade,saldo_atual,estoque_minimo,estoque_maximo) VALUES(?,?,?,?,?,?,?,?) RETURNING id',
            (cod, desc, fab, forn_ids[fi], un, alvo, mn, mx)).fetchone()['id']
        cap = mx if mx else alvo * 2
        for ts, tipo, q, obs in gerar_movimentos(rng, agora, FORNECEDORES[fi][0], alvo, cap):
            todos.append((ts, mid, tipo, q, obs))
    todos.sort(key=lambda x: x[0])  # ids em ordem cronológica
    for ts, mid, tipo, q, obs in todos:
        db.execute('INSERT INTO movimentacao(material_id,tipo,quantidade,data_hora,observacao) VALUES(?,?,?,?,?)', (mid, tipo, q, ts.strftime(FMT), obs))
    return len(FORNECEDORES), len(MATERIAIS), len(todos)


def popular_se_vazio():
    """Usado na inicialização da API (SEED_DEMO=true): só popula se não houver nenhum material."""
    with connect() as db:
        if db.execute('SELECT COUNT(*) AS n FROM material').fetchone()['n']:
            return False
        popular(db)
    return True


def main():
    ap = argparse.ArgumentParser(description='Popula o banco com dados de exemplo.')
    ap.add_argument('--reset', action='store_true', help='apaga todos os dados antes de popular')
    ap.add_argument('--yes', action='store_true', help='não pede confirmação do --reset')
    args = ap.parse_args()

    init_db()
    destino = 'Postgres (DATABASE_URL)' if USE_PG else 'SQLite local'
    with connect() as db:
        existentes = db.execute('SELECT COUNT(*) AS n FROM material').fetchone()['n']
        if existentes and not args.reset:
            print(f'O banco já tem {existentes} material(is). Nada foi alterado.')
            print('Use --reset para apagar tudo e popular de novo.')
            return
        if args.reset:
            if not args.yes and input(f'Isso APAGA todos os dados de {destino}. Digite SIM para continuar: ').strip() != 'SIM':
                print('Cancelado.')
                return
            limpar(db)
        nf, nm, nv = popular(db)
    print(f'Pronto ({destino}): {nf} fornecedores, {nm} materiais, {nv} movimentações.')


if __name__ == '__main__':
    main()
