"""
Authentication endpoints: register, login (OAuth2 password flow -> JWT),
and fetching the current logged-in user's profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        monthly_income=payload.monthly_income,
        monthly_expenses=payload.monthly_expenses,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Seed an empty financial profile so it always exists for the user.
    profile = models.FinancialProfile(
        user_id=user.user_id,
        monthly_income=payload.monthly_income,
        monthly_expenses=payload.monthly_expenses,
    )
    db.add(profile)
    db.commit()

    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.user_id)})
    return schemas.Token(access_token=token, user=user)


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
