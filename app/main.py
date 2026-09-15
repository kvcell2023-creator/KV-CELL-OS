import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, get_db_engine
from app.auth import bootstrap_initial_users, hash_password, verify_password, create_session_token, get_current_user
from app.models import User, Product, WorkOrder, Sale, Purchase, CashMovement, FinancialRecord

app = FastAPI(title="KV CELL PDV ERP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.on_event("startup")
def startup_event():
    init_db()
    bootstrap_initial_users()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "KV CELL PDV ERP",
        "version": "1.0.0",
        "databases": {
            "lagos": os.path.exists(os.path.join("data", "kvcell_lagos.db")),
            "mage": os.path.exists(os.path.join("data", "kvcell_mage.db"))
        },
        "uploads_dir": os.path.exists(UPLOADS_DIR)
    }

# Auth Endpoint
@app.post("/api/auth/login")
async def login(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if username == "KVCELL" and password == "2023":
        token = create_session_token("KVCELL", "KVCELL", "admin")
        response = JSONResponse({
            "success": True,
            "token": token,
            "username": "KVCELL",
            "unit": "KVCELL",
            "role": "admin",
            "name": "Administrador Global KV CELL"
        })
        response.set_cookie(key="session_token", value=token, httponly=True)
        return response

    unit_target = "KVCELLMAGE" if username == "KVCELLMAGE" else "KVCELLLAGOS"
    engine, SessionLocal = get_db_engine(unit_target)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            token = create_session_token(user.username, user.unit, user.role)
            response = JSONResponse({
                "success": True,
                "token": token,
                "username": user.username,
                "unit": user.unit,
                "role": user.role,
                "name": user.name
            })
            response.set_cookie(key="session_token", value=token, httponly=True)
            return response
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    finally:
        db.close()

# Main Dashboard API (Real Data)
@app.get("/api/dashboard/stats")
def get_dashboard_stats(user: dict = Depends(get_current_user)):
    units_to_query = ["KVCELLLAGOS", "KVCELLMAGE"] if user["unit"] == "KVCELL" else [user["unit"]]
    
    aggregated = {
        "today_sales": 0.0,
        "month_sales": 0.0,
        "today_purchases": 0.0,
        "freight_total": 0.0,
        "gross_revenue": 0.0,
        "gross_cost": 0.0,
        "gross_profit": 0.0,
        "open_os": 0,
        "approved_os": 0,
        "repair_os": 0,
        "ready_os": 0,
        "low_stock_count": 0,
        "accounts_payable": 0.0,
        "accounts_receivable": 0.0,
        "cash_balance": 0.0,
        "by_unit": {}
    }

    for unit in units_to_query:
        engine, SessionLocal = get_db_engine(unit)
        db = SessionLocal()
        try:
            sales = db.query(Sale).filter(Sale.status == "COMPLETED").all()
            unit_sales = sum(s.total_amount for s in sales)
            unit_cost = sum(s.total_cost for s in sales)
            unit_profit = sum(s.gross_profit for s in sales)
            
            purchases = db.query(Purchase).all()
            unit_purchases = sum(p.total_cost for p in purchases)
            unit_freight = sum(p.freight_cost for p in purchases)

            open_os = db.query(WorkOrder).filter(WorkOrder.status.in_(["ENTRY", "QUOTE", "WAITING_APPROVAL"])).count()
            approved_os = db.query(WorkOrder).filter(WorkOrder.status == "APPROVED").count()
            repair_os = db.query(WorkOrder).filter(WorkOrder.status.in_(["IN_REPAIR", "WAITING_PART"])).count()
            ready_os = db.query(WorkOrder).filter(WorkOrder.status == "READY").count()

            low_stock = db.query(Product).filter(Product.quantity <= Product.min_quantity, Product.is_active == True).count()
            
            payables = db.query(FinancialRecord).filter(FinancialRecord.type == "PAYABLE", FinancialRecord.status == "OPEN").all()
            receivables = db.query(FinancialRecord).filter(FinancialRecord.type == "RECEIVABLE", FinancialRecord.status == "OPEN").all()
            
            unit_pay = sum(p.amount for p in payables)
            unit_rec = sum(r.amount for r in receivables)

            cash_movs = db.query(CashMovement).all()
            unit_cash = sum(c.amount if c.type in ["OPENING", "IN", "SALE"] else -c.amount for c in cash_movs)

            aggregated["today_sales"] += unit_sales
            aggregated["month_sales"] += unit_sales
            aggregated["today_purchases"] += unit_purchases
            aggregated["freight_total"] += unit_freight
            aggregated["gross_revenue"] += unit_sales
            aggregated["gross_cost"] += unit_cost
            aggregated["gross_profit"] += unit_profit
            aggregated["open_os"] += open_os
            aggregated["approved_os"] += approved_os
            aggregated["repair_os"] += repair_os
            aggregated["ready_os"] += ready_os
            aggregated["low_stock_count"] += low_stock
            aggregated["accounts_payable"] += unit_pay
            aggregated["accounts_receivable"] += unit_rec
            aggregated["cash_balance"] += unit_cash

            aggregated["by_unit"][unit] = {
                "sales": unit_sales,
                "profit": unit_profit,
                "purchases": unit_purchases,
                "open_os": open_os + approved_os + repair_os
            }
        finally:
            db.close()

    return aggregated

# Single Page App Fallback
@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>KV CELL PDV ERP Rodando</h1>"
