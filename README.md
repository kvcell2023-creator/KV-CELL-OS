# KV CELL PDV — Square Cloud

PDV + assistência técnica com peças compradas sob demanda.

Fluxo:
Fornecedor → compra da peça → custo unitário + frete/retirada → vínculo à OS → custo real → venda → margem.

Não exige estoque físico. O módulo de compras registra o histórico das peças efetivamente compradas.

## Square Cloud
Python 3.11
Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

Banco: SQLite em data/kvcell.db
