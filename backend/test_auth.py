"""
Comprehensive tests for User Registration API.
Tests successful registration, validation, duplicates, and security.
"""

import asyncio
import sys
from typing import Dict, Any
import requests
from sqlalchemy import select, text
from database import init_db
from models import User
from security import verify_password


BASE_URL = "http://127.0.0.1:8000"
TEST_USERS = []


async def get_session_maker():
    """Get async session maker after initialization."""
    from database import async_session_maker
    return async_session_maker


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result with status indicator."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {test_name}")
    if details:
        print(f"  → {details}")


async def cleanup_test_users():
    """Clean up test users from database."""
    if not TEST_USERS:
        return

    print("\n🧹 Cleaning up test users...")
    session_maker = await get_session_maker()
    async with session_maker() as session:
        for email in TEST_USERS:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            if user:
                await session.delete(user)
        await session.commit()
    print(f"✓ Cleaned up {len(TEST_USERS)} test users")


def test_successful_registration():
    """Test successful user registration with all fields."""
    print_section("Test 1: Successful Registration")

    try:
        # Test data
        user_data = {
            "name": "Alice Johnson",
            "email": "alice.test@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123"
        }
        TEST_USERS.append(user_data["email"])

        # Make request
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        # Check status code
        if response.status_code != 201:
            print_test(
                "Status Code (201 Created)",
                False,
                f"Got {response.status_code}: {response.text}"
            )
            return False

        print_test("Status Code (201 Created)", True)

        # Check response structure
        data = response.json()

        # Validate message
        has_message = "message" in data and data["message"] == "User registered successfully"
        print_test("Success Message", has_message, data.get("message", ""))

        # Validate user object
        has_user = "user" in data
        print_test("User Object Present", has_user)

        if not has_user:
            return False

        user = data["user"]

        # Check all required fields
        required_fields = ["user_id", "name", "email", "phone", "role", "eco_points", "created_at"]
        all_fields_present = all(field in user for field in required_fields)
        print_test("All Required Fields Present", all_fields_present, str(required_fields))

        # Check field values
        name_correct = user["name"] == user_data["name"]
        print_test("Name Correct", name_correct, user["name"])

        email_correct = user["email"] == user_data["email"]
        print_test("Email Correct", email_correct, user["email"])

        phone_correct = user["phone"] == user_data["phone"]
        print_test("Phone Correct", phone_correct, user["phone"])

        role_correct = user["role"] == "user"
        print_test("Default Role (user)", role_correct, user["role"])

        points_correct = user["eco_points"] == 0
        print_test("Default Eco Points (0)", points_correct, str(user["eco_points"]))

        # CRITICAL: Ensure password_hash is NOT in response
        no_password = "password_hash" not in user and "password" not in user
        print_test("Password NOT in Response (SECURITY)", no_password)

        # Check UUID format
        import uuid
        try:
            uuid.UUID(user["user_id"])
            uuid_valid = True
        except ValueError:
            uuid_valid = False
        print_test("Valid UUID Format", uuid_valid, user["user_id"])

        all_passed = (
            has_message and has_user and all_fields_present and
            name_correct and email_correct and phone_correct and
            role_correct and points_correct and no_password and uuid_valid
        )

        return all_passed

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        return False


def test_registration_without_phone():
    """Test registration with optional phone field omitted."""
    print_section("Test 2: Registration Without Phone (Optional Field)")

    try:
        user_data = {
            "name": "Bob Smith",
            "email": "bob.test@example.com",
            "password": "AnotherPass456"
            # phone is optional, not included
        }
        TEST_USERS.append(user_data["email"])

        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        success = response.status_code == 201
        print_test("Registration Without Phone", success)

        if success:
            data = response.json()
            phone_is_null = data["user"]["phone"] is None
            print_test("Phone Field is NULL", phone_is_null)
            return phone_is_null

        return False

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        return False


