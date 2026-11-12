
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAYPAL_BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")


def get_access_token():
    """Get a temporary OAuth access token from PayPal Sandbox."""

    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError(
            "PayPal credentials are missing. Check your .env file."
        )

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        data={"grant_type": "client_credentials"},
        timeout=20
    )

    if not response.ok:
        raise RuntimeError(
            f"PayPal authentication failed (HTTP {response.status_code}). "
            "Check your Sandbox credentials and app configuration."
        )

    return response.json()["access_token"]


def test_paypal_connection():
    """Check whether PayPal Sandbox authentication works."""

    token = get_access_token()

    if token:
        return "PayPal Sandbox connection successful!"

    return "Could not connect to PayPal Sandbox."
