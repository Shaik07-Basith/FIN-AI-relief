"""
Loan management endpoints (Scenario 1: AI-Powered Settlement Recommendation).

Creating or updating a loan automatically recalculates the borrower's
financial profile and generates a fresh settlement prediction for that loan.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.services.financial_service import compute_financial_health, predict_settlement

router = APIRouter(prefix="/api/loans", tags=["Loans"])


def _recalculate_financial_profile(db: Session, user: models.User) -> models.FinancialProfile:
    loans = db.query(models.Loan).filter(models.Loan.user_id == user.user_id).all()
    total_emi = sum(loan.emi for loan in loans)
    total_outstanding = sum(loan.outstanding_amount for loan in loans)

    result = compute_financial_health(
        monthly_income=user.monthly_income,
        monthly_expenses=user.monthly_expenses,
        total_emi=total_emi,
        existing_debts=total_outstanding,
    )

    profile = db.query(models.FinancialProfile).filter(
        models.FinancialProfile.user_id == user.user_id
    ).first()
    if not profile:
        profile = models.FinancialProfile(user_id=user.user_id)
        db.add(profile)

    profile.monthly_income = user.monthly_income
    profile.monthly_expenses = user.monthly_expenses
    profile.existing_debts = total_outstanding
    profile.emi_ratio = result.emi_ratio
    profile.dti_ratio = result.dti_ratio
    profile.monthly_surplus = result.monthly_surplus
    profile.stress_level = result.stress_level
    profile.financial_health_score = result.financial_health_score

    db.commit()
    db.refresh(profile)
    return profile


def _generate_settlement_prediction(
    db: Session, user: models.User, loan: models.Loan, profile: models.FinancialProfile
) -> models.SettlementPrediction:
    result = predict_settlement(
        outstanding_amount=loan.outstanding_amount,
        overdue_months=loan.overdue_months,
        monthly_surplus=profile.monthly_surplus,
        financial_health_score=profile.financial_health_score,
    )

    prediction = models.SettlementPrediction(
        user_id=user.user_id,
        loan_id=loan.loan_id,
        settlement_prediction=result.settlement_prediction,
        recommended_amount=result.recommended_amount,
        risk_category=result.risk_category,
        priority_level=result.priority_level,
    )
    db.add(prediction)

    history = models.AIHistory(
        user_id=user.user_id,
        query_type="settlement_prediction",
        generated_content=(
            f"Loan #{loan.loan_id} ({loan.lender_name}): prediction={result.settlement_prediction}, "
            f"recommended_amount={result.recommended_amount}, risk={result.risk_category}"
        ),
    )
    db.add(history)

    db.commit()
    db.refresh(prediction)
    return prediction


def _get_owned_loan(db: Session, user: models.User, loan_id: int) -> models.Loan:
    loan = db.query(models.Loan).filter(
        models.Loan.loan_id == loan_id, models.Loan.user_id == user.user_id
    ).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@router.post("", response_model=schemas.LoanOut, status_code=status.HTTP_201_CREATED)
def create_loan(
    payload: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    loan = models.Loan(user_id=current_user.user_id, **payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)

    profile = _recalculate_financial_profile(db, current_user)
    _generate_settlement_prediction(db, current_user, loan, profile)

    return loan


@router.get("", response_model=List[schemas.LoanOut])
def list_loans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id).all()


@router.get("/{loan_id}", response_model=schemas.LoanOut)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return _get_owned_loan(db, current_user, loan_id)


@router.put("/{loan_id}", response_model=schemas.LoanOut)
def update_loan(
    loan_id: int,
    payload: schemas.LoanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    loan = _get_owned_loan(db, current_user, loan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)
    db.commit()
    db.refresh(loan)

    profile = _recalculate_financial_profile(db, current_user)
    _generate_settlement_prediction(db, current_user, loan, profile)

    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    loan = _get_owned_loan(db, current_user, loan_id)
    db.delete(loan)
    db.commit()
    _recalculate_financial_profile(db, current_user)
    return None


@router.get("/{loan_id}/settlements", response_model=List[schemas.SettlementPredictionOut])
def get_loan_settlements(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_owned_loan(db, current_user, loan_id)
    return db.query(models.SettlementPrediction).filter(
        models.SettlementPrediction.loan_id == loan_id
    ).order_by(models.SettlementPrediction.created_at.desc()).all()
