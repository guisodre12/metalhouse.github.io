export type Fornecedor={id:number;nome:string;contato:string;observacoes:string};
export type Material={id:number;codigo:string;descricao:string;fabricante:string;fornecedor_id:number;fornecedor:string|null;unidade:string;saldo_atual:number;estoque_minimo:number};
export type Movimentacao={id:number;codigo:string;material:string;tipo:'Entrada'|'Saída';quantidade:number;data_hora:string;observacao:string};
export type DashboardData={total_materiais:number;estoque_critico:number;total_movimentacoes:number;estoque_baixo:Array<{codigo:string;descricao:string;saldo_atual:number;estoque_minimo:number;unidade:string}>;movimentacoes_recentes:Movimentacao[];resumo_movimentacoes:{tipo:string;quantidade:number}[]};
