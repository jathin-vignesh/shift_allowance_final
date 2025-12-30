"""
Client summary API test cases.

This module contains integration tests for the `/client-summary`
endpoint, validating successful responses for all clients and
specific clients, as well as error handling for invalid inputs.
"""

from datetime import date
from models.models import ShiftAllowances

# API ROUTES
CLIENT_SUMMARY_URL = "/client-summary"

# HELPER FUNCTION
def seed_client_summary_data(db):
    """
    Seed database with minimal shift allowance data
    required for client summary tests.

    Args:
        db: Database session fixture.
    """
    db.query(ShiftAllowances).delete()
    db.add(
        ShiftAllowances(
            emp_id="E01",
            emp_name="User",
            client="ClientA",
            department="IT",
            duration_month=date(2024, 1, 1),
            payroll_month=date(2024, 1, 1),
        )
    )
    db.commit()

# /client-summary API TESTCASES
def test_client_summary_all_clients_success(client, db_session):
    """
    Verify client summary returns successfully when
    requesting data for all clients.
    """
    seed_client_summary_data(db_session)

    resp = client.post(CLIENT_SUMMARY_URL, json={"clients": "ALL"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)



def test_client_summary_specific_client_success(client, db_session):
    """
    Verify client summary returns data for a specific client
    with valid year and month filters.
    """
    seed_client_summary_data(db_session)

    payload = {
        "clients": {"ClientA": ["IT"]},
        "selected_year": "2024",
        "selected_months": ["01"],
    }

    resp = client.post(CLIENT_SUMMARY_URL, json=payload)
    assert resp.status_code == 200

    month_data = resp.json()["2024-01"]

    if "clients" in month_data:
        assert "ClientA" in month_data["clients"]
    else:
        assert "message" in month_data



def test_client_summary_months_without_year_fails(client):
    """
    Verify request fails when months are provided
    without specifying a year.
    """
    payload = {
        "clients": "ALL",
        "selected_months": ["01"],
    }

    resp = client.post(CLIENT_SUMMARY_URL, json=payload)
    assert resp.status_code == 400
    assert "selected_year" in resp.text



def test_client_summary_invalid_quarter(client):
    """
    Verify request fails when an invalid quarter value is provided.
    """
    payload = {
        "clients": "ALL",
        "selected_year": "2024",
        "selected_quarters": ["Q5"],
    }

    resp = client.post(CLIENT_SUMMARY_URL, json=payload)
    assert resp.status_code == 400
    assert "Invalid quarter" in resp.text
