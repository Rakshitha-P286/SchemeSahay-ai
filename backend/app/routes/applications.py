from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/applications", tags=["Applications"])

class CreateApplication(BaseModel):
    scheme_id: str
    channel: str = ""

@router.post("")
def create(data: CreateApplication, user=Depends(get_current_user)):
    db = get_db()
    scheme = db.schemes.find_one({"_id": ObjectId(data.scheme_id)})
    if not scheme:
        raise HTTPException(404, "Scheme not found")
    app = {
        "user_id": user["_id"],
        "scheme_id": scheme["_id"],
        "status": "draft",
        "readiness_score": None,
        "channel": data.channel,
        "created_at": datetime.utcnow(),
    }
    result = db.applications.insert_one(app)
    app["_id"] = result.inserted_id
    db.application_events.insert_one({
        "application_id": result.inserted_id,
        "status": "draft",
        "description": "Application prepared",
        "action_required": "Complete the application checklist",
        "created_at": datetime.utcnow()
    })
    return serialize(app)

@router.get("")
def list_apps(user=Depends(get_current_user)):
    return serialize(list(get_db().applications.find({"user_id": user["_id"]}).sort("created_at", -1)))

@router.get("/{application_id}")
def detail(application_id: str, user=Depends(get_current_user)):
    db = get_db()
    app = db.applications.find_one({"_id": ObjectId(application_id), "user_id": user["_id"]})
    if not app:
        raise HTTPException(404, "Application not found")
    events = list(db.application_events.find({"application_id": app["_id"]}).sort("created_at", 1))
    result = serialize(app)
    result["events"] = serialize(events)
    return result

@router.post("/{application_id}/submit")
def submit(application_id: str, user=Depends(get_current_user)):
    db = get_db()
    app = db.applications.find_one({"_id": ObjectId(application_id), "user_id": user["_id"]})
    if not app:
        raise HTTPException(404, "Application not found")
    db.applications.update_one({"_id": app["_id"]}, {"$set": {"status": "submitted", "submitted_at": datetime.utcnow()}})
    db.application_events.insert_one({
        "application_id": app["_id"],
        "status": "submitted",
        "description": "Application submitted for the demo workflow",
        "action_required": "",
        "created_at": datetime.utcnow()
    })
    return {"message": "Application submitted", "status": "submitted"}
