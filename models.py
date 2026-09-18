import hashlib
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base

def hash_data(data: str) -> str:
    """Privacy: Hashes usernames/handles so plain-text PII is not stored."""
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