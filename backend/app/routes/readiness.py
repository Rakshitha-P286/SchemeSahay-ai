from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.services.eligibility_engine import check_rules
from app.services.readiness_engine import calculate_readiness

router = APIRouter(prefix="/readiness", tags=["Readiness"])

@router.post("/check/{scheme_id}")
def readiness(scheme_id: str, user=Depends(get_current_user)):
    db = get_db()
    profile = db.citizen_profiles.find_one({"user_id": user["_id"]}) or {}
    scheme = db.schemes.find_one({"_id": ObjectId(scheme_id)})
    if not scheme:
        raise HTTPException(404, "Scheme not found")
    rules = list(db.eligibility_rules.find({"scheme_id": scheme["_id"]}))
    docs = list(db.scheme_documents.find({"scheme_id": scheme["_id"]}))
    uploaded = list(db.user_documents.find({"user_id": user["_id"]}))
    evidence, eligibility_score = check_rules(profile, rules)
    result = calculate_readiness(profile, evidence, docs, uploaded)
    result["scheme"] = {"id": str(scheme["_id"]), "name": scheme["name"]}
    result["disclaimer"] = "Readiness measures avoidable application issues. It is not a probability of sanction or approval."
    return result
