"""
Settlement prediction listing/filtering endpoints.
Predictions themselves are generated automatically from app/routers/loans.py
whenever a loan is created or updated.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/settlements", tags=["Settlements"])


@router.get("", response_model=List[schemas.SettlementPredictionOut])
def list_settlements(
    priority: Optional[str] = Query(default=None, description="Filter by High/Medium/Low"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.SettlementPrediction).filter(
        models.SettlementPrediction.user_id == current_user.user_id
    )
    if priority:
        query = query.filter(models.SettlementPrediction.priority_level == priority)

    return query.order_by(models.SettlementPrediction.created_at.desc()).all()
