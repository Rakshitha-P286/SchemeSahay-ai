from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.routes import auth, profile, schemes, eligibility, readiness, documents, simulator, matching, partners, applications
from chatbot import router as chatbot_router
app = FastAPI(title="SchemeSahay API", version="1.0.0")
app.include_router(chatbot_router, prefix="/api")
app.add_middleware(
        CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://scheme-sahay-ai.vercel.app/",
    ],
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(schemes.router, prefix="/api")
app.include_router(eligibility.router, prefix="/api")
app.include_router(readiness.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(partners.router, prefix="/api")
app.include_router(applications.router, prefix="/api")

@app.get("/")
def root():
    return {"name": "SchemeSahay", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
