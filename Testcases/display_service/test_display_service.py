"""
Display service API test cases.

This module contains integration tests for the `/display/update`
and `/display/client-enum` endpoints, validating update logic,
authentication behavior, and enum responses.
"""

from datetime import date
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app
from models.models import ShiftAllowances, ShiftsAmount
from utils.client_enums import Company
from utils.dependencies import get_current_user
client = TestClient(app)

# API ROUTES
UPDATE_URL = "/display/update"
CLIENT_ENUM_URL = "/display/client-enum"

# /display/update API TESTCASES
def test_update_shift_success(client: TestClient, db_session):
    """
    Verify shift update succeeds with valid input
    and returns correct allowance calculation.
    """
    db_session.add(ShiftsAmount(shift_type="A", amount=500, payroll_year=2024))
    allowance = ShiftAllowances(emp_id="IN01801960", emp_name="User1",
                                duration_month=date(2024,1,1),
                                payroll_month=date(2024,2,1))
    db_session.add(allowance)
    db_session.commit()

    resp = client.put(
        UPDATE_URL,
        params={"emp_id":"IN01801960","duration_month":"2024-01","payroll_month":"2024-02"},
        json={"shift_a":"2","shift_b":"0","shift_c":"0","prime":"0"}
    ).json()

    assert resp["message"] == "Shift updated successfully"
    assert resp["total_days"] == 2
    assert resp["total_allowance"] == 1000


def test_update_shift_invalid_payroll_month(client: TestClient):
    """
    Verify update fails when payroll month format is invalid.
    """
    resp = client.put(
        UPDATE_URL,
        params={"emp_id":"IN01801960","duration_month":"2024-01","payroll_month":"2024/02"},
        json={"shift_a":"1","shift_b":"0","shift_c":"0","prime":"0"}
    )
    assert resp.status_code == 400
    assert "YYYY-MM" in resp.json()["detail"]


def test_update_shift_same_month(client: TestClient):
    """
    Verify update fails when duration and payroll months are the same.
    """
    resp = client.put(
        UPDATE_URL,
        params={"emp_id":"IN01801960","duration_month":"2024-01","payroll_month":"2024-01"},
        json={"shift_a":"1","shift_b":"0","shift_c":"0","prime":"0"}
    )
    assert resp.status_code == 400
    assert "cannot be the same" in resp.json()["detail"]


def test_update_shift_record_not_found(client: TestClient):
    """
    Verify update fails when shift record does not exist.
    """
    resp = client.put(
        UPDATE_URL,
        params={"emp_id":"IN01844567","duration_month":"2024-01","payroll_month":"2024-02"},
        json={"shift_a": "1", "shift_b": "0", "shift_c": "0", "prime": "0"}
    )
    assert resp.status_code == 404
    assert "No shift record found" in resp.json()["detail"]


# /display/client-enum API TESTCASES

def test_client_enum_authenticated_returns_all_companies():
    """
    Verify authenticated user receives all client enum values.
    """
    client.app.dependency_overrides[get_current_user] = lambda: {
        "username": "testuser"
    }

    resp = client.get(CLIENT_ENUM_URL)
    assert resp.status_code == 200

    data = resp.json()

    for company in Company:
        assert company.value in data
        assert data[company.value]["value"] == company.name.replace("_", " ")
        assert data[company.value]["hexcode"].startswith("#")

    client.app.dependency_overrides = {}


def test_client_enum_response_contains_all_enum_values():
    """
    Verify client enum response contains all enum entries
    with correct response structure.
    """
    client.app.dependency_overrides[get_current_user] = lambda: {
        "username": "testuser"
    }

    resp = client.get(CLIENT_ENUM_URL)
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == len(Company)

    for company in Company:
        entry = data[company.value]
        assert set(entry.keys()) == {"value", "hexcode"}

    client.app.dependency_overrides = {}


def test_client_enum_unauthenticated_user():
    """
    Verify unauthenticated user is denied access.
    """
    resp = client.get(CLIENT_ENUM_URL)
    assert resp.status_code == 403


def test_client_enum_dependency_failure():
    """
    Verify authentication dependency failure is handled correctly.
    """
    client.app.dependency_overrides[get_current_user] = lambda: (
        (_ for _ in ()).throw(
            HTTPException(status_code=401, detail="Auth failed")
        )
    )

    resp = client.get(CLIENT_ENUM_URL)
    assert resp.status_code == 401

    client.app.dependency_overrides = {}
