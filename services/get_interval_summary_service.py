from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from models.models import ShiftAllowances, ShiftsAmount


def get_interval_summary_service(start_month: str, end_month: str, db: Session):
    try:
        start = datetime.strptime(start_month + "-01", "%Y-%m-%d").date()
        end = datetime.strptime(end_month + "-01", "%Y-%m-%d").date()
    except:
        raise ValueError("Invalid input month format. Expected YYYY-MM")

    if start > end:
        raise ValueError("start_month must be <= end_month")

    current = start
    summary = {}

    while current <= end:
        allowances = db.query(ShiftAllowances).filter(
            ShiftAllowances.payroll_month == current
        ).all()

        if allowances:
            for allowance in allowances:
                client = allowance.client or "Unknown Client"

                if client not in summary:
                    summary[client] = {"A": 0, "B": 0, "C": 0, "PRIME": 0, "total_amount": 0}

                for mapping in allowance.shift_mappings:
                    stype = mapping.shift_type.strip().upper()
                    if stype in summary[client]:
                        summary[client][stype] += mapping.days

                payroll_year = str(current.year)
                shift_amount_rows = db.query(ShiftsAmount).filter(
                    ShiftsAmount.payroll_year == payroll_year
                ).all()

                amount_map = {sa.shift_type.strip().upper(): float(sa.amount) for sa in shift_amount_rows}

                for stype, days in summary[client].items():
                    if stype != "total_amount" and stype in amount_map:
                        summary[client]["total_amount"] += summary[client][stype] * amount_map[stype]

        current += relativedelta(months=1)

    return summary
