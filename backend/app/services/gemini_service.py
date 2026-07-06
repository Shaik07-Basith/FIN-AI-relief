"""
AI Integration & Financial Processing Setup (Epic 2)

Wraps Google Gemini AI to generate:
  1. A short negotiation strategy for a given loan
  2. A professional settlement/negotiation letter addressed to the lender

If GEMINI_API_KEY is not configured (or the call fails for any reason, e.g.
network/quota issues), the service transparently falls back to a
template-based generator so the rest of the platform keeps working end to
end -- this is the "AI fallback management" referenced in Epic 5.
"""
from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()

_gemini_ready = False
if settings.gemini_api_key:
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        _gemini_ready = True
    except Exception:
        _gemini_ready = False


@dataclass
class NegotiationContent:
    negotiation_strategy: str
    negotiation_letter: str
    source: str  # "gemini" or "fallback"


def _build_prompt(context: dict, tone: str) -> str:
    return f"""
You are a financial negotiation assistant helping a borrower settle debt
responsibly and lawfully. Using the details below, produce:

1. A short (4-6 bullet points) negotiation strategy the borrower can follow.
2. A polite, {tone} settlement request letter addressed to the lender,
   referencing the loan and proposing the recommended settlement amount.

Loan/Lender: {context['lender_name']} ({context['loan_type']})
Outstanding amount: {context['outstanding_amount']}
Overdue months: {context['overdue_months']}
Borrower monthly surplus: {context['monthly_surplus']}
Recommended settlement amount: {context['recommended_amount']}
Financial stress level: {context['stress_level']}

Respond in two clearly labeled sections: "STRATEGY:" and "LETTER:".
Do not include any illegal, misleading, or threatening language.
""".strip()


def _fallback_generate(context: dict, tone: str) -> NegotiationContent:
    strategy = (
        f"- Open communication with {context['lender_name']} before the account escalates further.\n"
        f"- Reference the {context['overdue_months']} month(s) overdue status honestly.\n"
        f"- Propose a lump-sum settlement of {context['recommended_amount']} against the "
        f"outstanding {context['outstanding_amount']}.\n"
        f"- Highlight limited monthly surplus ({context['monthly_surplus']}) as the reason "
        f"full repayment isn't currently feasible.\n"
        f"- Request written confirmation of any settlement agreement before making payment.\n"
        f"- Ask about the impact on your credit report once the settlement is completed."
    )

    letter = f"""Dear {context['lender_name']} Team,

I am writing regarding my {context['loan_type']} account with an outstanding
balance of {context['outstanding_amount']}. Due to ongoing financial
hardship, I have been unable to maintain regular payments for the past
{context['overdue_months']} month(s).

After reviewing my current financial position, I would like to propose a
one-time settlement of {context['recommended_amount']} to fully close this
account. I am committed to resolving this matter responsibly and would
appreciate the opportunity to discuss a mutually agreeable arrangement.

Please let me know the next steps required to proceed with this settlement,
and kindly confirm any agreement in writing.

Thank you for your understanding and consideration.

Sincerely,
A Valued Customer"""

    return NegotiationContent(
        negotiation_strategy=strategy,
        negotiation_letter=letter,
        source="fallback",
    )


def _parse_gemini_response(text: str) -> tuple[str, str]:
    strategy, letter = "", ""
    upper = text.upper()
    if "STRATEGY:" in upper and "LETTER:" in upper:
        strategy_idx = upper.index("STRATEGY:")
        letter_idx = upper.index("LETTER:")
        if strategy_idx < letter_idx:
            strategy = text[strategy_idx + len("STRATEGY:"):letter_idx].strip()
            letter = text[letter_idx + len("LETTER:"):].strip()
        else:
            letter = text[letter_idx + len("LETTER:"):strategy_idx].strip()
            strategy = text[strategy_idx + len("STRATEGY:"):].strip()
    else:
        # Model didn't follow the format exactly; use the whole response as
        # the letter and leave a generic strategy note.
        letter = text.strip()
        strategy = "See generated letter for the recommended negotiation approach."
    return strategy, letter


def generate_negotiation_content(context: dict, tone: str = "professional") -> NegotiationContent:
    """
    context keys required: lender_name, loan_type, outstanding_amount,
    overdue_months, monthly_surplus, recommended_amount, stress_level
    """
    if not _gemini_ready:
        return _fallback_generate(context, tone)

    try:
        model = genai.GenerativeModel(settings.gemini_model)
        prompt = _build_prompt(context, tone)
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        if not text:
            return _fallback_generate(context, tone)

        strategy, letter = _parse_gemini_response(text)
        if not strategy or not letter:
            return _fallback_generate(context, tone)

        return NegotiationContent(
            negotiation_strategy=strategy,
            negotiation_letter=letter,
            source="gemini",
        )
    except Exception:
        # Any API/network/quota error -> fall back gracefully.
        return _fallback_generate(context, tone)
