from sqlalchemy.orm import Session
from models.models import ShiftAllowances, ShiftMapping, ShiftsAmount

from sqlalchemy import extract


def get_client_shift_summary(db: Session, payroll_month: str):
    """Fetch shift summary filtered by payroll_month (YYYY-MM) including total allowances."""

    year, month = payroll_month.split("-")

    # Fetch all records for this payroll month
    records = (
        db.query(ShiftAllowances)
        .filter(
            extract("year", ShiftAllowances.payroll_month) == int(year),
            extract("month", ShiftAllowances.payroll_month) == int(month)
        )
        .all()
    )

    if not records:
        return []

    summary = {}

    for row in records:
        client = row.client or "Unknown"

        if client not in summary:
            summary[client] = {
                "employees": set(),
                "shift_a": 0,
                "shift_b": 0,
                "shift_c": 0,
                "prime": 0,
                "total_allowances": 0
            }

        summary[client]["employees"].add(row.emp_id)

        # Loop shift mapping rows and calculate amounts
        for mapping in row.shift_mappings:
            shift_type = mapping.shift_type
            days = mapping.days or 0

            # Add days to summary
            if shift_type.lower() == "a":
                summary[client]["shift_a"] += days
            elif shift_type.lower() == "b":
                summary[client]["shift_b"] += days
            elif shift_type.lower() == "c":
                summary[client]["shift_c"] += days
            elif shift_type.lower() == "prime":
                summary[client]["prime"] += days

            # Fetch rate dynamically
            rate = (
                db.query(ShiftsAmount.amount)
                .filter(ShiftsAmount.shift_type == shift_type)
                .filter(ShiftsAmount.payroll_year == year)
                .scalar()
            ) or 0

            summary[client]["total_allowances"] += days * float(rate)

    # Convert final result format
    result = [
        {
            "client": client,
            "total_employees": len(info["employees"]),
            "shift_a_days": info["shift_a"],
            "shift_b_days": info["shift_b"],
            "shift_c_days": info["shift_c"],
            "prime_days": info["prime"],
            "total_allowances": round(info["total_allowances"], 2)
        }
        for client, info in summary.items()
    ]

    return result
