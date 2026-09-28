from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/profile", tags=["Profile"])

class ProfileIn(BaseModel):
    age: int | None = Field(default=None, ge=0, le=120)
    gender: str = ""
    state: str = ""
    district: str = ""
    area_type: str = ""
    category: str = ""
    income: float | None = Field(default=None, ge=0)
    occupation: str = ""
    employment_status: str = ""
    education: str = ""
    disability_status: bool = False
    family_size: int | None = None
    dependents: int | None = None
    land_ownership: float | None = None
    housing_status: str = ""
    bank_account: bool = False
    aadhaar_available: bool = False
    existing_benefits: list[str] = []
    business_type: str = ""
    business_status: str = ""
    project_cost: float | None = None
    required_loan: float | None = None

@router.get("")
def get_profile(user=Depends(get_current_user)):
    doc = get_db().citizen_profiles.find_one({"user_id": user["_id"]}) or {}
    return serialize(doc)

@router.put("")
def update_profile(data: ProfileIn, user=Depends(get_current_user)):
    payload = data.model_dump()
    payload["user_id"] = user["_id"]
    get_db().citizen_profiles.update_one({"user_id": user["_id"]}, {"$set": payload}, upsert=True)
    return {"message": "Profile saved", "profile": serialize(payload)}
