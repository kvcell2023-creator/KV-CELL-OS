import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "uploads"), exist_ok=True)

LAGOS_DB_PATH = os.environ.get("DATABASE_PATH_LAGOS", os.path.join(DATA_DIR, "kvcell_lagos.db"))
MAGE_DB_PATH = os.environ.get("DATABASE_PATH_MAGE", os.path.join(DATA_DIR, "kvcell_mage.db"))

engine_lagos = create_engine(f"sqlite:///{LAGOS_DB_PATH}", connect_args={"check_same_thread": False})
engine_mage = create_engine(f"sqlite:///{MAGE_DB_PATH}", connect_args={"check_same_thread": False})

SessionLagos = sessionmaker(autocommit=False, autoflush=False, bind=engine_lagos)
SessionMage = sessionmaker(autocommit=False, autoflush=False, bind=engine_mage)

Base = declarative_base()

def get_db_engine(unit: str):
    if unit == "KVCELLMAGE":
        return engine_mage, SessionMage
    return engine_lagos, SessionLagos

def init_db():
    Base.metadata.create_all(bind=engine_lagos)
    Base.metadata.create_all(bind=engine_mage)
