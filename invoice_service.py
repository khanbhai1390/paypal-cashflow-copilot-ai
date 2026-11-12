
from datetime import date, timedelta

import requests
from paypal_service import get_access_token


PAYPAL_INVOICES_URL = (
    "https://api-m.sandbox.paypal.com/v2/invoicing/invoices"
)


def _headers():
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }


def get_invoices():
    """Get invoice summaries and fetch full details for each invoice."""
    response = requests.get(
        PAYPAL_INVOICES_URL,
        headers=_headers(),
        params={"page": 1, "page_size": 100},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Could not retrieve invoices: HTTP {response.status_code}. "
            f"{response.text}"
        )

    summaries = response.json().get("items", [])
    full_invoices = []

    for summary in summaries:
        invoice_id = summary.get("id")

        if not invoice_id:
            full_invoices.append(summary)
            continue

        try:
            detail_response = requests.get(
                f"{PAYPAL_INVOICES_URL}/{invoice_id}",
                headers=_headers(),
                timeout=30,
            )

            if detail_response.status_code == 200:
                full_invoice = detail_response.json()

                for key, value in summary.items():
                    full_invoice.setdefault(key, value)

                full_invoices.append(full_invoice)
            else:
                full_invoices.append(summary)

        except requests.RequestException:
            full_invoices.append(summary)

    return full_invoices


def create_draft_invoice(
    customer_email,
    item_name,
    amount,
    currency="USD",
    due_in_days=7,
):
    """Create a draft invoice in PayPal Sandbox."""

    if not customer_email or not item_name:
        raise ValueError("Customer email and item name are required.")

    try:
        amount = float(amount)
        due_in_days = int(due_in_days)
    except (TypeError, ValueError):
        raise ValueError("Enter a valid amount and due period.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if due_in_days < 1:
        raise ValueError("Due days must be at least one.")

    currency = currency.upper()
    due_date = (
        date.today() + timedelta(days=due_in_days)
    ).isoformat()

    invoice_data = {
        "detail": {
            "currency_code": currency,
            "note": "Created by CashFlow Copilot AI - Sandbox test",
            "payment_term": {
                "due_date": due_date
            },
        },
        "primary_recipients": [
            {
                "billing_info": {
                    "email_address": customer_email.strip()
                }
            }
        ],
        "items": [
            {
                "name": item_name.strip(),
                "quantity": "1",
                "unit_amount": {
                    "currency_code": currency,
                    "value": f"{amount:.2f}",
                },
            }
        ],
    }

    response = requests.post(
        PAYPAL_INVOICES_URL,
        headers=_headers(),
        json=invoice_data,
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Invoice creation failed: HTTP {response.status_code}. "
            f"{response.text}"
        )

    result = response.json()
    result.setdefault("items", invoice_data["items"])
    result.setdefault("detail", invoice_data["detail"])

    return result


def send_invoice(invoice_id):
    """Send an existing draft invoice using PayPal Sandbox."""

    if not invoice_id or not str(invoice_id).strip():
        raise ValueError("Invoice ID is required.")

    response = requests.post(
        f"{PAYPAL_INVOICES_URL}/{invoice_id}/send",
        headers=_headers(),
        json={},
        timeout=30,
    )

    if response.status_code not in (200, 202, 204):
        raise RuntimeError(
            f"Could not send invoice: HTTP {response.status_code}. "
            f"{response.text}"
        )

    return {
        "success": True,
        "invoice_id": invoice_id,
        "message": "PayPal accepted the invoice send request.",
    }


def analyze_invoice(invoice):
    """Prepare invoice details for the dashboard."""

    detail = invoice.get("detail") or {}
    status = (invoice.get("status") or "UNKNOWN").upper()

    invoice_id = (
        invoice.get("id")
        or invoice.get("invoice_id")
        or "N/A"
    )

    payment_term = detail.get("payment_term") or {}
    due_date = payment_term.get("due_date")

    items = invoice.get("items") or []
    service_names = [
        str(item.get("name", "")).strip()
        for item in items
        if item.get("name")
    ]

    service_name = (
        ", ".join(service_names)
        if service_names
        else "Service not specified"
    )

    currency = detail.get("currency_code") or "USD"
    total_amount = 0.0

    for item in items:
        unit_amount = item.get("unit_amount") or {}
        currency = unit_amount.get("currency_code") or currency

        try:
            quantity = float(item.get("quantity") or 1)
            price = float(unit_amount.get("value") or 0)
            total_amount += quantity * price
        except (TypeError, ValueError):
            continue

    # Prefer PayPal's actual invoice total when available.
    # Do not use due_amount as the invoice total: it can represent
    # the remaining balance rather than the original invoice amount.
    amount_summary = invoice.get("amount") or {}

    if amount_summary.get("value") is not None:
        try:
            total_amount = float(amount_summary["value"])
            currency = amount_summary.get("currency_code") or currency
        except (TypeError, ValueError):
            pass

    overdue = False
    overdue_days = 0

    if due_date and status not in (
        "PAID", "CANCELLED", "REFUNDED"
    ):
        try:
            overdue_days = max(
                0, (date.today() - date.fromisoformat(due_date)).days
            )
            overdue = overdue_days > 0
        except ValueError:
            overdue_days = 0

    if status == "PAID":
        suggestion = "Payment received. Keep this invoice for your records."
    elif overdue:
        suggestion = "This invoice is overdue. Prepare a polite payment reminder."
    elif status in ("DRAFT", "SAVED"):
        suggestion = "Review the invoice and send it to the customer when ready."
    elif status in ("SENT", "SCHEDULED", "UNPAID", "PARTIALLY_PAID"):
        suggestion = "Track this invoice and follow up near its due date."
    elif status in ("CANCELLED", "REFUNDED"):
        suggestion = "No payment follow-up is needed for this invoice."
    else:
        suggestion = "Review the invoice status and decide the next action."

    return {
        "id": invoice_id,
        "invoice_id": invoice_id,
        "service_name": service_name,
        "amount": f"{total_amount:.2f}",
        "currency": currency,
        "status": status,
        "due_date": due_date or "Not set",
        "overdue": overdue,
        "overdue_days": overdue_days,
        "suggestion": suggestion,
    }
