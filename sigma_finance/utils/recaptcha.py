"""
reCAPTCHA v3 verification utility.

This module handles verification of reCAPTCHA v3 tokens with Google's API.
"""
import os
import requests
from flask import current_app

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# Minimum score threshold (0.0 to 1.0)
# 0.0 = likely bot, 1.0 = likely human
# 0.5 is a reasonable default
MIN_SCORE_THRESHOLD = 0.5


def verify_recaptcha(token: str, action: str = None) -> dict:
    """
    Verify a reCAPTCHA v3 token with Google's API.

    Args:
        token: The reCAPTCHA token from the frontend
        action: Expected action name (e.g., 'login', 'register')

    Returns:
        dict with keys:
            - success: bool - Whether verification passed
            - score: float - Risk score (0.0 to 1.0, higher = more likely human)
            - action: str - The action name from the token
            - error: str - Error message if verification failed
    """
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")

    # If no secret key configured, skip verification (for development)
    if not secret_key:
        current_app.logger.warning("RECAPTCHA_SECRET_KEY not configured, skipping verification")
        return {"success": True, "score": 1.0, "action": action, "skipped": True}

    # If no token provided, fail verification
    if not token:
        return {"success": False, "score": 0.0, "error": "No reCAPTCHA token provided"}

    try:
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={
                "secret": secret_key,
                "response": token,
            },
            timeout=5
        )
        response.raise_for_status()
        result = response.json()

        # Check if Google verification succeeded
        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            current_app.logger.warning(f"reCAPTCHA verification failed: {error_codes}")
            return {
                "success": False,
                "score": 0.0,
                "error": f"reCAPTCHA verification failed: {', '.join(error_codes)}"
            }

        score = result.get("score", 0.0)
        token_action = result.get("action", "")

        # Check score threshold
        if score < MIN_SCORE_THRESHOLD:
            current_app.logger.warning(f"reCAPTCHA score too low: {score}")
            return {
                "success": False,
                "score": score,
                "action": token_action,
                "error": "Request appears to be automated"
            }

        # Check action matches (if provided)
        if action and token_action != action:
            current_app.logger.warning(
                f"reCAPTCHA action mismatch: expected '{action}', got '{token_action}'"
            )
            return {
                "success": False,
                "score": score,
                "action": token_action,
                "error": "reCAPTCHA action mismatch"
            }

        current_app.logger.info(f"reCAPTCHA verified: score={score}, action={token_action}")
        return {
            "success": True,
            "score": score,
            "action": token_action
        }

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"reCAPTCHA API request failed: {e}")
        # On network error, allow the request to proceed (fail open)
        # This prevents reCAPTCHA issues from blocking legitimate users
        return {"success": True, "score": 0.5, "error": str(e), "fail_open": True}
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA verification error: {e}")
        return {"success": False, "score": 0.0, "error": str(e)}
