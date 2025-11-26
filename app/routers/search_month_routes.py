from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from services.search_month_service import search_shift_by_month_range

router = APIRouter(prefix="/monthly", tags=["Payroll Month Search"])

@router.get("/search")
def get_search_by_monthly(
    start_month: str | None = Query(None, description="Start month in YYYY-MM"),
    end_month: str | None = Query(None, description="End month in YYYY-MM"),
    db: Session = Depends(get_db)
):
    df = search_shift_by_month_range(db, start_month, end_month)
    return df.to_dict(orient="records")
