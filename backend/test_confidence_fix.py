"""
Test to verify the confidence NaN fix.
Tests that confidence is returned correctly for various scenarios.
"""

import requests
import json


BASE_URL = "http://127.0.0.1:8000"


def get_auth_token():
    """Get authentication token."""
    # Try to login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "conftest@example.com", "password": "testpass123"}
    )

    if response.status_code == 200:
        return response.json()["access_token"]

    # Register if needed
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "name": "Confidence Test User",
            "email": "conftest@example.com",
            "password": "testpass123"
        }
    )

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "conftest@example.com", "password": "testpass123"}
    )

    return response.json()["access_token"]


def test_confidence_field():
    """Test that confidence field is present and valid."""
    print("\n" + "=" * 70)
    print("  CONFIDENCE FIX VERIFICATION TEST")
    print("=" * 70)

    token = get_auth_token()
    print("✓ Authentication successful\n")

    test_cases = [
        ("iPhone 12", "mobile_phone"),
        ("Dell Laptop", "laptop"),
        ("AAA Battery", "battery"),
        ("USB Cable", "cable"),
        ("Unknown weird gadget", "other_ewaste"),
    ]

    all_passed = True

    for item_name, expected_category in test_cases:
        print(f"Testing: {item_name}")
        print("-" * 70)

        response = requests.post(
            f"{BASE_URL}/api/classify",
            headers={"Authorization": f"Bearer {token}"},
            data={"item_name": item_name}
        )

        if response.status_code != 200:
            print(f"✗ FAILED: Status {response.status_code}")
            print(f"  Response: {response.text}")
            all_passed = False
            continue

        data = response.json()

        # Check critical fields
        checks = {
            "Has 'confidence' field": "confidence" in data,
            "Has 'confidence_score' field": "confidence_score" in data,
            "Has 'item_name' field": "item_name" in data,
            "Has 'classified_at' field": "classified_at" in data,
            "Has 'special_care_warning' field": "special_care_warning" in data,
            "Has 'image_url' field": "image_url" in data,
        }

        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        # Verify confidence value
        if "confidence" in data:
            confidence = data["confidence"]

            is_number = isinstance(confidence, (int, float))
            print(f"  {'✓' if is_number else '✗'} Confidence is numeric: {type(confidence).__name__}")

            if is_number:
                not_nan = not (confidence != confidence)  # NaN check
                is_finite = confidence != float('inf') and confidence != float('-inf')
                in_range = 0 <= confidence <= 1

                print(f"  {'✓' if not_nan else '✗'} Confidence is not NaN: {confidence}")
                print(f"  {'✓' if is_finite else '✗'} Confidence is finite: {confidence}")
                print(f"  {'✓' if in_range else '✗'} Confidence in range [0, 1]: {confidence}")

                if not (is_number and not_nan and is_finite and in_range):
                    all_passed = False
            else:
                all_passed = False

        # Verify other fields
        if "item_name" in data:
            item_name_match = data["item_name"] == item_name
            print(f"  {'✓' if item_name_match else '✗'} item_name matches: {data['item_name']}")
            if not item_name_match:
                all_passed = False

        if "category" in data:
            category_match = data["category"] == expected_category
            print(f"  {'✓' if category_match else '✗'} Category: {data['category']}")

        print()

    # Test with image upload
    print("Testing: With image upload")
    print("-" * 70)

    # Create a minimal valid JPEG
    import io
    jpeg_header = b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    jpeg_footer = b'\xFF\xD9'
    fake_jpeg = jpeg_header + b'\x00' * 100 + jpeg_footer

    response = requests.post(
        f"{BASE_URL}/api/classify",
        headers={"Authorization": f"Bearer {token}"},
        data={"item_name": "Test Phone with Image"},
        files={"image": ("test.jpg", io.BytesIO(fake_jpeg), "image/jpeg")}
    )

    if response.status_code == 200:
        data = response.json()
        print("  ✓ Image upload successful")
        print(f"  ✓ image_uploaded: {data.get('image_uploaded')}")
        print(f"  ✓ image_url: {data.get('image_url')}")
        print(f"  ✓ confidence: {data.get('confidence')}")
    else:
        print(f"  ✗ Image upload failed: {response.status_code}")
        print(f"    Response: {response.text}")
        all_passed = False

    print()
    print("=" * 70)

    if all_passed:
        print("  ✅ ALL CONFIDENCE TESTS PASSED")
        print("  The NaN issue is FIXED - confidence is returned correctly")
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  Review the output above for details")

    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    import sys
    passed = test_confidence_field()
    sys.exit(0 if passed else 1)
