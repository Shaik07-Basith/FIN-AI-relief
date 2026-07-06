"""
Pydantic schemas used for request validation and response serialization.
Kept separate from the ORM models (app/models.py) on purpose.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    monthly_income: float
    monthly_expenses: float
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Financial Profile ----------

class FinancialProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: int
    user_id: int
    monthly_income: float
    monthly_expenses: float
    existing_debts: float
    emi_ratio: float
    dti_ratio: float
    monthly_surplus: float
    stress_level: str
    financial_health_score: float
    updated_at: datetime


class FinancialProfileUpdate(BaseModel):
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    existing_debts: Optional[float] = None


# ---------- Loans ----------

class LoanCreate(BaseModel):
    lender_name: str = Field(min_length=1, max_length=120)
    loan_type: str = Field(min_length=1, max_length=60)
    loan_amount: float = Field(gt=0)
    outstanding_amount: float = Field(ge=0)
    interest_rate: float = Field(ge=0, default=0.0)
    emi: float = Field(ge=0, default=0.0)
    overdue_months: int = Field(ge=0, default=0)
    due_date: Optional[datetime] = None


class LoanUpdate(BaseModel):
    lender_name: Optional[str] = None
    loan_type: Optional[str] = None
    loan_amount: Optional[float] = None
    outstanding_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    emi: Optional[float] = None
    overdue_months: Optional[int] = None
    due_date: Optional[datetime] = None


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_id: int
    user_id: int
    lender_name: str
    loan_type: str
    loan_amount: float
    outstanding_amount: float
    interest_rate: float
    emi: float
    overdue_months: int
    due_date: Optional[datetime]
    created_at: datetime


# ---------- Settlement Prediction ----------

class SettlementPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    settlement_id: int
    user_id: int
    loan_id: int
    settlement_prediction: str
    recommended_amount: float
    risk_category: str
    priority_level: str
    created_at: datetime


# ---------- AI Negotiation ----------

class NegotiationRequest(BaseModel):
    loan_id: int
    tone: Optional[str] = "professional"  # professional | firm | empathetic


class AINegotiationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ai_id: int
    loan_id: int
    user_id: int
    negotiation_strategy: str
    negotiation_letter: str
    generated_at: datetime


# ---------- AI History ----------

class AIHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    history_id: int
    user_id: int
    generated_content: str
    query_type: str
    timestamp: datetime


# ---------- Dashboard ----------

class DashboardSummary(BaseModel):
    total_outstanding: float
    total_emi: float
    monthly_surplus: float
    emi_ratio: float
    dti_ratio: float
    stress_level: str
    financial_health_score: float
    total_loans: int
    high_priority_loans: int
