"""
Comprehensive tests for Login and JWT Authentication.
Tests login, token validation, /me endpoint, and error cases.
"""

import asyncio
import sys
import time
import requests
from datetime import datetime, timedelta
from jose import jwt
from config import settings
from database import init_db


BASE_URL = "http://127.0.0.1:8000"
TEST_USER_EMAIL = None
TEST_USER_PASSWORD = "TestLogin123"


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


def setup_test_user():
    """Create a test user for login tests."""
    global TEST_USER_EMAIL

    print_section("Setup: Create Test User")

    timestamp = int(time.time())
    TEST_USER_EMAIL = f"login_test_{timestamp}@example.com"

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "name": "Login Test User",
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )

    if response.status_code == 201:
        print_test("Test user created", True, TEST_USER_EMAIL)
        return True
    else:
        print_test("Test user creation failed", False, response.text)
        return False


def test_successful_login():
    """Test successful login with correct credentials."""
    print_section("Test 1: Successful Login")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )

        # Check status code
        status_ok = response.status_code == 200
        print_test("Status Code (200 OK)", status_ok, f"Got {response.status_code}")

        if not status_ok:
            print(f"Response: {response.text}")
            return False

        data = response.json()

        # Check response structure
        has_token = "access_token" in data
        print_test("Access Token Present", has_token)

        has_token_type = data.get("token_type") == "bearer"
        print_test("Token Type is 'bearer'", has_token_type)

        has_user = "user" in data
        print_test("User Object Present", has_user)

        if not has_token or not has_user:
            return False

        # Validate token format (JWT has 3 parts separated by dots)
        token = data["access_token"]
        token_parts = token.split(".")
        valid_jwt_format = len(token_parts) == 3
        print_test("Valid JWT Format (3 parts)", valid_jwt_format, f"{len(token_parts)} parts")

        # Decode token (without verification for testing)
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            has_sub = "sub" in payload
            has_exp = "exp" in payload
            print_test("Token has 'sub' claim (user_id)", has_sub)
            print_test("Token has 'exp' claim (expiry)", has_exp)

            # Check expiry is in the future
            if has_exp:
                exp_time = datetime.fromtimestamp(payload["exp"])
                is_future = exp_time > datetime.utcnow()
                print_test("Token expiry is in future", is_future, exp_time.isoformat())
        except Exception as e:
            print_test("Token decoding", False, str(e))
            return False

        # Validate user object
        user = data["user"]
        email_matches = user["email"] == TEST_USER_EMAIL
        print_test("Email Matches", email_matches)

        has_user_id = "user_id" in user
        print_test("User ID Present", has_user_id)

        no_password = "password" not in user and "password_hash" not in user
        print_test("Password NOT in Response (SECURITY)", no_password)

        # Store token for next tests
        global TEST_ACCESS_TOKEN
        TEST_ACCESS_TOKEN = token

        return all([
            status_ok, has_token, has_token_type, has_user,
            valid_jwt_format, has_sub, has_exp, email_matches,
            has_user_id, no_password
        ])

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_incorrect_password():
    """Test login with incorrect password returns 401."""
    print_section("Test 2: Incorrect Password")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": "WrongPassword123"
            }
        )

        is_401 = response.status_code == 401
        print_test("Returns 401 Unauthorized", is_401, f"Got {response.status_code}")

        if is_401:
            error = response.json()
            has_detail = "detail" in error
            print_test("Error has 'detail' field", has_detail)

            # Check error message doesn't reveal which field is wrong
            detail = error.get("detail", "").lower()
            generic_message = "invalid" in detail and ("email" in detail or "password" in detail)
            print_test("Generic error message", generic_message, error.get("detail"))

            return has_detail and generic_message

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_unknown_email():
    """Test login with non-existent email returns 401."""
    print_section("Test 3: Unknown Email")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": f"nonexistent_{int(time.time())}@example.com",
                "password": "SomePassword123"
            }
        )

        is_401 = response.status_code == 401
        print_test("Returns 401 Unauthorized", is_401, f"Got {response.status_code}")

        if is_401:
            error = response.json()
            has_detail = "detail" in error
            print_test("Error has 'detail' field", has_detail)

            # Check error message is generic (doesn't reveal email doesn't exist)
            detail = error.get("detail", "").lower()
            generic_message = "invalid" in detail
            print_test("Generic error message", generic_message, error.get("detail"))

            return has_detail and generic_message

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_me_endpoint_with_valid_token():
    """Test /me endpoint with valid JWT token."""
    print_section("Test 4: GET /api/auth/me with Valid Token")

    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"}
        )

        is_200 = response.status_code == 200
        print_test("Returns 200 OK", is_200, f"Got {response.status_code}")

        if not is_200:
            print(f"Response: {response.text}")
            return False

        user = response.json()

        # Validate response
        email_matches = user["email"] == TEST_USER_EMAIL
        print_test("Email Matches", email_matches, user["email"])

        has_user_id = "user_id" in user
        print_test("User ID Present", has_user_id)

        has_name = "name" in user
        print_test("Name Present", has_name)

        has_role = "role" in user
        print_test("Role Present", has_role, user.get("role"))

        has_eco_points = "eco_points" in user
        print_test("Eco Points Present", has_eco_points, str(user.get("eco_points")))

        no_password = "password" not in user and "password_hash" not in user
        print_test("Password NOT in Response (SECURITY)", no_password)

        return all([
            is_200, email_matches, has_user_id,
            has_name, has_role, has_eco_points, no_password
        ])

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_me_endpoint_without_token():
    """Test /me endpoint without authentication token."""
    print_section("Test 5: GET /api/auth/me without Token")

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")

        is_403 = response.status_code == 403  # FastAPI returns 403 for missing auth
        print_test("Returns 403 Forbidden", is_403, f"Got {response.status_code}")

        return is_403

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_me_endpoint_with_invalid_token():
    """Test /me endpoint with invalid JWT token."""
    print_section("Test 6: GET /api/auth/me with Invalid Token")

    try:
        # Use a malformed token
        invalid_token = "invalid.token.here"

        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        is_401 = response.status_code == 401
        print_test("Returns 401 Unauthorized", is_401, f"Got {response.status_code}")

        if is_401:
            error = response.json()
            has_detail = "detail" in error
            print_test("Error has 'detail' field", has_detail, error.get("detail"))
            return has_detail

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_me_endpoint_with_expired_token():
    """Test /me endpoint with expired JWT token."""
    print_section("Test 7: GET /api/auth/me with Expired Token")

    try:
        # Create an expired token
        from security import create_access_token

        expired_token = create_access_token(
            data={"sub": "test-user-id"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        is_401 = response.status_code == 401
        print_test("Returns 401 Unauthorized", is_401, f"Got {response.status_code}")

        if is_401:
            error = response.json()
            has_detail = "detail" in error
            print_test("Error has 'detail' field", has_detail, error.get("detail"))
            return has_detail

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_registration_still_works():
    """Verify registration endpoint still works after adding login."""
    print_section("Test 8: Registration Endpoint Still Works")

    try:
        timestamp = int(time.time())
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "name": "New User After Login",
                "email": f"post_login_test_{timestamp}@example.com",
                "password": "NewUserPass123"
            }
        )

        is_201 = response.status_code == 201
        print_test("Registration Returns 201 Created", is_201, f"Got {response.status_code}")

        if is_201:
            data = response.json()
            has_user = "user" in data
            print_test("Registration Response Valid", has_user)
            return has_user

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_login_validation():
    """Test login input validation."""
    print_section("Test 9: Login Input Validation")

    all_passed = True

    # Test invalid email format
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "not-an-email",
                "password": "SomePass123"
            }
        )

        is_422 = response.status_code == 422
        print_test("Invalid Email Format Returns 422", is_422, f"Got {response.status_code}")
        all_passed = all_passed and is_422

    except Exception as e:
        print_test("Invalid Email Test", False, str(e))
        all_passed = False

    # Test missing password
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "test@example.com"
                # Missing password
            }
        )

        is_422 = response.status_code == 422
        print_test("Missing Password Returns 422", is_422, f"Got {response.status_code}")
        all_passed = all_passed and is_422

    except Exception as e:
        print_test("Missing Password Test", False, str(e))
        all_passed = False

    return all_passed


