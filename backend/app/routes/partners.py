from fastapi import APIRouter, Depends
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/partners", tags=["Partners"])

@router.get("")
def partners(user=Depends(get_current_user)):
    return serialize(list(get_db().assistance_channels.find({"is_demo": True}).sort("distance_km", 1)))

@router.get("/recommended/{scheme_id}")
def recommended(scheme_id: str, user=Depends(get_current_user)):
    profile = get_db().citizen_profiles.find_one({"user_id": user["_id"]}) or {}
    partners = list(get_db().assistance_channels.find({"is_demo": True}))
    # Demo routing: compatibility is represented through services. In production,
    # replace this with an authoritative authorization mapping.
    state = profile.get("state", "")
    if state:
        local = [p for p in partners if not p.get("state") or p.get("state") == state]
        if local:
            partners = local
    return {
        "scheme_id": scheme_id,
        "routing_basis": ["scheme compatibility", "authorization data when available", "geographic proximity"],
        "partners": serialize(sorted(partners, key=lambda x: x.get("distance_km", 999))[:5]),
        "note": "Demo partner records are illustrative. Live authorization/availability must come from authoritative partner data."
    }
