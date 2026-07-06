"""
AI Integration & Financial Processing Setup (Epic 2)

This module holds all the "intelligent decision making" logic that doesn't
require calling out to an external LLM:

- Financial health scoring (EMI ratio, DTI ratio, monthly surplus, stress level)
- Rule-based settlement prediction & recommended settlement amount
- Loan prioritization for the dashboard

Keeping this logic rule-based (rather than only relying on Gemini) means the
platform still produces consistent, explainable financial recommendations
even if the AI_History/AI_Negotiation calls fail or no API key is configured.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass
class FinancialHealthResult:
    emi_ratio: float
    dti_ratio: float
    monthly_surplus: float
    stress_level: str
    financial_health_score: float


def compute_financial_health(
    monthly_income: float,
    monthly_expenses: float,
    total_emi: float,
    existing_debts: float,
) -> FinancialHealthResult:
    """
    EMI Ratio   = total monthly EMI outflow / monthly income
    DTI Ratio   = total outstanding debt balance / annual income
                  (standard "debt-to-annual-income" serviceability metric --
                  comparing a total balance to a single month's income would
                  produce meaningless triple-digit percentages)
    Surplus     = income - expenses - EMI
    Health score (0-100): higher is healthier. Penalizes high EMI/DTI ratios
    and low/negative surplus.
    """
    income = max(monthly_income, 0.01)  # avoid divide-by-zero
    annual_income = income * 12

    emi_ratio = round((total_emi / income) * 100, 2)
    dti_ratio = round((existing_debts / annual_income) * 100, 2)
    monthly_surplus = round(monthly_income - monthly_expenses - total_emi, 2)

    if emi_ratio >= 60 or monthly_surplus < 0:
        stress_level = "High"
    elif emi_ratio >= 35:
        stress_level = "Medium"
    else:
        stress_level = "Low"

    # Weighted score: reward low EMI ratio, low DTI ratio, positive surplus.
    score = 100.0
    score -= min(emi_ratio, 100) * 0.5
    score -= min(dti_ratio, 100) * 0.3
    if monthly_surplus < 0:
        score -= 20
    elif monthly_surplus < income * 0.1:
        score -= 10

    financial_health_score = round(max(0.0, min(100.0, score)), 2)

    return FinancialHealthResult(
        emi_ratio=emi_ratio,
        dti_ratio=dti_ratio,
        monthly_surplus=monthly_surplus,
        stress_level=stress_level,
        financial_health_score=financial_health_score,
    )


@dataclass
class SettlementResult:
    settlement_prediction: str
    recommended_amount: float
    risk_category: str
    priority_level: str


def predict_settlement(
    outstanding_amount: float,
    overdue_months: int,
    monthly_surplus: float,
    financial_health_score: float,
) -> SettlementResult:
    """
    Rule-based settlement prediction used as the platform's core AI-assisted
    recommendation engine. Produces a suggested settlement percentage based
    on overdue duration and the borrower's financial stress.
    """
    # Base settlement discount: more overdue months + weaker financial
    # health => lender more likely to accept a lower settlement.
    if overdue_months >= 12 or financial_health_score < 30:
        discount = 0.55
        risk_category = "High"
        settlement_prediction = "Likely"
    elif overdue_months >= 6 or financial_health_score < 55:
        discount = 0.35
        risk_category = "Medium"
        settlement_prediction = "Possible"
    else:
        discount = 0.15
        risk_category = "Low"
        settlement_prediction = "Unlikely"

    # If the borrower has no surplus at all, nudge the discount slightly
    # higher since repayment capacity is very limited.
    if monthly_surplus < 0:
        discount = min(discount + 0.10, 0.70)

    recommended_amount = round(outstanding_amount * (1 - discount), 2)

    if risk_category == "High":
        priority_level = "High"
    elif risk_category == "Medium":
        priority_level = "Medium"
    else:
        priority_level = "Low"

    return SettlementResult(
        settlement_prediction=settlement_prediction,
        recommended_amount=recommended_amount,
        risk_category=risk_category,
        priority_level=priority_level,
    )


def rank_loans_by_priority(loans: Iterable) -> list:
    """Sort loans (highest overdue_months & outstanding_amount first)."""
    return sorted(
        loans,
        key=lambda loan: (loan.overdue_months, loan.outstanding_amount),
        reverse=True,
    )
