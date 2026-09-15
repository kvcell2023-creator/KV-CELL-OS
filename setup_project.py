import os

files = {
    "static/css/kvcello.css": """
:root {
    --bg-main: #0c0d10;
    --bg-card: #15171e;
    --bg-input: #1f222d;
    --primary-yellow: #f1c40f;
    --primary-hover: #ffd700;
    --text-light: #f5f6fa;
    --text-muted: #95a5a6;
    --border-color: #2c3e50;
    --danger: #e74c3c;
    --success: #2ecc71;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
body { background-color: var(--bg-main); color: var(--text-light); min-height: 100vh; display: flex; flex-direction: column; }

header { background: #000; border-bottom: 2px solid var(--primary-yellow); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; }
.logo-badge { background: var(--primary-yellow); color: #000; font-weight: 900; padding: 6px 14px; border-radius: 6px; font-size: 1.2rem; }
.unit-tag { background: #222; color: var(--primary-yellow); padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; border: 1px solid var(--primary-yellow); }

.layout-container { display: flex; flex: 1; }
aside { width: 240px; background: #111; border-right: 1px solid #222; padding: 15px 0; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: var(--text-muted); text-decoration: none; font-weight: 600; cursor: pointer; transition: 0.2s; }
.nav-item:hover, .nav-item.active { background: rgba(241, 196, 15, 0.1); color: var(--primary-yellow); border-left: 4px solid var(--primary-yellow); }

main { flex: 1; padding: 20px; max-width: 1400px; width: 100%; }
.card { background: var(--bg-card); border: 1px solid #252836; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
.card-title { color: var(--primary-yellow); font-size: 1.2rem; font-weight: 700; margin-bottom: 15px; }

.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
.stat-box { background: #1a1d27; border-left: 4px solid var(--primary-yellow); border-radius: 8px; padding: 16px; }
.stat-val { font-size: 1.8rem; font-weight: 800; color: #fff; margin-top: 5px; }

input, select, textarea { width: 100%; padding: 10px; background: var(--bg-input); border: 1px solid #2e3346; border-radius: 6px; color: #fff; margin-top: 5px; }
.btn { padding: 10px 18px; border-radius: 6px; border: none; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
.btn-yellow { background: var(--primary-yellow); color: #000; }
.btn-dark { background: #2b3042; color: #fff; }

table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #232736; }
th { background: #11131a; color: var(--primary-yellow); }

@media (max-width: 768px) {
    .layout-container { flex-direction: column; }
    aside { width: 100%; display: flex; overflow-x: auto; white-space: nowrap; }
}

@media print {
    body * { visibility: hidden; }
    #printableArea, #printableArea * { visibility: visible; }
    #printableArea { position: absolute; left: 0; top: 0; width: 100%; color: #000; background: #fff; padding: 20px; }
}
""",

    "static/index.html": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KV CELL - ERP / PDV System</title>
    <link rel="stylesheet" href="/static/css/kvcello.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>

    <header>
        <div style="display:flex; align-items:center; gap:12px;">
            <div class="logo-badge">KV CELL</div>
            <span class="unit-tag" id="displayUnit">Carregando...</span>
        </div>
        <button class="btn btn-dark" onclick="logout()"><i class="fa-solid fa-right-from-bracket"></i> Sair</button>
    </header>

    <div class="layout-container">
        <aside>
            <div class="nav-item active" onclick="showTab('dashboard')"><i class="fa-solid fa-chart-line"></i> Dashboard</div>
            <div class="nav-item" onclick="showTab('pdv')"><i class="fa-solid fa-cash-register"></i> PDV</div>
            <div class="nav-item" onclick="showTab('os')"><i class="fa-solid fa-screwdriver-wrench"></i> Ordens de Serviço</div>
            <div class="nav-item" onclick="showTab('estoque')"><i class="fa-solid fa-boxes-stacked"></i> Estoque</div>
            <div class="nav-item" onclick="showTab('compras')"><i class="fa-solid fa-truck-field"></i> Compras de Peças</div>
            <div class="nav-item" onclick="showTab('aparelhos')"><i class="fa-solid fa-mobile-screen-button"></i> Aparelhos Usados</div>
        </aside>

        <main>
            <section id="tab-dashboard">
                <div class="card-title"><i class="fa-solid fa-chart-pie"></i> Resumo Financeiro & Operacional</div>
                <div class="grid-4">
                    <div class="stat-box"><div>Vendas Totais</div><div class="stat-val" id="dashSales">R$ 0,00</div></div>
                    <div class="stat-box"><div>Lucro Bruto</div><div class="stat-val" id="dashProfit">R$ 0,00</div></div>
                    <div class="stat-box"><div>OS em Aberto</div><div class="stat-val" id="dashOS">0</div></div>
                    <div class="stat-box"><div>Produtos Estoque Baixo</div><div class="stat-val" id="dashLowStock">0</div></div>
                </div>
            </section>
        </main>
    </div>

    <script>
        async function loadDashboard() {
            const res = await fetch('/api/dashboard/stats');
            if (res.ok) {
                const data = await res.json();
                document.getElementById('dashSales').innerText = 'R$ ' + data.gross_revenue.toFixed(2);
                document.getElementById('dashProfit').innerText = 'R$ ' + data.gross_profit.toFixed(2);
                document.getElementById('dashOS').innerText = data.open_os + data.approved_os + data.repair_os;
                document.getElementById('dashLowStock').innerText = data.low_stock_count;
            }
        }
        function logout() { document.cookie = "session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; location.reload(); }
        window.onload = loadDashboard;
    </script>
</body>
</html>
"""
}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Estrutura KV CELL gerada com sucesso!")
