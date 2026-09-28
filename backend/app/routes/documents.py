import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.config.settings import settings
from app.database.connection import get_db
from app.utils.security import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/documents", tags=["Documents"])
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

@router.get("")
def documents(user=Depends(get_current_user)):
    return serialize(list(get_db().user_documents.find({"user_id": user["_id"]}).sort("uploaded_at", -1)))

@router.post("/upload")
async def upload(document_type: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, "Only PDF and image files are allowed")
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(413, "File too large; maximum is 10 MB")
    content = await file.read()
    filename = f"{uuid4().hex}{ext}"
    path = Path(settings.upload_dir) / filename
    path.write_bytes(content)

    ocr_text = ""
    ocr_status = "not_run"
    if ext in {".png", ".jpg", ".jpeg", ".webp"}:
        try:
            from PIL import Image
            import pytesseract
            ocr_text = pytesseract.image_to_string(Image.open(path))
            ocr_status = "completed"
        except Exception as exc:
            ocr_status = "unavailable"
    doc = {
        "user_id": user["_id"],
        "document_type": document_type,
        "document_name": file.filename,
        "file_url": f"/uploads/{filename}",
        "status": "uploaded",
        "ocr_status": ocr_status,
        "ocr_text": ocr_text[:10000],
    }
    result = get_db().user_documents.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)
