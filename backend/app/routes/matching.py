from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.utils.serializers import serialize
from app.services.matching import keyword_match

router = APIRouter(prefix="/matching", tags=["AI Matching"])

class MatchIn(BaseModel):
    request: str = Field(min_length=3, max_length=1000)

@router.post("")
def match(data: MatchIn, user=Depends(get_current_user)):
    schemes = list(get_db().schemes.find({"status": "active"}))
    ranked = keyword_match(data.request, schemes)
    top = []
    for score, scheme in ranked[:6]:
        item = serialize(scheme)
        item["semantic_match_score"] = min(100, score * 15)
        item["match_reason"] = "Semantic/keyword relevance based on the scheme description; official eligibility is checked separately."
        top.append(item)
    return {
        "query": data.request,
        "results": top,
        "guardrail": "Matching relevance does not establish legal eligibility. Use the eligibility and readiness checks."
    }
