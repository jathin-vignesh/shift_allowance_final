import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import ShiftAllowances, ShiftMapping, ShiftsAmount


def export_filtered_excel(db: Session, emp_id: str | None, account_manager: str | None):

    # Base query with UNIQUE emp_id grouping
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
            func.min(ShiftAllowances.delivery_manager).label("delivery_manager"),
            func.min(ShiftAllowances.practice_lead).label("practice_lead"),
            func.min(ShiftAllowances.billability_status).label("billability_status"),
            func.min(ShiftAllowances.practice_remarks).label("practice_remarks"),
            func.min(ShiftAllowances.rmg_comments).label("rmg_comments"),
            func.min(ShiftAllowances.duration_month).label("duration_month"),
            func.min(ShiftAllowances.payroll_month).label("payroll_month")
        )
        .outerjoin(ShiftMapping, ShiftAllowances.id == ShiftMapping.shiftallowance_id)
        .group_by(ShiftAllowances.emp_id)   # 👈 EMPLOYEE UNIQUE
    )

    # No filters → get all employees
    if not emp_id and not account_manager:
        rows = query.all()
    else:
        if emp_id:
            query = query.filter(ShiftAllowances.emp_id == emp_id)

        if account_manager:
            query = query.filter(ShiftAllowances.account_manager == account_manager)

        rows = query.all()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No data found for the given emp_id or account_manager"
            )

    # Fetch shift amount values
    shift_rates = db.query(ShiftsAmount).all()

    if not shift_rates:
        raise HTTPException(
            status_code=404,
            detail="Shift allowance amount table (shifts_amount) is empty. Please configure the shift rates."
        )

    # Convert shift amounts into a lookup map
    allowance_map = {
        rate.shift_type.upper(): float(rate.amount)
        for rate in shift_rates
    }

    final_data = []

    for row in rows:

        shift_list = row.shift_type or []
        shift_list = [str(s).upper() for s in shift_list]

        # Calculate total allowances
        total_allowances = sum(allowance_map.get(s, 0) for s in shift_list)

        row_dict = row._asdict()

        # Convert numpy types to python types
        clean_row = {}
        for key, val in row_dict.items():
            if hasattr(val, "item"):
                clean_row[key] = val.item()
            else:
                clean_row[key] = val

        clean_row["total_allowances"] = total_allowances

        final_data.append(clean_row)

    # Convert to Excel-friendly format
    df = pd.DataFrame(final_data)

    return df.to_dict(orient="records")
