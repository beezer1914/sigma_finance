"""
Test script to verify security fixes before committing.
Run this from the project root: python test_security_fixes.py
"""
import sys
from sigma_finance.utils.sanitize import sanitize_for_email, sanitize_email_address, sanitize_for_html


def test_email_sanitization():
    """Test that email sanitization prevents header injection"""
    print("\n" + "="*60)
    print("TEST 1: Email Sanitization")
    print("="*60)

    test_cases = [
        {
            "input": "Alice\nBcc: hacker@evil.com",
            "description": "Newline injection attempt",
            "should_remove": "\n"
        },
        {
            "input": "Bob\r\nCc: spy@bad.com",
            "description": "CRLF injection attempt",
            "should_remove": "\r\n"
        },
        {
            "input": "Charlie<script>alert('xss')</script>",
            "description": "XSS in name",
            "should_escape": "<script>"
        },
        {
            "input": "Normal User Name",
            "description": "Normal safe input",
            "expected": "Normal User Name"
        },
        {
            "input": "  Trimmed Name  ",
            "description": "Whitespace trimming",
            "expected": "Trimmed Name"
        }
    ]

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = sanitize_for_email(test["input"])
        print(f"\n  Test {i}: {test['description']}")
        print(f"    Input:  '{test['input']}'")
        print(f"    Output: '{result}'")

        # Check if dangerous characters were removed
        if "should_remove" in test:
            if test["should_remove"] in result:
                print(f"    [FAIL] '{test['should_remove']}' still present!")
                all_passed = False
            else:
                print(f"    [PASS] Dangerous characters removed")

        # Check if HTML was escaped
        elif "should_escape" in test:
            if test["should_escape"] in result:
                print(f"    [FAIL] FAILED: HTML not escaped!")
                all_passed = False
            else:
                print(f"    [PASS] PASSED: HTML escaped correctly")

        # Check exact match
        elif "expected" in test:
            if result == test["expected"]:
                print(f"    [PASS] PASSED: Output matches expected")
            else:
                print(f"    [FAIL] FAILED: Expected '{test['expected']}'")
                all_passed = False

    return all_passed


def test_email_address_validation():
    """Test email address validation"""
    print("\n" + "="*60)
    print("TEST 2: Email Address Validation")
    print("="*60)

    test_cases = [
        ("user@example.com", True, "Valid email"),
        ("invalid-email", False, "Invalid format"),
        ("user@domain", False, "Missing TLD"),
        ("  user@example.com  ", True, "Whitespace trimmed"),
        ("User@Example.COM", True, "Uppercase normalized"),
    ]

    all_passed = True
    for i, (email, should_pass, description) in enumerate(test_cases, 1):
        result = sanitize_email_address(email)
        print(f"\n  Test {i}: {description}")
        print(f"    Input:  '{email}'")
        print(f"    Output: '{result}'")

        if should_pass and result:
            print(f"    [PASS] PASSED: Valid email accepted")
        elif not should_pass and not result:
            print(f"    [PASS] PASSED: Invalid email rejected")
        else:
            print(f"    [FAIL] FAILED: Unexpected result")
            all_passed = False

    return all_passed


