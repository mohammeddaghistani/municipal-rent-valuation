from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
from modules.utils import now_iso

DB_PATH = Path("data/app.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="valuer")
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=now_iso)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True)
    activity = Column(String, nullable=False)
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    area_m2 = Column(Float, nullable=False, default=0.0)
    annual_rent = Column(Float, nullable=False, default=0.0)
    year = Column(Integer, nullable=False, default=2024)
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=now_iso)
    updated_at = Column(String, default=now_iso)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True)
    activity = Column(String, nullable=False)
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    area_m2 = Column(Float, nullable=False, default=0.0)
    contract_years = Column(Integer, nullable=False, default=10)
    method_used = Column(String, nullable=False, default="income")
    recommended_annual_rent = Column(Float, nullable=False, default=0.0)
    min_annual_rent = Column(Float, nullable=False, default=0.0)
    max_annual_rent = Column(Float, nullable=False, default=0.0)
    confidence_pct = Column(Float, nullable=False, default=0.0)
    confidence_label = Column(String, nullable=False, default="منخفضة")
    explanation = Column(Text, nullable=True)
    croquis_path = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(String, default=now_iso)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
