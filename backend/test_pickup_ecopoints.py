"""
Comprehensive tests for Pickup Booking and EcoPoints features.
Tests pickup creation, cancellation, completion, and EcoPoints rewards.
"""

import time
import pytest
import requests
from datetime import datetime, timedelta, timezone


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def test_user_credentials():
    """Create a test user and return credentials (session-scoped, runs once)."""
    timestamp = int(time.time())
    test_user_email = f"pickup_test_{timestamp}@example.com"

    # Register
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "name": "Pickup Test User",
            "email": test_user_email,
            "password": "PickupTest123"
        }
    )
    assert response.status_code == 201, f"Failed to register: {response.text}"

    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": test_user_email,
            "password": "PickupTest123"
        }
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"

    data = response.json()
    return {"email": test_user_email, "access_token": data["access_token"]}


@pytest.fixture
def access_token(test_user_credentials):
    """Get access token from test user credentials."""
    return test_user_credentials["access_token"]


@pytest.fixture
def pickup_id(access_token):
    """Create a test pickup and return its ID."""
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    response = requests.post(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "item_description": "Test Item for Fixture",
            "estimated_weight_kg": 0.5,
            "scheduled_at": tomorrow.isoformat(),
            "address": {
                "street": "123 Fixture Street",
                "city": "Test City",
                "state": "Test State",
                "pincode": "12345",
                "lat": 37.7749,
                "lng": -122.4194
            }
        }
    )

    assert response.status_code == 201, f"Failed to create pickup: {response.text}"
    return response.json()["pickup_id"]


def test_create_pickup(access_token):
    """Test creating a new pickup request."""
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    response = requests.post(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "item_description": "Old iPhone 12 - needs recycling",
            "estimated_weight_kg": 0.2,
            "scheduled_at": tomorrow.isoformat(),
            "address": {
                "street": "123 Test Street",
                "city": "San Francisco",
                "state": "California",
                "pincode": "94102",
                "lat": 37.7749,
                "lng": -122.4194
            },
            "notes": "Please call before arriving"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "pickup_id" in data
    assert data["status"] == "pending"
    assert "otp" in data and len(data["otp"]) == 6
    assert "message" in data


def test_get_pickups(access_token, pickup_id):
    """Test retrieving user's pickups."""
    response = requests.get(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "pickups" in data
    assert "total" in data
    assert len(data["pickups"]) > 0

    pickup = data["pickups"][0]
    required_fields = ["pickup_id", "item_description", "status", "scheduled_at", "address", "otp"]
    for field in required_fields:
        assert field in pickup, f"Missing field: {field}"


def test_get_single_pickup(access_token, pickup_id):
    """Test retrieving a single pickup by ID."""
    response = requests.get(
        f"{BASE_URL}/api/pickups/{pickup_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["pickup_id"] == pickup_id
    assert "otp" in data


def test_invalid_pickup_date(access_token):
    """Test validation of past pickup dates."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)

    response = requests.post(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "item_description": "Test item",
            "scheduled_at": yesterday.isoformat(),
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "Test State",
                "pincode": "12345",
                "lat": 0.0,
                "lng": 0.0
            }
        }
    )

    assert response.status_code == 422
    error = response.json()
    assert "future" in str(error).lower()


def test_cancel_pickup(access_token, pickup_id):
    """Test cancelling a pickup."""
    response = requests.post(
        f"{BASE_URL}/api/pickups/{pickup_id}/cancel",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reason": "Changed my mind"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"
    assert data["cancellation_reason"] == "Changed my mind"


def test_complete_pickup_with_ecopoints(access_token):
    """Test completing a pickup and awarding EcoPoints."""
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    # Create pickup
    create_response = requests.post(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "item_description": "Dell Laptop for completion test",
            "scheduled_at": tomorrow.isoformat(),
            "address": {
                "street": "456 Complete Ave",
                "city": "Test City",
                "state": "Test State",
                "pincode": "67890",
                "lat": 37.7749,
                "lng": -122.4194
            }
        }
    )

    assert create_response.status_code == 201
    pickup_data = create_response.json()
    pickup_id = pickup_data["pickup_id"]
    otp = pickup_data["otp"]

    # Complete pickup with OTP
    complete_response = requests.post(
        f"{BASE_URL}/api/pickups/{pickup_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"otp": otp}
    )

    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["status"] == "completed"
    assert complete_data["eco_points_awarded"] == 75
    assert "new_balance" in complete_data
    assert "transaction_id" in complete_data


def test_duplicate_ecopoints_prevention(access_token):
    """Test that EcoPoints cannot be awarded twice for the same pickup."""
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)

    # Create pickup
    create_response = requests.post(
        f"{BASE_URL}/api/pickups",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "item_description": "Test item for duplicate prevention",
            "scheduled_at": tomorrow.isoformat(),
            "address": {
                "street": "789 Duplicate Ave",
                "city": "Test City",
                "state": "Test State",
                "pincode": "11111",
                "lat": 37.7749,
                "lng": -122.4194
            }
        }
    )

    pickup_data = create_response.json()
    pickup_id = pickup_data["pickup_id"]
    otp = pickup_data["otp"]

    # Complete pickup first time
    first_complete = requests.post(
        f"{BASE_URL}/api/pickups/{pickup_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"otp": otp}
    )
    assert first_complete.status_code == 200

    # Try to complete again (should fail)
    second_complete = requests.post(
        f"{BASE_URL}/api/pickups/{pickup_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"otp": otp}
    )

    assert second_complete.status_code == 400
    error = second_complete.json()
    assert "already" in error.get("detail", "").lower()


def test_ecopoints_balance(access_token):
    """Test getting EcoPoints balance."""
    response = requests.get(
        f"{BASE_URL}/api/ecopoints/balance",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "user_id" in data
    assert isinstance(data["balance"], int)
    assert data["balance"] >= 75  # Should have earned points from previous tests


def test_ecopoints_transactions(access_token):
    """Test getting EcoPoints transaction history."""
    response = requests.get(
        f"{BASE_URL}/api/ecopoints/transactions",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data
    assert "current_balance" in data

    transactions = data["transactions"]
    assert len(transactions) > 0

    txn = transactions[0]
    required_fields = ["transaction_id", "points", "reason", "created_at"]
    for field in required_fields:
        assert field in txn, f"Missing field: {field}"
    assert txn["points"] == 75


def test_ecopoints_stats(access_token):
    """Test getting EcoPoints statistics."""
    response = requests.get(
        f"{BASE_URL}/api/ecopoints/stats",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    required_fields = ["current_balance", "total_earned", "total_transactions", "rank", "pickups_completed"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert isinstance(data["rank"], int)


def test_unauthorized_access():
    """Test that pickup endpoints require authentication."""
    # Test without token
    response = requests.get(f"{BASE_URL}/api/pickups")
    assert response.status_code == 403

    # Test EcoPoints without token
    response = requests.get(f"{BASE_URL}/api/ecopoints/balance")
    assert response.status_code == 403
