
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3, os
from datetime import datetime

app=FastAPI(title="KV CELL PDV")
templates=Jinja2Templates(directory="app/templates")
DB="data/kvcell.db"
os.makedirs("data",exist_ok=True)

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def now(): return datetime.now().isoformat(timespec="seconds")
def init():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS suppliers(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,phone TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,phone TEXT,document TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,customer_id INTEGER NOT NULL,status TEXT DEFAULT 'ORÇAMENTO',description TEXT,labor REAL DEFAULT 0,sale_total REAL DEFAULT 0,created_at TEXT);
    CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT,supplier_id INTEGER NOT NULL,part_name TEXT NOT NULL,quantity REAL DEFAULT 1,unit_cost REAL NOT NULL,freight REAL DEFAULT 0,delivery_mode TEXT NOT NULL,order_id INTEGER,notes TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY AUTOINCREMENT,customer_id INTEGER,order_id INTEGER,total REAL NOT NULL,payment TEXT NOT NULL,created_at TEXT);
    CREATE TABLE IF NOT EXISTS cash(id INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT,description TEXT,amount REAL,created_at TEXT);
    """); c.commit(); c.close()
init()

def money(x): return max(0,float(x or 0))

@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    c=db()
    s={
    "customers":c.execute("select count(*) n from customers").fetchone()["n"],
    "orders":c.execute("select count(*) n from orders").fetchone()["n"],
    "purchases":c.execute("select count(*) n from purchases").fetchone()["n"],
    "revenue":c.execute("select coalesce(sum(total),0) n from sales").fetchone()["n"],
    "cost":c.execute("select coalesce(sum(quantity*unit_cost+freight),0) n from purchases").fetchone()["n"]}
    recent=c.execute("""select p.*,s.name supplier from purchases p join suppliers s on s.id=p.supplier_id
    order by p.id desc limit 10""").fetchall(); c.close()
    return templates.TemplateResponse(request,"dashboard.html",{"request":request,**s,"recent":recent})

@app.get("/fornecedores",response_class=HTMLResponse)
def fornecedores(request:Request):
    c=db(); rows=c.execute("select * from suppliers order by name").fetchall(); c.close()
    return templates.TemplateResponse(request,"suppliers.html",{"request":request,"rows":rows})
@app.post("/fornecedores")
def add_fornecedor(name:str=Form(...),phone:str=Form(""),notes:str=Form("")):
    c=db(); c.execute("insert into suppliers(name,phone,notes) values(?,?,?)",(name,phone,notes)); c.commit(); c.close()
    return RedirectResponse("/fornecedores",303)

@app.get("/clientes",response_class=HTMLResponse)
def clientes(request:Request):
    c=db(); rows=c.execute("select * from customers order by name").fetchall(); c.close()
    return templates.TemplateResponse(request,"customers.html",{"request":request,"rows":rows})
@app.post("/clientes")
def add_cliente(name:str=Form(...),phone:str=Form(""),document:str=Form(""),notes:str=Form("")):
    c=db(); c.execute("insert into customers(name,phone,document,notes) values(?,?,?,?)",(name,phone,document,notes)); c.commit(); c.close()
    return RedirectResponse("/clientes",303)

@app.get("/os",response_class=HTMLResponse)
def os_list(request:Request):
    c=db()
    rows=c.execute("""select o.*,c.name customer,
    coalesce((select sum(quantity*unit_cost+freight) from purchases p where p.order_id=o.id),0) part_cost
    from orders o join customers c on c.id=o.customer_id order by o.id desc""").fetchall()
    customers=c.execute("select * from customers order by name").fetchall(); c.close()
    return templates.TemplateResponse(request,"orders.html",{"request":request,"rows":rows,"customers":customers})
@app.post("/os")
def add_os(customer_id:int=Form(...),description:str=Form(...),labor:float=Form(0),sale_total:float=Form(0)):
    c=db(); c.execute("""insert into orders(customer_id,description,labor,sale_total,created_at)
    values(?,?,?,?,?)""",(customer_id,description,money(labor),money(sale_total),now())); c.commit(); c.close()
    return RedirectResponse("/os",303)

@app.get("/os/{oid}",response_class=HTMLResponse)
def os_detail(request:Request,oid:int):
    c=db()
    o=c.execute("""select o.*,c.name customer,c.phone from orders o join customers c on c.id=o.customer_id where o.id=?""",(oid,)).fetchone()
    if not o: c.close(); return HTMLResponse("OS não encontrada",404)
    parts=c.execute("""select p.*,s.name supplier from purchases p join suppliers s on s.id=p.supplier_id
    where p.order_id=? order by p.id desc""",(oid,)).fetchall()
    cost=c.execute("select coalesce(sum(quantity*unit_cost+freight),0) n from purchases where order_id=?",(oid,)).fetchone()["n"]
    c.close()
    return templates.TemplateResponse(request,"order_detail.html",{"request":request,"o":o,"parts":parts,"cost":cost,"profit":money(o["sale_total"])-money(cost)})
@app.post("/os/{oid}/status")
def status(oid:int,status:str=Form(...)):
    allowed={"ORÇAMENTO","AGUARDANDO PEÇA","EM REPARO","PRONTO","ENTREGUE","CANCELADO"}
    if status not in allowed: status="ORÇAMENTO"
    c=db(); c.execute("update orders set status=? where id=?",(status,oid)); c.commit(); c.close()
    return RedirectResponse(f"/os/{oid}",303)

@app.get("/compras",response_class=HTMLResponse)
def compras(request:Request):
    c=db()
    rows=c.execute("""select p.*,s.name supplier from purchases p join suppliers s on s.id=p.supplier_id
    order by p.id desc""").fetchall()
    suppliers=c.execute("select * from suppliers order by name").fetchall()
    orders=c.execute("""select o.id,o.description,c.name customer from orders o join customers c on c.id=o.customer_id
    order by o.id desc""").fetchall(); c.close()
    return templates.TemplateResponse(request,"purchases.html",{"request":request,"rows":rows,"suppliers":suppliers,"orders":orders})
@app.post("/compras")
def add_compra(supplier_id:int=Form(...),part_name:str=Form(...),quantity:float=Form(1),
               unit_cost:float=Form(...),delivery_mode:str=Form(...),freight:float=Form(0),
               order_id:str=Form(""),notes:str=Form("")):
    qty=max(.01,money(quantity)); cost=money(unit_cost)
    freight=0 if delivery_mode=="RETIRADA" else money(freight)
    oid=int(order_id) if order_id else None
    c=db(); c.execute("""insert into purchases(supplier_id,part_name,quantity,unit_cost,freight,delivery_mode,order_id,notes,created_at)
    values(?,?,?,?,?,?,?,?,?)""",(supplier_id,part_name,qty,cost,freight,delivery_mode,oid,notes,now()))
    c.commit(); c.close(); return RedirectResponse("/compras",303)

@app.get("/pdv",response_class=HTMLResponse)
def pdv(request:Request):
    c=db(); customers=c.execute("select * from customers order by name").fetchall()
    orders=c.execute("""select o.id,o.sale_total,c.name customer from orders o join customers c on c.id=o.customer_id
    where o.status!='CANCELADO' order by o.id desc""").fetchall(); c.close()
    return templates.TemplateResponse(request,"pdv.html",{"request":request,"customers":customers,"orders":orders})
@app.post("/pdv")
def venda(customer_id:str=Form(""),order_id:str=Form(""),total:float=Form(...),payment:str=Form(...)):
    cid=int(customer_id) if customer_id else None; oid=int(order_id) if order_id else None; total=money(total); t=now()
    c=db(); c.execute("insert into sales(customer_id,order_id,total,payment,created_at) values(?,?,?,?,?)",(cid,oid,total,payment,t))
    c.execute("insert into cash(type,description,amount,created_at) values(?,?,?,?)",("ENTRADA","Venda PDV",total,t))
    if oid: c.execute("update orders set status='ENTREGUE' where id=?",(oid,))
    c.commit(); c.close(); return RedirectResponse("/pdv?ok=1",303)

@app.get("/relatorios",response_class=HTMLResponse)
def relatorios(request:Request):
    c=db(); revenue=c.execute("select coalesce(sum(total),0)n from sales").fetchone()["n"]
    cost=c.execute("select coalesce(sum(quantity*unit_cost+freight),0)n from purchases").fetchone()["n"]
    labor=c.execute("select coalesce(sum(labor),0)n from orders").fetchone()["n"]
    data=c.execute("""select o.id,c.name customer,o.status,o.sale_total,
    coalesce((select sum(quantity*unit_cost+freight) from purchases p where p.order_id=o.id),0) part_cost
    from orders o join customers c on c.id=o.customer_id order by o.id desc""").fetchall(); c.close()
    return templates.TemplateResponse(request,"reports.html",{"request":request,"revenue":revenue,"cost":cost,"labor":labor,"data":data})
