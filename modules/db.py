from pathlib import Path

from sqlalchemy import Boolean, Column, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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


class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True)
    yield_rate_pct = Column(Float, nullable=False, default=8.0)  # نسبة العائد
    grace_period_years = Column(Float, nullable=False, default=0.0)  # فترة السماح
    rent_to_sale_pct = Column(Float, nullable=False, default=5.0)  # نسبة الإيجار من قيمة البيع
    updated_at = Column(String, default=now_iso)


def init_db():
    Base.metadata.create_all(engine)


def ensure_settings():
    """Ensure there is always a singleton settings row."""
    init_db()
    db = SessionLocal()
    try:
        row = db.query(AppSettings).filter(AppSettings.id == 1).first()
        if not row:
            db.add(AppSettings(id=1, yield_rate_pct=8.0, grace_period_years=0.0, rent_to_sale_pct=5.0, updated_at=now_iso()))
            db.commit()
    finally:
        db.close()


def get_settings() -> AppSettings:
    ensure_settings()
    db = SessionLocal()
    try:
        row = db.query(AppSettings).filter(AppSettings.id == 1).first()
        return row
    finally:
        db.close()