def test_duplicate_email():
    """Test that duplicate email returns 409 Conflict."""
    print_section("Test 3: Duplicate Email Detection")

    try:
        # First registration
        user_data = {
            "name": "Charlie Brown",
            "email": "charlie.test@example.com",
            "password": "UniquePass789"
        }
        TEST_USERS.append(user_data["email"])

        response1 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        first_success = response1.status_code == 201
        print_test("First Registration Successful", first_success)

        # Attempt duplicate registration with same email
        user_data["name"] = "Charlie Brown Jr."  # Different name, same email
        response2 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        is_conflict = response2.status_code == 409
        print_test("Duplicate Email Returns 409 Conflict", is_conflict)

        if is_conflict:
            error_data = response2.json()
            has_detail = "detail" in error_data
            print_test("Error Response Has Detail", has_detail, error_data.get("detail", ""))

            correct_message = "email" in error_data.get("detail", "").lower()
            print_test("Error Message Mentions Email", correct_message)

            return has_detail and correct_message

        return False

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        return False


def test_duplicate_phone():
    """Test that duplicate phone returns 409 Conflict."""
    print_section("Test 4: Duplicate Phone Number Detection")

    try:
        # First registration
        user_data1 = {
            "name": "Diana Prince",
            "email": "diana.test@example.com",
            "phone": "+919999999999",
            "password": "WonderPass111"
        }
        TEST_USERS.append(user_data1["email"])

        response1 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data1
        )

        first_success = response1.status_code == 201
        print_test("First Registration Successful", first_success)

        # Attempt duplicate with same phone, different email
        user_data2 = {
            "name": "Diana Prince Alt",
            "email": "diana.alt.test@example.com",
            "phone": "+919999999999",  # Same phone
            "password": "WonderPass222"
        }
        TEST_USERS.append(user_data2["email"])

        response2 = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data2
        )

        is_conflict = response2.status_code == 409
        print_test("Duplicate Phone Returns 409 Conflict", is_conflict)

        if is_conflict:
            error_data = response2.json()
            has_detail = "detail" in error_data
            print_test("Error Response Has Detail", has_detail, error_data.get("detail", ""))

            correct_message = "phone" in error_data.get("detail", "").lower()
            print_test("Error Message Mentions Phone", correct_message)

            return has_detail and correct_message

        return False

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        return False


def test_validation_errors():
    """Test input validation (password, email, etc.)."""
    print_section("Test 5: Input Validation")

    all_passed = True

    # Test 5a: Invalid email format
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "Invalid Email",
                "email": "not-an-email",
                "password": "ValidPass123"
            }
        )

        is_error = response.status_code == 422  # Validation error
        print_test("Invalid Email Format (422)", is_error, f"Status: {response.status_code}")
        all_passed = all_passed and is_error

    except Exception as e:
        print_test("Invalid Email Test", False, str(e))
        all_passed = False

    # Test 5b: Password too short
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "Short Password",
                "email": "short.test@example.com",
                "password": "Pass1"  # Less than 8 characters
            }
        )

        is_error = response.status_code == 422
        print_test("Short Password Rejected (422)", is_error, f"Status: {response.status_code}")
        all_passed = all_passed and is_error

    except Exception as e:
        print_test("Short Password Test", False, str(e))
        all_passed = False

    # Test 5c: Password without digit
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "No Digit Password",
                "email": "nodigit.test@example.com",
                "password": "NoDigitPass"  # No numbers
            }
        )

        is_error = response.status_code == 422
        print_test("Password Without Digit Rejected (422)", is_error, f"Status: {response.status_code}")
        all_passed = all_passed and is_error

    except Exception as e:
        print_test("No Digit Password Test", False, str(e))
        all_passed = False

    # Test 5d: Missing required fields
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "Missing Email"
                # Missing email and password
            }
        )

        is_error = response.status_code == 422
        print_test("Missing Required Fields Rejected (422)", is_error, f"Status: {response.status_code}")
        all_passed = all_passed and is_error

    except Exception as e:
        print_test("Missing Fields Test", False, str(e))
        all_passed = False

    # Test 5e: Empty name
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "   ",  # Whitespace only
                "email": "empty.test@example.com",
                "password": "ValidPass123"
            }
        )

        is_error = response.status_code == 422
        print_test("Empty Name Rejected (422)", is_error, f"Status: {response.status_code}")
        all_passed = all_passed and is_error

    except Exception as e:
        print_test("Empty Name Test", False, str(e))
        all_passed = False

    return all_passed


