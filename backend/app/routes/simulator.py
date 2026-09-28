from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.utils.security import get_current_user

router = APIRouter(prefix="/simulator", tags=["Financial Simulator"])

class SimIn(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    tenure_months: int = Field(gt=0, le=360)
    own_contribution: float = Field(ge=0, default=0)
    moratorium_months: int = Field(ge=0, le=60, default=0)

def calc_emi(p, annual_rate, n):
    if annual_rate == 0:
        return p / n
    r = annual_rate / 12 / 100
    return p * r * (1+r)**n / ((1+r)**n - 1)

@router.post("/calculate")
def calculate(data: SimIn, user=Depends(get_current_user)):
    emi = calc_emi(data.principal, data.annual_rate, data.tenure_months)
    total = emi * data.tenure_months
    interest = total - data.principal
    return {
        "loan_amount": round(data.principal, 2),
        "own_contribution": round(data.own_contribution, 2),
        "estimated_emi": round(emi, 2),
        "estimated_interest": round(max(0, interest), 2),
        "estimated_total_repayment": round(total, 2),
        "moratorium_months": data.moratorium_months,
        "note": "Illustrative calculation based on user inputs and entered parameters. Not a guaranteed government benefit or sanction amount."
    }
