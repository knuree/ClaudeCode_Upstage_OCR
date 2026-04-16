import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Vercel 서버리스 환경에서는 /tmp 디렉토리만 쓰기 가능
if os.getenv("VERCEL"):
    DATA_FILE = Path("/tmp/expenses.json")
else:
    DATA_FILE = Path(os.getenv("DATA_FILE_PATH", "backend/data/expenses.json"))


def _ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_expenses() -> list[dict]:
    _ensure_file()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_expenses(data: list[dict]) -> None:
    _ensure_file()
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_expense(item: dict) -> dict:
    item["id"] = str(uuid.uuid4())
    item["created_at"] = datetime.now(timezone.utc).isoformat()
    expenses = load_expenses()
    expenses.append(item)
    save_expenses(expenses)
    return item
