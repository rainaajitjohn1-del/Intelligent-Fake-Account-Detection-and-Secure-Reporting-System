from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProfileCheck(Base):
    __tablename__ = "profile_checks"

    id = Column(Integer, primary_key=True, index=True)
    profile_url = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0)
    status = Column(String, default="not yet analyzed")
    checked_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    profile_url = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)