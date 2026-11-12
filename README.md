# PayPal CashFlow Copilot AI

An AI-powered invoice and cash-flow assistant built using Python, Flask, and PayPal Sandbox.

## About the Project

PayPal CashFlow Copilot AI helps small businesses manage invoices, monitor overdue payments, and understand their cash-flow position.

It combines PayPal's invoicing capabilities with AI-based invoice analysis to provide useful payment suggestions.

## Key Features

- PayPal Sandbox connection
- Create draft invoices
- Send invoices through PayPal
- View and manage invoice statuses
- Identify overdue invoices
- AI-powered invoice analysis and suggestions
- Cash-flow overview with currency-wise estimates

## Technology Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- PayPal Invoicing API
- AI-based invoice analysis

## Run Locally

1. Clone this repository.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Create your own local `.env` file.
4. Add your PayPal Sandbox credentials using the environment variable names expected by `paypal_service.py`.
5. Start the application:

   `python app.py`

6. Open `http://127.0.0.1:5000` in your browser.

## Testing

This project was tested using PayPal Sandbox accounts and test invoices.

## Security

Never upload `.env`, PayPal Client Secrets, access tokens, or real customer information.

This project is a prototype and uses PayPal Sandbox for testing.