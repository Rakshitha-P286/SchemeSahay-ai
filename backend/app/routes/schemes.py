from fastapi import APIRouter, Depends, Query
from app.database.connection import get_db
from app.utils.serializers import serialize
from app.utils.security import get_current_user

router = APIRouter(prefix="/schemes", tags=["Schemes"])

@router.get("")
def list_schemes(q: str = "", category: str = "", user=Depends(get_current_user)):
    query = {"status": "active"}
    if category:
        query["category"] = category
    docs = list(get_db().schemes.find(query).sort("name", 1))
    if q:
        ql = q.lower()
        docs = [x for x in docs if ql in (x.get("name","") + " " + x.get("description","") + " " + x.get("category","")).lower()]
    return [serialize(x) for x in docs]

@router.get("/{scheme_id}")
def scheme_detail(scheme_id: str, user=Depends(get_current_user)):
    from bson import ObjectId
    db = get_db()
    scheme = db.schemes.find_one({"_id": ObjectId(scheme_id)})
    if not scheme:
        from fastapi import HTTPException
        raise HTTPException(404, "Scheme not found")
    rules = list(db.eligibility_rules.find({"scheme_id": scheme["_id"]}))
    docs = list(db.scheme_documents.find({"scheme_id": scheme["_id"]}))
    result = serialize(scheme)
    result["rules"] = serialize(rules)
    result["documents"] = serialize(docs)
    return result
