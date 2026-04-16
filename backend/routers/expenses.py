from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.services import storage_service

router = APIRouter()


@router.get("/expenses")
def get_expenses(from_date: Optional[str] = None, to_date: Optional[str] = None):
    """전체 지출 내역 조회. from/to 쿼리로 날짜 필터링 (YYYY-MM-DD)."""
    expenses = storage_service.load_expenses()

    if from_date:
        expenses = [e for e in expenses if e.get("receipt_date", "") >= from_date]
    if to_date:
        expenses = [e for e in expenses if e.get("receipt_date", "") <= to_date]

    return expenses


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str):
    """UUID로 지출 항목 삭제."""
    expenses = storage_service.load_expenses()
    filtered = [e for e in expenses if e.get("id") != expense_id]

    if len(filtered) == len(expenses):
        raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")

    storage_service.save_expenses(filtered)
    return {"message": "삭제되었습니다.", "id": expense_id}


@router.put("/expenses/{expense_id}")
def update_expense(expense_id: str, updates: dict):
    """UUID로 지출 항목 부분 수정."""
    expenses = storage_service.load_expenses()

    for i, expense in enumerate(expenses):
        if expense.get("id") == expense_id:
            # id·created_at 은 변경 불가
            updates.pop("id", None)
            updates.pop("created_at", None)
            expenses[i] = {**expense, **updates}
            storage_service.save_expenses(expenses)
            return expenses[i]

    raise HTTPException(status_code=404, detail="해당 지출 항목을 찾을 수 없습니다.")
