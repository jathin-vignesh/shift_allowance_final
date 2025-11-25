import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import ShiftAllowances, ShiftMapping, ShiftsAmount


def export_filtered_excel(db: Session, emp_id: str | None, account_manager: str | None):

    # Base query → GROUP BY emp_id to keep EMPLOYEE UNIQUE
    query = (
        db.query(
            ShiftAllowances.emp_id,
            func.min(ShiftAllowances.emp_name).label("emp_name"),
            func.min(ShiftAllowances.grade).label("grade"),
            func.min(ShiftAllowances.department).label("department"),
            func.min(ShiftAllowances.client).label("client"),
            func.min(ShiftAllowances.project).label("project"),
            func.min(ShiftAllowances.project_code).label("project_code"),
            func.min(ShiftAllowances.account_manager).label("account_manager"),
            func.array_agg(ShiftMapping.shift_type).label("shift_type"),
            func.min(ShiftAllowances.duration_month).label("duration_month"),
            func.min(ShiftAllowances.payroll_month).label("payroll_month")
        )
        .outerjoin(ShiftMapping, ShiftAllowances.id == ShiftMapping.shiftallowance_id)
        .group_by(ShiftAllowances.emp_id)
    )

    # Apply filters
    if emp_id:
        query = query.filter(ShiftAllowances.emp_id == emp_id)

    if account_manager:
        query = query.filter(ShiftAllowances.account_manager == account_manager)

    rows = query.all()

    if not rows:
        raise HTTPException(status_code=404, detail="Entered emp_id or account_manager is not found")

    # Load shift amounts
    shift_amounts = db.query(ShiftsAmount).all()
    if not shift_amounts:
        raise HTTPException(status_code=404, detail="Shift amount table is empty")

    # Convert amounts to dictionary → {'A': 500, 'B':350, ...}
    AMOUNT_MAP = {s.shift_type.upper(): float(s.amount) for s in shift_amounts}

    # FINAL RESULT LIST
    final = []

    for r in rows:
        shifts = r.shift_type or []
        shifts = [s.upper() for s in shifts]

        total_allowances = sum(AMOUNT_MAP.get(s, 0) for s in shifts)

        row_dict = r._asdict()
        row_dict["total_allowances"] = total_allowances

        final.append(row_dict)

    return pd.DataFrame(final)
