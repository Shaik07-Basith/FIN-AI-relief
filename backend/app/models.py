"""
Database Management & Financial Data Storage Setup (Epic 3)

SQLAlchemy ORM models implementing the FinRelief AI ER diagram:

    Users (1) ----- (1) Financial_Profile
    Users (1) ----- (N) Loans
    Users (1) ----- (N) AI_History
    Loans (1) ----- (N) Settlement_Prediction
    Loans (1) ----- (N) AI_Negotiation
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # bcrypt hash, never plaintext
    monthly_income = Column(Float, default=0.0)
    monthly_expenses = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)

    loans = relationship("Loan", back_populates="owner", cascade="all, delete-orphan")
    financial_profile = relationship(
        "FinancialProfile", back_populates="owner", uselist=False,
        cascade="all, delete-orphan"
    )
    ai_history = relationship("AIHistory", back_populates="owner", cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)

    monthly_income = Column(Float, default=0.0)
    monthly_expenses = Column(Float, default=0.0)
    existing_debts = Column(Float, default=0.0)

    emi_ratio = Column(Float, default=0.0)
    dti_ratio = Column(Float, default=0.0)
    monthly_surplus = Column(Float, default=0.0)
    stress_level = Column(String(20), default="Low")
    financial_health_score = Column(Float, default=0.0)

    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="financial_profile")


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    lender_name = Column(String(120), nullable=False)
    loan_type = Column(String(60), nullable=False)
    loan_amount = Column(Float, nullable=False)
    outstanding_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0)
    emi = Column(Float, default=0.0)
    overdue_months = Column(Integer, default=0)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="loans")
    settlement_predictions = relationship(
        "SettlementPrediction", back_populates="loan", cascade="all, delete-orphan"
    )
    ai_negotiations = relationship(
        "AINegotiation", back_populates="loan", cascade="all, delete-orphan"
    )


class SettlementPrediction(Base):
    __tablename__ = "settlement_predictions"

    settlement_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)

    settlement_prediction = Column(String(60), nullable=False)   # e.g. "Likely", "Possible", "Unlikely"
    recommended_amount = Column(Float, nullable=False)
    risk_category = Column(String(20), nullable=False)           # High / Medium / Low
    priority_level = Column(String(20), nullable=False)          # High / Medium / Low
    created_at = Column(DateTime, default=utcnow)

    loan = relationship("Loan", back_populates="settlement_predictions")


class AINegotiation(Base):
    __tablename__ = "ai_negotiations"

    ai_id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    negotiation_strategy = Column(Text, nullable=False)
    negotiation_letter = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=utcnow)

    loan = relationship("Loan", back_populates="ai_negotiations")


class AIHistory(Base):
    __tablename__ = "ai_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    generated_content = Column(Text, nullable=False)
    query_type = Column(String(60), nullable=False)  # e.g. "settlement_prediction", "negotiation_letter"
    timestamp = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="ai_history")
