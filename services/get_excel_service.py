import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import ShiftAllowances, ShiftMapping, ShiftsAmount
from fastapi import HTTPException
from datetime import datetime, date
 
def export_filtered_excel(
    db: Session,
    emp_id: str | None = None,
    account_manager: str | None = None,
    start_month: str | None = None,
    end_month: str | None = None
):
 
    # Base query
    query = (
        db.query(
            ShiftAllowances.emp_id,
            ShiftAllowances.emp_name,
            ShiftAllowances.grade,
            ShiftAllowances.department,
            ShiftAllowances.client,
            ShiftAllowances.project,
            ShiftAllowances.project_code,
            ShiftAllowances.account_manager,
            func.array_agg(ShiftMapping.shift_type).label("shift_type"),
            ShiftAllowances.delivery_manager,
            ShiftAllowances.practice_lead,
            ShiftAllowances.billability_status,
            ShiftAllowances.practice_remarks,
            ShiftAllowances.rmg_comments,
            ShiftAllowances.duration_month,
            ShiftAllowances.payroll_month
        )
        .outerjoin(ShiftMapping, ShiftAllowances.id == ShiftMapping.shiftallowance_id)
        .group_by(ShiftAllowances.id)
    )
 
    # Filters for emp_id & account_manager
    if emp_id:
        query = query.filter(func.trim(ShiftAllowances.emp_id) == emp_id.strip())
 
    if account_manager:
        query = query.filter(func.lower(func.trim(ShiftAllowances.account_manager)) ==
                             account_manager.strip().lower())
 
    today = date.today()
    current_month_start = today.replace(day=1)
 
    # --- MONTH FILTER LOGIC ---
    if start_month or end_month:
        # start month mandatory if end month given
        if not start_month:
            raise HTTPException(status_code=400, detail="start_month is required when end_month is provided")
 
        # Convert start month
        try:
            start_date = datetime.strptime(start_month, "%Y-%m").date().replace(day=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_month must be YYYY-MM")
 
        # If end month provided
        if end_month:
            try:
                end_date = datetime.strptime(end_month, "%Y-%m").date().replace(day=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="end_month must be YYYY-MM")
 
            if end_date > current_month_start:
                raise HTTPException(status_code=400, detail="end_month cannot be greater than current month")
 
            if start_date > end_date:
                raise HTTPException(status_code=400, detail="start_month cannot be after end_month")
 
            query = query.filter(
                func.date_trunc("month", ShiftAllowances.duration_month) >= start_date,
                func.date_trunc("month", ShiftAllowances.duration_month) <= end_date,
            )
        else:
            query = query.filter(func.date_trunc("month", ShiftAllowances.duration_month) == start_date)
 
    else:
        # No month filters
        # If employee or AM provided → RETURN ALL MONTHS
        if not emp_id and not account_manager:
            # No filters at all → return current month only
            query = query.filter(func.date_trunc("month", ShiftAllowances.duration_month) == current_month_start)
 
    # Execute query
    rows = query.all()
    if not rows:
        raise HTTPException(status_code=404, detail="No records found for given filters")
 
    # Shift allowance calculation
    shift_amounts = db.query(ShiftsAmount).all()
    ALLOWANCE_MAP = {item.shift_type.upper(): float(item.amount) for item in shift_amounts} if shift_amounts else {}
 
    final_data = []
    for row in rows:
        shift_list = [s.upper() for s in row.shift_type] if row.shift_type else []
        total_allowances = sum(ALLOWANCE_MAP.get(s, 0) for s in shift_list)
 
        final_data.append({
            "emp_id": row.emp_id,
            "emp_name": row.emp_name,
            "grade": row.grade,
            "department": row.department,
            "client": row.client,
            "project": row.project,
            "project_code": row.project_code,
            "account_manager": row.account_manager,
            "shift_type": shift_list,
            "delivery_manager": row.delivery_manager,
            "practice_lead": row.practice_lead,
            "billability_status": row.billability_status,
            "practice_remarks": row.practice_remarks,
            "rmg_comments": row.rmg_comments,
            "duration_month": row.duration_month.strftime("%Y-%m") if row.duration_month else None,
            "payroll_month": row.payroll_month.strftime("%Y-%m") if row.payroll_month else None,
            "total_allowances": total_allowances
        })
 
    return pd.DataFrame(final_data)