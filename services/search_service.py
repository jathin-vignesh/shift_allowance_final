import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import ShiftAllowances
 
def export_filtered_excel(db: Session, emp_id: str | None = None, account_manager: str | None = None):
 
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
            func.to_char(ShiftAllowances.duration_month, "YYYY-MM").label("duration_month"),
            func.to_char(ShiftAllowances.payroll_month, "YYYY-MM").label("payroll_month")
        )
    )
 
    # Apply filters if provided
    if emp_id:
        query = query.filter(ShiftAllowances.emp_id.ilike(f"%{emp_id}%"))
 
    if account_manager:
        query = query.filter(ShiftAllowances.account_manager.ilike(f"%{account_manager}%"))
 
    rows = query.all()
 
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No data found for the given emp_id or account_manager"
        )
 
    # Convert query result to list of dicts
    final_data = []
    for row in rows:
        row_dict = row._asdict()
        # Convert any numpy types to native Python types
        clean_row = {k: (v.item() if hasattr(v, "item") else v) for k, v in row_dict.items()}
        final_data.append(clean_row)
 
    df = pd.DataFrame(final_data)
    return df.to_dict(orient="records")