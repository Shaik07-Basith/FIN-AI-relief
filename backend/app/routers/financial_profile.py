"""
Financial profile & dashboard endpoints
(Scenario 3: Financial Health Tracking & Loan Analysis).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.services.financial_service import compute_financial_health, rank_loans_by_priority

router = APIRouter(prefix="/api/financial-profile", tags=["Financial Profile"])


@router.get("", response_model=schemas.FinancialProfileOut)
def get_financial_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    profile = db.query(models.FinancialProfile).filter(
        models.FinancialProfile.user_id == current_user.user_id
    ).first()
    if not profile:
        profile = models.FinancialProfile(user_id=current_user.user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=schemas.FinancialProfileOut)
def update_financial_profile(
    payload: schemas.FinancialProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.monthly_income is not None:
        current_user.monthly_income = payload.monthly_income
    if payload.monthly_expenses is not None:
        current_user.monthly_expenses = payload.monthly_expenses
    db.commit()

    loans = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id).all()
    total_emi = sum(loan.emi for loan in loans)
    existing_debts = (
        payload.existing_debts
        if payload.existing_debts is not None
        else sum(loan.outstanding_amount for loan in loans)
    )

    result = compute_financial_health(
        monthly_income=current_user.monthly_income,
        monthly_expenses=current_user.monthly_expenses,
        total_emi=total_emi,
        existing_debts=existing_debts,
    )

    profile = db.query(models.FinancialProfile).filter(
        models.FinancialProfile.user_id == current_user.user_id
    ).first()
    if not profile:
        profile = models.FinancialProfile(user_id=current_user.user_id)
        db.add(profile)

    profile.monthly_income = current_user.monthly_income
    profile.monthly_expenses = current_user.monthly_expenses
    profile.existing_debts = existing_debts
    profile.emi_ratio = result.emi_ratio
    profile.dti_ratio = result.dti_ratio
    profile.monthly_surplus = result.monthly_surplus
    profile.stress_level = result.stress_level
    profile.financial_health_score = result.financial_health_score

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    loans = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id).all()
    profile = db.query(models.FinancialProfile).filter(
        models.FinancialProfile.user_id == current_user.user_id
    ).first()

    ranked = rank_loans_by_priority(loans)
    high_priority_count = sum(1 for loan in ranked if loan.overdue_months >= 6)

    return schemas.DashboardSummary(
        total_outstanding=round(sum(loan.outstanding_amount for loan in loans), 2),
        total_emi=round(sum(loan.emi for loan in loans), 2),
        monthly_surplus=profile.monthly_surplus if profile else 0.0,
        emi_ratio=profile.emi_ratio if profile else 0.0,
        dti_ratio=profile.dti_ratio if profile else 0.0,
        stress_level=profile.stress_level if profile else "Low",
        financial_health_score=profile.financial_health_score if profile else 0.0,
        total_loans=len(loans),
        high_priority_loans=high_priority_count,
    )
