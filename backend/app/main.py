"""
FinRelief AI Application Development & System Setup (Epic 1)

Main FastAPI application entrypoint. Wires up CORS, creates database tables
on startup, and registers all routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, loans, financial_profile, settlements, ai_history

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinRelief AI",
    description=(
        "AI Powered Debt Relief & Financial Recovery Platform API. "
        "Provides loan management, financial health analysis, settlement "
        "prediction, and Gemini-powered negotiation letter generation."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(financial_profile.router)
app.include_router(settlements.router)
app.include_router(ai_history.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "FinRelief AI API"}


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
