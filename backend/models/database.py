import os
import hashlib
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_data(data: str) -> str:
    if not data:
        return ""
    return hashlib.sha256(data.encode()).hexdigest()

class ProfileCheck(Base):
    __tablename__ = "profile_checks"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    hashed_username = Column(String(64), index=True, nullable=False)
    overall_risk_score = Column(Float, nullable=False)
    risk_breakdown = Column(JSON, nullable=True)
    rhythm_score = Column(Float, nullable=True)
    cluster_flag = Column(Boolean, default=False)
    checked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    reports = relationship("Report", back_populates="profile_check")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    profile_check_id = Column(Integer, ForeignKey("profile_checks.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    profile_check = relationship("ProfileCheck", back_populates="reports")

def init_db():
    Base.metadata.create_all(bind=engine)