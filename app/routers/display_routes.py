from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session,joinedload
from db import get_db
from models.models import ShiftAllowances,ShiftMapping
from utils.dependencies import get_current_user
from schemas.displayschema import PaginatedShiftResponse,EmployeeResponse,ShiftUpdateRequest,ShiftUpdateResponse
from services.display_service import update_shift_service
from sqlalchemy import func

router = APIRouter(prefix="/display")

@router.get("/", response_model=PaginatedShiftResponse)
def get_all_data(
    start: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    query = (
        db.query(
            ShiftAllowances.emp_id.label("emp_id"),
            func.min(ShiftAllowances.id).label("id"),
            func.min(ShiftAllowances.emp_name).label("emp_name"),
            func.min(ShiftAllowances.department).label("department"),
            func.min(ShiftAllowances.payroll_month).label("month"),
            func.min(ShiftAllowances.client).label("client"),
            func.min(ShiftAllowances.project_code).label("project_code"),
            func.min(ShiftAllowances.account_manager).label("account_manager"),
            func.array_agg(ShiftMapping.shift_type).label("shift_category")
        )
        .outerjoin(ShiftMapping, ShiftAllowances.id == ShiftMapping.shiftallowance_id)
        .group_by(ShiftAllowances.emp_id)
    )

    total_records = query.count()

    data = (
        query.order_by(func.min(ShiftAllowances.id).asc())
        .offset(start)
        .limit(limit)
        .all()
    )

    if not data:
        raise HTTPException(status_code=404, detail="No data found for given range")

    return {
        "total_records": total_records,
        "data": data
    }


@router.get("/{id}",response_model=EmployeeResponse)
def get_detail_page(id:int, 
                    db:Session = Depends(get_db),
                    current_user=Depends(get_current_user),):
    data = (db.query(ShiftAllowances)
            .options(joinedload(ShiftAllowances.shift_mappings))
            .filter(ShiftAllowances.id == id).first())
    if not data:
        raise HTTPException(status_code=404,detail="Given id doesn't exist")
    return data


@router.put("/update/{record_id}", response_model=ShiftUpdateResponse)
def update_detail_data(record_id: int, req: ShiftUpdateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    updates = req.model_dump() 
    
    result = update_shift_service(db, record_id, updates)
    
    return {
        "message": "Shift updated successfully",
        "updated_fields": [k for k, v in updates.items() if v > 0],
        "total_days": result["total_days"],
        "total_allowance": result["total_allowance"],
        "shift_details": result["shift_details"]
    }