def test_csrf_imports():
    """Test that CSRF protection is properly imported"""
    print("\n" + "="*60)
    print("TEST 3: CSRF Protection Setup")
    print("="*60)

    all_passed = True

    # Test extensions import
    print("\n  Checking extensions.py...")
    try:
        from sigma_finance.extensions import csrf
        print("    [PASS] PASSED: CSRF imported in extensions")
    except ImportError as e:
        print(f"    [FAIL] FAILED: Cannot import CSRF - {e}")
        all_passed = False

    # Test app.py uses csrf
    print("\n  Checking app.py initialization...")
    try:
        with open('sigma_finance/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
            if 'csrf.init_app(app)' in app_content:
                print("    [PASS] PASSED: CSRF initialized in app")
            else:
                print("    [FAIL] FAILED: CSRF not initialized")
                all_passed = False
    except Exception as e:
        print(f"    [FAIL] FAILED: Cannot read app.py - {e}")
        all_passed = False

    # Test webhook exemption
    print("\n  Checking webhook CSRF exemption...")
    try:
        with open('sigma_finance/routes/webhooks.py', 'r', encoding='utf-8') as f:
            webhook_content = f.read()
            if '@csrf.exempt' in webhook_content:
                print("    [PASS] PASSED: Webhook exempted from CSRF")
            else:
                print("    [WARN]  WARNING: Webhook may not be exempted")
                # Don't fail, but warn
    except Exception as e:
        print(f"    [FAIL] FAILED: Cannot read webhooks.py - {e}")
        all_passed = False

    return all_passed


def test_template_csrf_tokens():
    """Test that templates have CSRF tokens"""
    print("\n" + "="*60)
    print("TEST 4: CSRF Tokens in Templates")
    print("="*60)

    templates_to_check = [
        ('sigma_finance/templates/treasurer/manage-members.html',
         ['csrf_token()']),
        ('sigma_finance/templates/treasurer/edit_member.html',
         ['csrf_token()']),
        ('sigma_finance/templates/treasurer/invite_dashboard.html',
         ['csrf_token()']),
        ('sigma_finance/templates/treasurer/members.html',
         ['csrf_token()']),
    ]

    all_passed = True
    for template_path, required_tokens in templates_to_check:
        print(f"\n  Checking {template_path.split('/')[-1]}...")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for token in required_tokens:
                    if token in content:
                        print(f"    [PASS] PASSED: Contains {token}")
                    else:
                        print(f"    [FAIL] FAILED: Missing {token}")
                        all_passed = False
        except FileNotFoundError:
            print(f"    [FAIL] FAILED: Template not found")
            all_passed = False
        except Exception as e:
            print(f"    [FAIL] FAILED: Error reading template - {e}")
            all_passed = False

    return all_passed


def test_confirmation_flow():
    """Test that reset confirmation is implemented"""
    print("\n" + "="*60)
    print("TEST 5: Reset Confirmation Flow")
    print("="*60)

    all_passed = True

    # Check confirmation template exists
    print("\n  Checking confirmation template...")
    try:
        with open('sigma_finance/templates/treasurer/confirm_reset.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DELETE' in content and 'csrf_token()' in content:
                print("    [PASS] PASSED: Confirmation template exists with CSRF")
            else:
                print("    [FAIL] FAILED: Template missing required elements")
                all_passed = False
    except FileNotFoundError:
        print("    [FAIL] FAILED: Confirmation template not found")
        all_passed = False

    # Check route exists
    print("\n  Checking confirmation route...")
    try:
        with open('sigma_finance/routes/treasurer.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'treasurer_confirm_reset_user' in content:
                print("    [PASS] PASSED: Confirmation route exists")
            else:
                print("    [FAIL] FAILED: Confirmation route not found")
                all_passed = False

            # Check DELETE validation
            if 'confirm" != "DELETE' in content or "confirm') != 'DELETE" in content:
                print("    [PASS] PASSED: DELETE validation implemented")
            else:
                print("    [WARN]  WARNING: DELETE validation may be missing")
    except FileNotFoundError:
        print("    [FAIL] FAILED: treasurer.py not found")
        all_passed = False

    # Check manage-members links to confirmation
    print("\n  Checking manage-members links to confirmation...")
    try:
        with open('sigma_finance/templates/treasurer/manage-members.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'treasurer_confirm_reset_user' in content:
                print("    [PASS] PASSED: Links to confirmation page")
            else:
                print("    [FAIL] FAILED: Still uses direct POST")
                all_passed = False
    except FileNotFoundError:
        print("    [FAIL] FAILED: manage-members.html not found")
        all_passed = False

    return all_passed


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SECURITY FIXES VERIFICATION SUITE")
    print("=" * 60)

    results = {
        "Email Sanitization": test_email_sanitization(),
        "Email Validation": test_email_address_validation(),
        "CSRF Setup": test_csrf_imports(),
        "CSRF Templates": test_template_csrf_tokens(),
        "Confirmation Flow": test_confirmation_flow(),
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"
        print(f"  {test_name:.<40} {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("*** ALL TESTS PASSED! Ready to commit. ***")
    else:
        print("*** SOME TESTS FAILED. Review failures before committing. ***")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
