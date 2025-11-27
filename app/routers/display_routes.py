from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session,joinedload
from db import get_db
from models.models import ShiftAllowances,ShiftMapping
from utils.dependencies import get_current_user
from schemas.displayschema import PaginatedShiftResponse,EmployeeResponse,ShiftUpdateRequest,ShiftUpdateResponse
from services.display_service import update_shift_service,display_emp_details,fetch_shift_data
from sqlalchemy import func

router = APIRouter(prefix="/display")

@router.get("/", response_model=PaginatedShiftResponse)
def get_all_data(
    start: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    selected_month, total_records, data, message = fetch_shift_data(db, start, limit)
 
    return {
        "selected_month": selected_month,
        "message": message,
        "total_records": total_records,
        "data": data
    }


@router.get("/{emp_id}")
def get_employee_shift_details(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return display_emp_details(emp_id, db)


@router.put("/shift/update", response_model=ShiftUpdateResponse)
def update_shift_detail(
    req: ShiftUpdateRequest,
    emp_id: str,
    payroll_month: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    updates = req.model_dump(exclude_unset=True)
    result = update_shift_service(db, emp_id=emp_id, payroll_month=payroll_month, updates=updates)
 
    return {
        "message": "Shift updated successfully",
        "updated_fields": result["updated_fields"],
        "total_days": result["total_days"],
        "total_allowance": result["total_allowance"],
        "shift_details": result["shift_details"]
    }


