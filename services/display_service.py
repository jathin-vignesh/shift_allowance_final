from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import ShiftAllowances, ShiftMapping, ShiftsAmount

def update_shift_service(db: Session, record_id: int, updates: dict):
    # Allowed request keys
    allowed_fields = ["shift_a", "shift_b", "shift_c", "prime"]
    
    # Throw exception if extra fields sent
    extra_fields = [k for k in updates if k not in allowed_fields]
    if extra_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields: {extra_fields}. Only {allowed_fields} are allowed."
        )
    
    # Map request keys to DB shift types
    shift_map = {"shift_a": "A", "shift_b": "B", "shift_c": "C", "prime": "PRIME"}
    mapped_updates = {shift_map[k]: updates[k] for k in updates if updates[k] > 0}

    if not mapped_updates:
        raise HTTPException(status_code=400, detail="No shift days provided for update.")

    # Fetch the main record
    record = db.query(ShiftAllowances).filter(ShiftAllowances.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Shift allowance record not found")

    # Fetch rates from DB
    rate_rows = db.query(ShiftsAmount).all()
    rates = {r.shift_type: float(r.amount) for r in rate_rows}
    
    # Throw exception if any rate missing
    for shift_type in mapped_updates.keys():
        if shift_type not in rates:
            raise HTTPException(
                status_code=400,
                detail=f"Missing rate for shift '{shift_type}' in ShiftsAmount table."
            )

    # Update or create shift mappings
    existing_mappings = {m.shift_type: m for m in record.shift_mappings}
    for shift_type, days in mapped_updates.items():
        if shift_type in existing_mappings:
            existing_mappings[shift_type].days = days
        else:
            new_map = ShiftMapping(
                shiftallowance_id=record.id,
                shift_type=shift_type,
                days=days
            )
            db.add(new_map)
            existing_mappings[shift_type] = new_map

    db.commit()
    db.refresh(record)

    # Prepare shift details only for updated shifts
    shift_details = [
        {"shift": m.shift_type, "days": m.days}
        for shift_type, m in existing_mappings.items()
        if shift_type in mapped_updates
    ]

    total_days = sum(m.days for shift_type, m in existing_mappings.items() if shift_type in mapped_updates)
    total_allowance = sum(m.days * rates[m.shift_type] for shift_type, m in existing_mappings.items() if shift_type in mapped_updates)

    return {
        "record_id": record.id,
        "total_days": total_days,
        "total_allowance": total_allowance,
        "shift_details": shift_details
    }
