"""
Test to verify that unique emails can register successfully.
This test proves the endpoint works correctly for new users.
"""

import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_unique_email_registration():
    """Test that multiple unique emails can register successfully."""
    print("=" * 70)
    print("Testing Unique Email Registration")
    print("=" * 70)

    # Generate unique emails using timestamp
    timestamp = int(time.time())
    test_cases = [
        {
            "name": f"User {i}",
            "email": f"test_user_{timestamp}_{i}@example.com",
            "password": "SecurePass123"
        }
        for i in range(1, 6)  # Test 5 unique registrations
    ]

    successful_registrations = 0

    for i, user_data in enumerate(test_cases, 1):
        print(f"\n[Test {i}/5] Registering: {user_data['email']}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data
            )

            if response.status_code == 201:
                data = response.json()
                print(f"  ✓ Success! User ID: {data['user']['user_id']}")
                print(f"    Name: {data['user']['name']}")
                print(f"    Email: {data['user']['email']}")
                print(f"    Role: {data['user']['role']}")
                print(f"    Eco Points: {data['user']['eco_points']}")
                successful_registrations += 1
            else:
                print(f"  ✗ Failed with status {response.status_code}")
                print(f"    Response: {response.text}")

        except Exception as e:
            print(f"  ✗ Exception: {e}")

    print("\n" + "=" * 70)
    print(f"Results: {successful_registrations}/5 unique emails registered successfully")
    print("=" * 70)

    if successful_registrations == 5:
        print("✅ ALL TESTS PASSED - Unique emails register successfully!")
        return 0
    else:
        print(f"❌ FAILED - Only {successful_registrations}/5 succeeded")
        return 1


def test_duplicate_detection():
    """Test that duplicate email properly returns 409."""
    print("\n" + "=" * 70)
    print("Testing Duplicate Email Detection")
    print("=" * 70)

    timestamp = int(time.time())
    user_data = {
        "name": "Duplicate Test",
        "email": f"duplicate_test_{timestamp}@example.com",
        "password": "SecurePass123"
    }

    # First registration
    print(f"\n[Test 1] First registration: {user_data['email']}")
    response1 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )

    if response1.status_code == 201:
        print("  ✓ First registration successful")
    else:
        print(f"  ✗ First registration failed: {response1.status_code}")
        return 1

    # Duplicate registration
    print(f"\n[Test 2] Duplicate registration: {user_data['email']}")
    response2 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )

    if response2.status_code == 409:
        error_data = response2.json()
        print(f"  ✓ Duplicate correctly rejected with 409")
        print(f"    Error message: {error_data.get('detail')}")
    else:
        print(f"  ✗ Expected 409, got {response2.status_code}")
        return 1

    print("\n" + "=" * 70)
    print("✅ Duplicate detection works correctly!")
    print("=" * 70)
    return 0


def test_phone_uniqueness():
    """Test that duplicate phone numbers are rejected."""
    print("\n" + "=" * 70)
    print("Testing Phone Number Uniqueness")
    print("=" * 70)

    timestamp = int(time.time())
    phone = "+919999888877"

    # First user with phone
    user1 = {
        "name": "Phone User 1",
        "email": f"phone_user1_{timestamp}@example.com",
        "phone": phone,
        "password": "SecurePass123"
    }

    print(f"\n[Test 1] First user with phone {phone}")
    response1 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user1
    )

    if response1.status_code == 201:
        print("  ✓ First user registered successfully")
    else:
        print(f"  ✗ First registration failed: {response1.status_code}")
        return 1

    # Second user with same phone
    user2 = {
        "name": "Phone User 2",
        "email": f"phone_user2_{timestamp}@example.com",
        "phone": phone,  # Same phone
        "password": "SecurePass123"
    }

    print(f"\n[Test 2] Second user with same phone {phone}")
    response2 = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user2
    )

    if response2.status_code == 409:
        error_data = response2.json()
        print(f"  ✓ Duplicate phone correctly rejected with 409")
        print(f"    Error message: {error_data.get('detail')}")
    else:
        print(f"  ✗ Expected 409, got {response2.status_code}")
        return 1

    print("\n" + "=" * 70)
    print("✅ Phone uniqueness works correctly!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  REGISTRATION ENDPOINT VERIFICATION TEST")
    print("  Testing: POST /api/auth/register")
    print("=" * 70)

    # Run all tests
    result1 = test_unique_email_registration()
    result2 = test_duplicate_detection()
    result3 = test_phone_uniqueness()

    # Overall result
    print("\n" + "=" * 70)
    print("  OVERALL TEST RESULTS")
    print("=" * 70)

    if result1 == 0 and result2 == 0 and result3 == 0:
        print("✅ ALL TESTS PASSED")
        print("\nConclusion: The registration endpoint works correctly.")
        print("- Unique emails register successfully")
        print("- Duplicate emails are properly rejected (409)")
        print("- Duplicate phones are properly rejected (409)")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
