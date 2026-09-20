import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_family_registration_happy_path():
    payload = {
        "address": {
            "line1": "101, Shanti Tower, Sector-11",
            "village_or_town": "Bhavnagar",
            "taluka": "Bhavnagar City",
            "district_code": 7,
            "pincode": "364001",
        },
        "head": {
            "full_name": "Rameshbhai Patel",
            "dob": "1980-05-15",
            "gender": "MALE",
            "marital_status": "MARRIED",
            "mobile": "9876500001",
            "relation_to_head": "SELF",
            "social_category": "GENERAL",
            "education_level": "GRADUATE",
            "occupation_type": "FARMER",
            "has_bank_account": True,
            "is_head": True,
        },
        "members": [
            {
                "full_name": "Savitaben Patel",
                "dob": "1984-08-20",
                "gender": "FEMALE",
                "marital_status": "MARRIED",
                "mobile": "9876500002",
                "relation_to_head": "SPOUSE",
                "social_category": "GENERAL",
                "education_level": "SECONDARY",
                "occupation_type": "HOMEMAKER",
                "has_bank_account": True,
            },
            {
                "full_name": "Aarav Patel",
                "dob": "2012-03-10",
                "gender": "MALE",
                "marital_status": "UNMARRIED",
                "relation_to_head": "SON",
                "social_category": "GENERAL",
                "education_level": "PRIMARY",
                "occupation_type": "OTHER",
            },
        ],
        "ration_card_type": "PHH",
        "ration_card_number": "GJ0712345678",
        "income_band": "1L_2_5L",
        "land_holding_acres": 2.5,
        "house_type": "PUCCA",
        "house_owned": True,
        "consent_given": True,
    }

    res = client.post("/api/v1/families", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert "family_id" in data
    assert data["family_id"].startswith("GJ-07-")
    assert data["status"] == "SUBMITTED"
    assert data["head_name"] == "Rameshbhai Patel"
    assert data["member_count"] == 3
    assert len(data["members"]) == 3


def test_family_registration_rejects_minor_head():
    payload = {
        "address": {
            "line1": "202, Green Park",
            "village_or_town": "Ahmedabad",
            "taluka": "Ahmedabad City",
            "district_code": 1,
            "pincode": "380001",
        },
        "head": {
            "full_name": "Minor Kid",
            "dob": "2015-01-01",  # 11 years old -> MUST REJECT
            "gender": "MALE",
            "marital_status": "UNMARRIED",
            "relation_to_head": "SELF",
        },
        "members": [],
    }

    res = client.post("/api/v1/families", json=payload)
    assert res.status_code == 422  # Validation Error


def test_family_lookup_api():
    # 1. Register a family
    reg_payload = {
        "address": {
            "line1": "Address 1",
            "village_or_town": "Rajkot",
            "taluka": "Rajkot",
            "district_code": 27,
            "pincode": "360001",
        },
        "head": {
            "full_name": "Kiritbhai Shah",
            "dob": "1975-04-12",
            "gender": "MALE",
            "relation_to_head": "SELF",
        },
        "members": [],
    }
    res = client.post("/api/v1/families", json=reg_payload)
    fid = res.json()["family_id"]

    # 2. Lookup family existence
    lookup_res = client.get(f"/api/v1/lookup/family/{fid}")
    assert lookup_res.status_code == 200
    ldata = lookup_res.json()
    assert ldata["exists"] is True
    assert ldata["is_valid_format"] is True
    assert ldata["status"] == "SUBMITTED"
