"""
Comprehensive tests for E-Waste Classification API.
Tests classification endpoint, file validation, and baseline classifier.
"""

import sys
import time
import requests
from pathlib import Path
import io


BASE_URL = "http://127.0.0.1:8000"
TEST_USER_EMAIL = None
TEST_ACCESS_TOKEN = None


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
    """Create a test user and login."""
    global TEST_USER_EMAIL, TEST_ACCESS_TOKEN

    print_section("Setup: Create Test User and Login")

    timestamp = int(time.time())
    TEST_USER_EMAIL = f"classify_test_{timestamp}@example.com"

    # Register
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "name": "Classification Test User",
            "email": TEST_USER_EMAIL,
            "password": "ClassifyTest123"
        }
    )

    if response.status_code == 201:
        print_test("Test user registered", True, TEST_USER_EMAIL)
    else:
        print_test("Test user registration failed", False, response.text)
        return False

    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": "ClassifyTest123"
        }
    )

    if response.status_code == 200:
        data = response.json()
        TEST_ACCESS_TOKEN = data["access_token"]
        print_test("Login successful", True, f"Token: {TEST_ACCESS_TOKEN[:20]}...")
        return True
    else:
        print_test("Login failed", False, response.text)
        return False


def test_get_categories():
    """Test getting supported categories."""
    print_section("Test 1: Get Supported Categories")

    try:
        response = requests.get(f"{BASE_URL}/api/classify/categories")

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            return False

        data = response.json()

        has_categories = "categories" in data
        print_test("Has 'categories' field", has_categories)

        has_total = "total" in data
        print_test("Has 'total' field", has_total)

        if has_categories:
            categories = data["categories"]
            expected_categories = [
                "mobile_phone", "laptop", "battery", "cable", "monitor",
                "keyboard", "mouse", "tablet", "printer", "hard_drive",
                "router", "camera", "other_ewaste"
            ]

            all_present = all(cat in categories for cat in expected_categories)
            print_test(
                "All expected categories present",
                all_present,
                f"Found {len(categories)} categories"
            )

            return is_200 and has_categories and has_total and all_present

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_classify_mobile_phone():
    """Test classifying a mobile phone."""
    print_section("Test 2: Classify Mobile Phone")

    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "Old Samsung Galaxy phone"}
        )

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            print(f"Response: {response.text}")
            return False

        data = response.json()

        # Check response structure
        has_classification_id = "classification_id" in data
        print_test("Has classification_id", has_classification_id)

        has_category = "category" in data
        print_test("Has category", has_category)

        category_correct = data.get("category") == "mobile_phone"
        print_test("Category is 'mobile_phone'", category_correct, data.get("category"))

        has_confidence = "confidence_score" in data
        confidence = data.get("confidence_score", 0)
        confidence_valid = 0 <= confidence <= 1
        print_test(
            "Confidence score valid (0-1)",
            confidence_valid,
            f"{confidence:.3f}"
        )

        has_safety_tips = "safety_tips" in data and len(data.get("safety_tips", [])) > 0
        print_test("Has safety tips", has_safety_tips, f"{len(data.get('safety_tips', []))} tips")

        has_special_care = "special_care_needed" in data
        special_care = data.get("special_care_needed", False)
        print_test("Special care needed flag", has_special_care, str(special_care))

        has_warning = "warning" in data
        warning = data.get("warning", "")
        baseline_warning = "baseline" in warning.lower()
        print_test("Baseline classifier warning present", baseline_warning, warning[:50])

        return all([
            is_200, has_classification_id, has_category, category_correct,
            has_confidence, confidence_valid, has_safety_tips,
            has_special_care, baseline_warning
        ])

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_classify_laptop():
    """Test classifying a laptop."""
    print_section("Test 3: Classify Laptop")

    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "MacBook Pro 2015"}
        )

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            return False

        data = response.json()

        category_correct = data.get("category") == "laptop"
        print_test("Category is 'laptop'", category_correct, data.get("category"))

        has_weight = "estimated_weight_kg" in data and data.get("estimated_weight_kg") is not None
        weight = data.get("estimated_weight_kg", 0)
        print_test("Has estimated weight", has_weight, f"{weight} kg")

        return is_200 and category_correct and has_weight

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_classify_battery():
    """Test classifying a battery (high-risk item)."""
    print_section("Test 4: Classify Battery (High Risk)")

    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "lithium battery"}
        )

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            return False

        data = response.json()

        category_correct = data.get("category") == "battery"
        print_test("Category is 'battery'", category_correct, data.get("category"))

        special_care = data.get("special_care_needed", False)
        print_test("Special care needed = True", special_care, str(special_care))

        safety_tips = data.get("safety_tips", [])
        has_critical_warning = any("CRITICAL" in tip or "⚠️" in tip for tip in safety_tips)
        print_test("Has critical safety warning", has_critical_warning)

        return is_200 and category_correct and special_care and has_critical_warning

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_classify_unknown_item():
    """Test classifying an unknown/unrecognized item."""
    print_section("Test 5: Classify Unknown Item")

    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "random unknown gadget thing"}
        )

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            return False

        data = response.json()

        category_is_other = data.get("category") == "other_ewaste"
        print_test("Category is 'other_ewaste'", category_is_other, data.get("category"))

        low_confidence = data.get("confidence_score", 1.0) < 0.5
        print_test(
            "Low confidence for unknown",
            low_confidence,
            f"{data.get('confidence_score', 0):.3f}"
        )

        return is_200 and category_is_other and low_confidence

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_invalid_input():
    """Test validation of invalid inputs."""
    print_section("Test 6: Invalid Input Validation")

    all_passed = True

    # Test empty item name
    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "   "}
        )

        is_400 = response.status_code == 400
        print_test("Empty item name returns 400", is_400, f"Got {response.status_code}")
        all_passed = all_passed and is_400

    except Exception as e:
        print_test("Empty item name test", False, str(e))
        all_passed = False

    # Test without authentication
    try:
        response = requests.post(
            f"{BASE_URL}/api/classify",
            data={"item_name": "test phone"}
        )

        is_403 = response.status_code == 403
        print_test("No auth token returns 403", is_403, f"Got {response.status_code}")
        all_passed = all_passed and is_403

    except Exception as e:
        print_test("No auth test", False, str(e))
        all_passed = False

    return all_passed


