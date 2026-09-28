from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from app.database.connection import get_db
from app.utils.security import hash_password, verify_password, create_token
from app.utils.serializers import serialize

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    phone: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(data: RegisterIn):
    db = get_db()
    if db.users.find_one({"email": data.email.lower()}):
        raise HTTPException(409, "Email already registered")
    doc = {
        "name": data.name.strip(),
        "email": data.email.lower(),
        "phone": data.phone.strip(),
        "password_hash": hash_password(data.password),
        "role": "citizen",
    }
    result = db.users.insert_one(doc)
    db.profiles.insert_one({
        "user_id": result.inserted_id,
        "name": doc["name"],
        "email": doc["email"],
        "phone": doc["phone"],
        "created_at": __import__("datetime").datetime.utcnow(),
    })
    return {"message": "Registration successful", "user": {"id": str(result.inserted_id), "name": doc["name"], "email": doc["email"]}}

@router.post("/login")
def login(data: LoginIn):
    user = get_db().users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {
        "access_token": create_token(str(user["_id"])),
        "token_type": "bearer",
        "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user.get("role", "citizen")}
    }

@router.get("/me")
def me(user=__import__("fastapi").Depends(__import__("app.utils.security", fromlist=["get_current_user"]).get_current_user)):
    return {"user": serialize(user)}
