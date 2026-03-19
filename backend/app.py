import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Exam Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("faiss_stores", exist_ok=True)

# In-memory stores for documents and exams
documents_store = {}  # document_id -> parsed data
exams_store = {}      # exam_id -> exam data

from routes.upload import router as upload_router
from routes.generate import router as generate_router

app.include_router(upload_router, prefix="/upload", tags=["upload"])
app.include_router(generate_router, tags=["generate"])


@app.get("/health")
def health():
    return {"status": "ok"}
