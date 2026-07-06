"""
Intelligent Negotiation Letter Generation (Scenario 2) and AI interaction
history endpoints.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.services.gemini_service import generate_negotiation_content

router = APIRouter(prefix="/api/ai", tags=["AI Negotiation & History"])


@router.post("/negotiate", response_model=schemas.AINegotiationOut, status_code=status.HTTP_201_CREATED)
def generate_negotiation(
    payload: schemas.NegotiationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    loan = db.query(models.Loan).filter(
        models.Loan.loan_id == payload.loan_id, models.Loan.user_id == current_user.user_id
    ).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

    profile = db.query(models.FinancialProfile).filter(
        models.FinancialProfile.user_id == current_user.user_id
    ).first()

    latest_prediction = db.query(models.SettlementPrediction).filter(
        models.SettlementPrediction.loan_id == loan.loan_id
    ).order_by(models.SettlementPrediction.created_at.desc()).first()

    recommended_amount = (
        latest_prediction.recommended_amount if latest_prediction else loan.outstanding_amount
    )

    context = {
        "lender_name": loan.lender_name,
        "loan_type": loan.loan_type,
        "outstanding_amount": loan.outstanding_amount,
        "overdue_months": loan.overdue_months,
        "monthly_surplus": profile.monthly_surplus if profile else 0.0,
        "recommended_amount": recommended_amount,
        "stress_level": profile.stress_level if profile else "Low",
    }

    content = generate_negotiation_content(context, tone=payload.tone or "professional")

    negotiation = models.AINegotiation(
        loan_id=loan.loan_id,
        user_id=current_user.user_id,
        negotiation_strategy=content.negotiation_strategy,
        negotiation_letter=content.negotiation_letter,
    )
    db.add(negotiation)

    history = models.AIHistory(
        user_id=current_user.user_id,
        query_type="negotiation_letter",
        generated_content=(
            f"Negotiation generated for loan #{loan.loan_id} ({loan.lender_name}) "
            f"via {content.source}."
        ),
    )
    db.add(history)

    db.commit()
    db.refresh(negotiation)
    return negotiation


@router.get("/negotiations", response_model=List[schemas.AINegotiationOut])
def list_negotiations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.AINegotiation).filter(
        models.AINegotiation.user_id == current_user.user_id
    ).order_by(models.AINegotiation.generated_at.desc()).all()


@router.get("/history", response_model=List[schemas.AIHistoryOut])
def list_ai_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.AIHistory).filter(
        models.AIHistory.user_id == current_user.user_id
    ).order_by(models.AIHistory.timestamp.desc()).all()
