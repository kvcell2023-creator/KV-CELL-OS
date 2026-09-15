import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="operator")  # admin, manager, operator, technician
    unit = Column(String(20), nullable=False)  # KVCELLLAGOS, KVCELLMAGE, KVCELL
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), index=True, nullable=False)
    cpf_cnpj = Column(String(20), index=True, nullable=True)
    phone = Column(String(20), index=True, nullable=False)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(80), nullable=True)
    state = Column(String(2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), index=True, nullable=False)
    imei1 = Column(String(30), index=True, nullable=True)
    imei2 = Column(String(30), index=True, nullable=True)
    serial = Column(String(50), index=True, nullable=True)
    color = Column(String(30), nullable=True)
    storage = Column(String(30), nullable=True)
    condition = Column(String(100), nullable=True)
    accessories = Column(String(200), nullable=True)
    password_hint = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Technician(Base):
    __tablename__ = "technicians"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    commission_percent = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    sku = Column(String(50), index=True, nullable=True)
    barcode = Column(String(50), index=True, nullable=True)
    category = Column(String(50), nullable=False, default="Acessórios")
    brand = Column(String(50), nullable=True)
    quantity = Column(Integer, default=0, nullable=False)
    min_quantity = Column(Integer, default=2, nullable=False)
    cost_price = Column(Float, default=0.0, nullable=False)
    sale_price = Column(Float, default=0.0, nullable=False)
    supplier_name = Column(String(100), nullable=True)
    warranty_days = Column(Integer, default=90)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    type = Column(String(30), nullable=False)  # PURCHASE, SALE, OS_CONSUMPTION, MANUAL_ENTRY, MANUAL_REMOVAL, ADJUSTMENT, RETURN, LOSS, TRANSFER
    reason = Column(String(200), nullable=True)
    unit_cost = Column(Float, default=0.0)
    user_name = Column(String(80), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    supplier_name = Column(String(100), nullable=True)
    os_id = Column(Integer, nullable=True)
    sale_id = Column(Integer, nullable=True)

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), index=True, nullable=False)
    cpf_cnpj = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    contact = Column(String(80), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(80), nullable=True)
    state = Column(String(2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier_name = Column(String(120), nullable=False)
    part_name = Column(String(150), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_cost = Column(Float, nullable=False)
    freight_cost = Column(Float, default=0.0, nullable=False)
    is_pickup = Column(Boolean, default=False)
    total_cost = Column(Float, nullable=False)  # quantity * unit_cost + freight_cost
    purchase_date = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    invoice_ref = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    linked_os_id = Column(Integer, nullable=True)
    user_name = Column(String(80), nullable=False)

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    os_number = Column(String(30), unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client_name = Column(String(120), nullable=False)
    client_phone = Column(String(20), nullable=False)
    device_name = Column(String(120), nullable=False)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    technician_name = Column(String(100), nullable=True)
    status = Column(String(30), default="ENTRY", index=True)  # ENTRY, QUOTE, WAITING_APPROVAL, APPROVED, IN_REPAIR, WAITING_PART, READY, DELIVERED, WARRANTY
    entry_date = Column(DateTime, default=datetime.datetime.utcnow)
    expected_date = Column(DateTime, nullable=True)
    defect_reported = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    password_hint = Column(String(100), nullable=True)
    imei = Column(String(30), index=True, nullable=True)
    serial = Column(String(50), index=True, nullable=True)
    condition = Column(String(150), nullable=True)
    observations = Column(Text, nullable=True)
    quote_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    warranty_days = Column(Integer, default=90)
    payment_status = Column(String(20), default="PENDING")  # PENDING, PAID

class WorkOrderItem(Base):
    __tablename__ = "work_order_items"
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    type = Column(String(20), nullable=False)  # SERVICE or PART
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    total_cost = Column(Float, default=0.0)

class WorkOrderPhoto(Base):
    __tablename__ = "work_order_photos"
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    filename = Column(String(200), nullable=False)
    filepath = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(30), unique=True, index=True)
    client_name = Column(String(120), nullable=False)
    client_phone = Column(String(20), nullable=False)
    device_summary = Column(String(150), nullable=False)
    services_parts_json = Column(Text, nullable=False)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    validity_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, SENT, APPROVED, REJECTED, EXPIRED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    sale_number = Column(String(30), unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client_name = Column(String(120), default="Cliente Avulso")
    total_amount = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    gross_profit = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    payment_method = Column(String(30), nullable=False)  # PIX, CASH, DEBIT, CREDIT, TRANSFER, FIADO
    status = Column(String(20), default="COMPLETED")  # COMPLETED, CANCELLED
    user_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

class PhoneTrade(Base):
    __tablename__ = "phone_trades"
    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(10), default="BUY")  # BUY or SELL
    brand = Column(String(50), nullable=False)
    model = Column(String(100), index=True, nullable=False)
    imei = Column(String(30), index=True, nullable=True)
    serial = Column(String(50), nullable=True)
    storage = Column(String(30), nullable=True)
    color = Column(String(30), nullable=True)
    condition = Column(String(100), nullable=True)
    defects = Column(Text, nullable=True)
    replaced_parts = Column(Text, nullable=True)
    purchase_price = Column(Float, default=0.0)
    repair_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    other_costs = Column(Float, default=0.0)
    freight_cost = Column(Float, default=0.0)
    total_investment = Column(Float, nullable=False)  # sum of costs
    market_min = Column(Float, default=0.0)
    market_max = Column(Float, default=0.0)
    market_avg = Column(Float, default=0.0)
    recommended_price = Column(Float, default=0.0)
    actual_sale_price = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    status = Column(String(30), default="IN_REPAIR")  # IN_REPAIR, READY_FOR_SALE, SOLD
    supplier_source = Column(String(100), nullable=True)
    customer_buyer = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CashMovement(Base):
    __tablename__ = "cash_movements"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # OPENING, IN, OUT, SALE, EXPENSE, ADJUSTMENT, CLOSING
    amount = Column(Float, nullable=False)
    description = Column(String(200), nullable=False)
    payment_method = Column(String(30), nullable=True)
    user_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # PAYABLE or RECEIVABLE
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    client_name = Column(String(120), nullable=True)
    supplier_name = Column(String(120), nullable=True)
    status = Column(String(20), default="OPEN", index=True)  # OPEN, PAID, CANCELLED, OVERDUE
    payment_date = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=False, default="Geral")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class WarrantyRecord(Base):
    __tablename__ = "warranties"
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    client_name = Column(String(120), nullable=False)
    device_summary = Column(String(150), nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    warranty_days = Column(Integer, default=90)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, EXPIRED, CANCELLED
    notes = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(80), nullable=False)
    action = Column(String(50), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    details = Column(Text, nullable=True)
