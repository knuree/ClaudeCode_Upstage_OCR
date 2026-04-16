from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# uploads 디렉토리 보장
Path("backend/uploads").mkdir(parents=True, exist_ok=True)

from backend.routers import expenses, summary, upload  # noqa: E402

app = FastAPI(
    title="Receipt Expense Tracker API",
    version="1.0.0",
    description="영수증 업로드 → Upstage Vision LLM OCR → 지출 관리",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(expenses.router, prefix="/api", tags=["expenses"])
app.include_router(summary.router, prefix="/api", tags=["summary"])


@app.get("/")
def root():
    return {"message": "Receipt Expense Tracker API", "docs": "/docs"}