def test_file_type_validation():
    """Test file type validation for image uploads."""
    print_section("Test 7: File Type Validation")

    try:
        # Create a fake text file
        fake_file = io.BytesIO(b"This is not an image")

        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
            data={"item_name": "test phone"},
            files={"image": ("test.txt", fake_file, "text/plain")}
        )

        is_400 = response.status_code == 400
        print_test("Invalid file type returns 400", is_400, f"Got {response.status_code}")

        if is_400:
            error = response.json()
            has_detail = "detail" in error
            mentions_type = "type" in error.get("detail", "").lower()
            print_test("Error mentions file type", mentions_type, error.get("detail"))
            return has_detail and mentions_type

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_classification_history():
    """Test getting classification history."""
    print_section("Test 8: Classification History")

    try:
        response = requests.get(
            f"{BASE_URL}/api/classify/history",
            headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"}
        )

        is_200 = response.status_code == 200
        print_test("Status Code (200 OK)", is_200, f"Got {response.status_code}")

        if not is_200:
            return False

        data = response.json()

        has_classifications = "classifications" in data
        print_test("Has 'classifications' field", has_classifications)

        has_total = "total" in data
        print_test("Has 'total' field", has_total)

        if has_classifications:
            classifications = data["classifications"]
            # We created several classifications in previous tests
            has_records = len(classifications) >= 4
            print_test(
                "Has classification records",
                has_records,
                f"Found {len(classifications)} records"
            )

            return is_200 and has_classifications and has_total and has_records

        return False

    except Exception as e:
        print_test("Exception", False, str(e))
        return False


def test_baseline_classifier():
    """Test various items to verify baseline classifier behavior."""
    print_section("Test 9: Baseline Classifier Behavior")

    test_items = [
        ("iPhone 12", "mobile_phone"),
        ("Dell laptop", "laptop"),
        ("USB cable", "cable"),
        ("LED monitor", "monitor"),
        ("computer mouse", "mouse"),  # Changed to be more specific
        ("iPad tablet", "tablet"),
    ]

    all_passed = True

    for item_name, expected_category in test_items:
        try:
            response = requests.post(
                f"{BASE_URL}/api/classify",
                headers={"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"},
                data={"item_name": item_name}
            )

            if response.status_code == 200:
                data = response.json()
                category = data.get("category")
                passed = category == expected_category
                print_test(
                    f"'{item_name}' → '{expected_category}'",
                    passed,
                    f"Got '{category}'"
                )
                all_passed = all_passed and passed
            else:
                print_test(f"'{item_name}' classification", False, f"Status {response.status_code}")
                all_passed = False

        except Exception as e:
            print_test(f"'{item_name}' classification", False, str(e))
            all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  ECOLOOP E-WASTE CLASSIFICATION API - TEST SUITE")
    print("=" * 70)
    print(f"  Testing endpoint: {BASE_URL}/api/classify")
    print("=" * 70)

    # Setup
    if not setup_test_user():
        print("\n❌ SETUP FAILED - Cannot run tests")
        return 1

    # Run tests
    results = []

    results.append(("Get Supported Categories", test_get_categories()))
    results.append(("Classify Mobile Phone", test_classify_mobile_phone()))
    results.append(("Classify Laptop", test_classify_laptop()))
    results.append(("Classify Battery (High Risk)", test_classify_battery()))
    results.append(("Classify Unknown Item", test_classify_unknown_item()))
    results.append(("Invalid Input Validation", test_invalid_input()))
    results.append(("File Type Validation", test_file_type_validation()))
    results.append(("Classification History", test_classification_history()))
    results.append(("Baseline Classifier Behavior", test_baseline_classifier()))

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
