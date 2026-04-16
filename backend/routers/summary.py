from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timezone

from backend.services import storage_service

router = APIRouter()


@router.get("/summary")
def get_summary(month: Optional[str] = None):
    """
    지출 합계 통계 조회.

    Args:
        month: YYYY-MM 형식 (없으면 전체 기간)
    """
    expenses = storage_service.load_expenses()

    # 이번달 계산
    now = datetime.now(timezone.utc)
    this_month_prefix = now.strftime("%Y-%m")

    if month:
        filtered = [e for e in expenses if e.get("receipt_date", "").startswith(month)]
    else:
        filtered = expenses

    total_amount = sum(e.get("total_amount", 0) for e in filtered)
    this_month_amount = sum(
        e.get("total_amount", 0)
        for e in expenses
        if e.get("receipt_date", "").startswith(this_month_prefix)
    )

    # 카테고리별 합계
    category_map: dict[str, int] = {}
    for e in filtered:
        cat = e.get("category", "기타") or "기타"
        category_map[cat] = category_map.get(cat, 0) + e.get("total_amount", 0)

    category_summary = [
        {"category": cat, "amount": amount}
        for cat, amount in sorted(category_map.items(), key=lambda x: -x[1])
    ]

    return {
        "total_amount": total_amount,
        "this_month_amount": this_month_amount,
        "category_summary": category_summary,
    }