async def cleanup_test_users():
    """Clean up test users."""
    print("\n🧹 Cleaning up test users...")
    # Test users will be cleaned up with test_unique_registration cleanup
    print("✓ Test data preserved for inspection")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  ECOLOOP LOGIN & JWT AUTHENTICATION - TEST SUITE")
    print("=" * 70)
    print(f"  Testing endpoints:")
    print(f"    - POST /api/auth/login")
    print(f"    - GET  /api/auth/me")
    print("=" * 70)

    # Initialize database
    init_db()

    # Setup
    if not setup_test_user():
        print("\n❌ SETUP FAILED - Cannot run tests")
        return 1

    # Run tests
    results = []

    results.append(("Successful Login", test_successful_login()))
    results.append(("Incorrect Password", test_incorrect_password()))
    results.append(("Unknown Email", test_unknown_email()))
    results.append(("GET /me with Valid Token", test_me_endpoint_with_valid_token()))
    results.append(("GET /me without Token", test_me_endpoint_without_token()))
    results.append(("GET /me with Invalid Token", test_me_endpoint_with_invalid_token()))
    results.append(("GET /me with Expired Token", test_me_endpoint_with_expired_token()))
    results.append(("Registration Still Works", test_registration_still_works()))
    results.append(("Login Input Validation", test_login_validation()))

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
    exit_code = main()
    sys.exit(exit_code)