async def test_password_security():
    """Test that passwords are properly hashed in database."""
    print_section("Test 6: Password Security (Hashing)")

    try:
        # Register a user
        user_data = {
            "name": "Security Test User",
            "email": "security.test@example.com",
            "password": "MySecurePass123"
        }
        TEST_USERS.append(user_data["email"])

        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        if response.status_code != 201:
            print_test("User Registration", False, f"Status: {response.status_code}")
            return False

        print_test("User Registration", True)

        # Query database directly to check password storage
        session_maker = await get_session_maker()
        async with session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            user = result.scalar_one_or_none()

            if not user:
                print_test("User Found in Database", False)
                return False

            print_test("User Found in Database", True)

            # Check password is hashed (not plaintext)
            password_is_hashed = user.password_hash != user_data["password"]
            print_test(
                "Password is Hashed (NOT plaintext)",
                password_is_hashed,
                f"Hash: {user.password_hash[:20]}..."
            )

            # Check hash format (Argon2 starts with $argon2)
            is_argon2 = user.password_hash.startswith("$argon2")
            print_test("Uses Argon2 Format", is_argon2, user.password_hash[:15])

            # Verify password using our hash function
            password_verifies = verify_password(user_data["password"], user.password_hash)
            print_test("Password Verification Works", password_verifies)

            # Verify wrong password fails
            wrong_password_fails = not verify_password("WrongPassword123", user.password_hash)
            print_test("Wrong Password Rejected", wrong_password_fails)

            return (
                password_is_hashed and
                is_argon2 and
                password_verifies and
                wrong_password_fails
            )

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_database_consistency():
    """Test that database records match API responses."""
    print_section("Test 7: Database Consistency")

    try:
        # Register a user
        user_data = {
            "name": "Consistency Test",
            "email": "consistency.test@example.com",
            "phone": "+918888888888",
            "password": "ConsistentPass123"
        }
        TEST_USERS.append(user_data["email"])

        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data
        )

        if response.status_code != 201:
            print_test("User Registration", False)
            return False

        api_user = response.json()["user"]
        print_test("User Registration", True)

        # Query database
        session_maker = await get_session_maker()
        async with session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            db_user = result.scalar_one_or_none()

            if not db_user:
                print_test("User in Database", False)
                return False

            print_test("User in Database", True)

            # Compare API response with DB record
            name_matches = db_user.name == api_user["name"] == user_data["name"]
            print_test("Name Consistency", name_matches)

            email_matches = db_user.email == api_user["email"] == user_data["email"]
            print_test("Email Consistency", email_matches)

            phone_matches = db_user.phone == api_user["phone"] == user_data["phone"]
            print_test("Phone Consistency", phone_matches)

            role_matches = db_user.role.value == api_user["role"] == "user"
            print_test("Role Consistency (user)", role_matches)

            points_match = db_user.eco_points == api_user["eco_points"] == 0
            print_test("Eco Points Consistency (0)", points_match)

            uuid_matches = str(db_user.user_id) == api_user["user_id"]
            print_test("User ID Consistency", uuid_matches)

            return all([
                name_matches, email_matches, phone_matches,
                role_matches, points_match, uuid_matches
            ])

    except Exception as e:
        print_test("Exception Handling", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  ECOLOOP USER REGISTRATION API - AUTOMATED TEST SUITE")
    print("=" * 70)
    print(f"  Testing endpoint: {BASE_URL}/api/auth/register")
    print("=" * 70)

    # Initialize database
    init_db()

    # Run tests
    results = []

    # Synchronous tests
    results.append(("Successful Registration", test_successful_registration()))
    results.append(("Registration Without Phone", test_registration_without_phone()))
    results.append(("Duplicate Email Detection", test_duplicate_email()))
    results.append(("Duplicate Phone Detection", test_duplicate_phone()))
    results.append(("Input Validation", test_validation_errors()))

    # Async tests
    results.append(("Password Security", await test_password_security()))
    results.append(("Database Consistency", await test_database_consistency()))

    # Cleanup
    await cleanup_test_users()

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} - {test_name}")

    print("\n" + "=" * 70)
    success_rate = (passed / total) * 100

    if passed == total:
        print(f"  ✅ ALL TESTS PASSED ({passed}/{total}) - 100%")
    else:
        print(f"  ⚠️  TESTS PASSED: {passed}/{total} - {success_rate:.1f}%")
        print(f"  ❌ TESTS FAILED: {total - passed}/{total}")

    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
