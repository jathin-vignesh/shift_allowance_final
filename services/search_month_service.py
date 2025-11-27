import pandas as pd
from datetime import datetime, date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import ShiftAllowances
 
def search_shift_by_month_range(
    db: Session,
    start_month: str | None = None,
    end_month: str | None = None
):
    # Ensure at least one month is provided
    if not start_month and not end_month:
        raise HTTPException(status_code=400, detail="Provide at least one month.")
 
    # Parse month strings
    try:
        start_date = datetime.strptime(start_month, "%Y-%m").date() if start_month else None
        end_date = datetime.strptime(end_month, "%Y-%m").date() if end_month else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
 
    today = date.today()
    current_month_start = today.replace(day=1)
 
    # Check end month not greater than current
    if end_date and end_date > current_month_start:
        raise HTTPException(status_code=400, detail="end_month cannot be greater than current month")
 
    # Convert start/end to first day of month
    if start_date:
        start_date = start_date.replace(day=1)
    if end_date:
        end_date = end_date.replace(day=1)
 
    # Base query
    query = db.query(
        ShiftAllowances.emp_id,
        ShiftAllowances.emp_name,
        ShiftAllowances.grade,
        ShiftAllowances.department,
        ShiftAllowances.client,
        ShiftAllowances.project,
        ShiftAllowances.project_code,
        ShiftAllowances.account_manager,
        func.to_char(ShiftAllowances.duration_month, "YYYY-MM").label("duration_month"),
        ShiftAllowances.payroll_month
    )
 
    # Apply month filters
    if start_date and end_date:
        query = query.filter(
            func.date_trunc("month", ShiftAllowances.payroll_month) >= start_date,
            func.date_trunc("month", ShiftAllowances.payroll_month) <= end_date
        )
    elif start_date:
        query = query.filter(func.date_trunc("month", ShiftAllowances.payroll_month) == start_date)
    elif end_date:
        query = query.filter(func.date_trunc("month", ShiftAllowances.payroll_month) == end_date)
 
    # Execute query
    rows = query.order_by(ShiftAllowances.payroll_month, ShiftAllowances.emp_id).all()
 
    if not rows:
        raise HTTPException(status_code=404, detail="No records found for given month range")
 
    # Convert to dict + format payroll_month as YYYY-MM
    final_data = []
    for row in rows:
        r = row._asdict()
        r["payroll_month"] = row.payroll_month.strftime("%Y-%m")
        final_data.append(r)
 
    return pd.DataFrame(final_data)