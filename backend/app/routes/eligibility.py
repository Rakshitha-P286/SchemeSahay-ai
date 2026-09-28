from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.services.eligibility_engine import check_rules

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])

@router.post("/check/{scheme_id}")
def check(scheme_id: str, user=Depends(get_current_user)):
    db = get_db()
    profile = db.citizen_profiles.find_one({"user_id": user["_id"]}) or {}
    scheme = db.schemes.find_one({"_id": ObjectId(scheme_id)})
    if not scheme:
        raise HTTPException(404, "Scheme not found")
    rules = list(db.eligibility_rules.find({"scheme_id": scheme["_id"]}))
    evidence, score = check_rules(profile, rules)
    satisfied = all(x["status"] == "SATISFIED" for x in evidence if x["required"])
    return {
        "scheme": {"id": str(scheme["_id"]), "name": scheme["name"]},
        "potentially_eligible": satisfied,
        "eligibility_score": score,
        "evidence": evidence,
        "disclaimer": "This is a pre-screening based on stored scheme rules, not a government approval decision."
    }
