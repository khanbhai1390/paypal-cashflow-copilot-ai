
from datetime import date
from flask import Flask, render_template_string, request, jsonify

from invoice_service import (
    get_invoices,
    create_draft_invoice,
    analyze_invoice,
    send_invoice,
)
from paypal_service import test_paypal_connection

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CashFlow Copilot AI</title>

<style>
:root {
    --navy: #101d3a;
    --blue: #2463eb;
    --blue-soft: #edf3ff;
    --ink: #172033;
    --muted: #718096;
    --line: #e8edf5;
    --surface: #ffffff;
    --page: #f5f7fb;
    --green: #16865b;
    --red: #d84b59;
    --amber: #b7791f;
    --shadow: 0 12px 35px rgba(26, 43, 77, .06);
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    margin: 0;
    background: var(--page);
    color: var(--ink);
    font-family: Inter, Arial, sans-serif;
}

button, input, select { font: inherit; }
button { cursor: pointer; }

.app-shell { min-height: 100vh; }

.sidebar {
    width: 248px;
    position: fixed;
    inset: 0 auto 0 0;
    display: flex;
    flex-direction: column;
    padding: 26px 17px 20px;
    background: linear-gradient(180deg, var(--navy), #14284b);
    color: white;
    z-index: 5;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 2px 9px 32px;
}

.brand-mark {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #6ca3ff, #2e65df);
    font-size: 19px;
    font-weight: 800;
    box-shadow: 0 7px 18px #07142d66;
}

.brand-name {
    font-size: 15px;
    font-weight: 750;
}

.brand-sub {
    margin-top: 3px;
    color: #a9bad8;
    font-size: 11px;
}

.nav-label {
    padding: 0 11px 10px;
    color: #8295b8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #bdcbe2;
    text-decoration: none;
    padding: 12px 13px;
    border-radius: 10px;
    margin: 3px 0;
    font-size: 13px;
    font-weight: 600;
    transition: .18s ease;
}

.nav-link:hover,
.nav-link.active {
    color: white;
    background: #ffffff16;
}

.nav-icon {
    width: 20px;
    text-align: center;
    font-size: 16px;
}

.sidebar-spacer { flex: 1; }

.sandbox-card {
    border: 1px solid #ffffff20;
    background: #ffffff0c;
    padding: 14px;
    border-radius: 13px;
}

.sandbox-title {
    font-size: 12px;
    font-weight: 700;
}

.sandbox-note {
    color: #9fb0ce;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 6px;
}

.sandbox-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #b9f4d8;
    background: #1d80523d;
    padding: 5px 8px;
    border-radius: 20px;
    margin-top: 10px;
    font-size: 10px;
    font-weight: 800;
}

.main {
    margin-left: 248px;
    min-height: 100vh;
}

.topbar {
    height: 76px;
    background: #ffffffd9;
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 38px;
    position: sticky;
    top: 0;
    z-index: 4;
}

.breadcrumb {
    color: var(--muted);
    font-size: 12px;
}

.breadcrumb strong {
    color: var(--ink);
}

.top-actions {
    display: flex;
    align-items: center;
    gap: 13px;
}

.connection-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 11px;
    border: 1px solid var(--line);
    border-radius: 30px;
    background: white;
    font-size: 11px;
    color: #536179;
}

.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #d69a36;
}

.dot.online {
    background: #21a36c;
    box-shadow: 0 0 0 3px #21a36c1a;
}

.refresh-btn,
.primary-btn,
.secondary-btn,
.send-btn {
    border: 0;
    border-radius: 9px;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 750;
    transition: .18s ease;
}

.refresh-btn {
    color: #30415f;
    background: #f0f3f9;
    border: 1px solid #e6ebf3;
}

.refresh-btn:hover,
.secondary-btn:hover {
    background: #e6ecf7;
}

.primary-btn {
    color: white;
    background: var(--blue);
    box-shadow: 0 6px 14px #2463eb25;
}

.primary-btn:hover {
    background: #174fc9;
    transform: translateY(-1px);
}

button:disabled {
    opacity: .6;
    cursor: not-allowed;
}

.content {
    max-width: 1440px;
    padding: 31px 38px 48px;
    margin: 0 auto;
}

.welcome {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 20px;
    margin-bottom: 25px;
}

.eyebrow {
    color: var(--blue);
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.3px;
}

h1 {
    margin: 7px 0;
    font-size: clamp(24px, 3vw, 31px);
    letter-spacing: -1px;
}

.welcome p {
    color: var(--muted);
    font-size: 13px;
    margin: 0;
    line-height: 1.6;
}

.date-label {
    color: var(--muted);
    font-size: 11px;
    white-space: nowrap;
    padding-bottom: 4px;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    margin: 28px 0 14px;
}

.section-heading h2 {
    font-size: 15px;
    margin: 0;
}

.section-heading p {
    color: var(--muted);
    font-size: 11px;
    margin: 5px 0 0;
}

.metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 15px;
}

.metric-card,
.panel {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 15px;
    box-shadow: var(--shadow);
}

.metric-card {
    padding: 18px 19px;
    min-width: 0;
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
}

.metric-label {
    color: var(--muted);
    font-size: 11px;
    font-weight: 650;
}

.metric-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-size: 15px;
    background: var(--blue-soft);
    color: var(--blue);
}

.metric-icon.red {
    color: var(--red);
    background: #fff0f1;
}

.metric-icon.green {
    color: var(--green);
    background: #eaf8f1;
}

.metric-icon.amber {
    color: var(--amber);
    background: #fff7e8;
}

.metric-value {
    font-size: 27px;
    font-weight: 780;
    letter-spacing: -.9px;
    margin-top: 13px;
}

.metric-foot {
    color: #9aa5b6;
    font-size: 10px;
    margin-top: 5px;
}

.work-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.3fr) minmax(270px, .7fr);
    gap: 17px;
    align-items: stretch;
}

.panel {
    padding: 21px;
    min-width: 0;
}

.panel-title {
    font-size: 14px;
    font-weight: 780;
    margin: 0;
}

.panel-subtitle {
    color: var(--muted);
    font-size: 11px;
    margin: 5px 0 0;
    line-height: 1.5;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 13px;
}

.field.full {
    grid-column: 1 / -1;
}

label {
    display: block;
    color: #46536a;
    font-size: 11px;
    font-weight: 750;
    margin: 15px 0 7px;
}

input, select {
    width: 100%;
    border: 1px solid #dfe5ee;
    border-radius: 9px;
    background: white;
    color: var(--ink);
    padding: 11px 12px;
    font-size: 12px;
    outline: none;
    transition: .18s ease;
}

input:focus, select:focus {
    border-color: #7ea5f7;
    box-shadow: 0 0 0 3px #2463eb13;
}

input::placeholder { color: #aab3c1; }

.helper {
    color: #98a2b2;
    font-size: 10px;
    margin: 6px 0 0;
}

.form-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 17px;
    flex-wrap: wrap;
}

.form-actions .primary-btn { margin: 0; }

#message {
    color: #526078;
    font-size: 11px;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

#message.error { color: var(--red); }
#message.success { color: var(--green); }

.connection-panel {
    background: linear-gradient(145deg, #14284b, #1e3c6c);
    color: white;
    border: 0;
    position: relative;
    overflow: hidden;
}

.connection-panel:after {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    border: 1px solid #ffffff12;
    border-radius: 50%;
    right: -80px;
    top: -78px;
    box-shadow: 0 0 0 24px #ffffff08, 0 0 0 48px #ffffff05;
}

.connection-panel .panel-subtitle { color: #b4c4de; }
.connection-panel .panel-title { position: relative; z-index: 1; }

.paypal-mark {
    display: grid;
    place-items: center;
    width: 43px;
    height: 43px;
    background: #ffffff16;
    border: 1px solid #ffffff20;
    border-radius: 13px;
    color: white;
    font-weight: 900;
    font-size: 18px;
    margin: 23px 0 14px;
    position: relative;
    z-index: 1;
}

.connection-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 700;
    position: relative;
    z-index: 1;
}

.connection-panel .dot { background: #e5b65d; }
.connection-panel .dot.online { background: #4be0a0; }

.connection-detail {
    color: #b4c4de;
    font-size: 10px;
    line-height: 1.6;
    margin-top: 8px;
    position: relative;
    z-index: 1;
}

.connection-panel .secondary-btn {
    background: #ffffff18;
    color: white;
    border: 1px solid #ffffff24;
    margin-top: 20px;
    position: relative;
    z-index: 1;
}

.connection-panel .secondary-btn:hover {
    background: #ffffff2a;
}

.outstanding-list {
    margin-top: 17px;
    border-top: 1px solid #ffffff20;
    padding-top: 13px;
    position: relative;
    z-index: 1;
}

.outstanding-title {
    color: #b4c4de;
    font-size: 10px;
    font-weight: 700;
}

.currency-line {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-top: 10px;
    font-size: 12px;
}

.currency-line strong { font-size: 13px; }

.table-panel { margin-top: 18px; }

.table-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-wrap { width: min(250px, 100%); }
.filter-wrap { width: 130px; }
.invoice-list { margin-top: 17px; }

.invoice-head,
.invoice-row {
    display: grid;
    grid-template-columns:
        minmax(180px, 1.6fr)
        minmax(95px, .7fr)
        minmax(95px, .7fr)
        minmax(90px, .6fr)
        minmax(160px, 1.2fr)
        105px;
    gap: 12px;
    align-items: center;
}

.invoice-head {
    color: #929daf;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: .8px;
    text-transform: uppercase;
    padding: 0 12px 11px;
    border-bottom: 1px solid var(--line);
}

.invoice-row {
    padding: 14px 12px;
    border-bottom: 1px solid #f0f2f6;
    font-size: 11px;
    min-width: 700px;
}

.invoice-row:last-child { border-bottom: 0; }

.invoice-name {
    color: #26344d;
    font-weight: 750;
    overflow-wrap: anywhere;
}

.invoice-id {
    color: #a0a9b7;
    font-size: 9px;
    margin-top: 4px;
    overflow-wrap: anywhere;
}

.invoice-amount {
    font-weight: 750;
    color: #26344d;
}

.invoice-due { color: #6e7b90; }

.status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    padding: 5px 8px;
    width: fit-content;
    background: #f0f3f8;
    color: #657187;
    font-size: 9px;
    font-weight: 850;
}

.status-badge.sent,
.status-badge.paid {
    background: #e9f8f0;
    color: #16865b;
}

.status-badge.draft,
.status-badge.saved {
    background: #fff6e6;
    color: #a56b12;
}

.status-badge.overdue {
    background: #fff0f1;
    color: #c43d4b;
}

.suggestion-text {
    color: #7a8799;
    font-size: 10px;
    line-height: 1.5;
}

.send-btn {
    background: #eaf8f1;
    color: #16865b;
    padding: 8px 10px;
    font-size: 10px;
    margin: 0;
}

.send-btn:hover { background: #d8f2e5; }

.empty-state {
    padding: 35px 15px;
    text-align: center;
    color: var(--muted);
    border: 1px dashed #dce3ee;
    border-radius: 12px;
    font-size: 12px;
}

.empty-icon {
    font-size: 24px;
    margin-bottom: 9px;
}

.mobile-invoices { overflow-x: auto; }

.footnote {
    color: #9aa4b3;
    font-size: 10px;
    line-height: 1.6;
    margin-top: 12px;
}

@media (max-width: 1100px) {
    .metrics {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 850px) {
    .sidebar {
        width: 70px;
        padding: 20px 9px;
    }

    .brand {
        justify-content: center;
        padding: 2px 0 28px;
    }

    .brand-copy,
    .nav-label,
    .nav-text,
    .sandbox-card {
        display: none;
    }

    .nav-link {
        justify-content: center;
        padding: 13px 5px;
    }

    .nav-icon { font-size: 18px; }
    .main { margin-left: 70px; }
    .topbar { padding: 0 22px; }
    .content { padding: 26px 22px 40px; }
    .work-grid { grid-template-columns: 1fr; }
}

@media (max-width: 580px) {
    .topbar {
        height: 65px;
        padding: 0 14px;
    }

    .breadcrumb { font-size: 10px; }
    .connection-indicator { display: none; }

    .content { padding: 22px 13px 32px; }
    .welcome { display: block; }
    .date-label { margin-top: 13px; }

    .metrics {
        grid-template-columns: 1fr 1fr;
        gap: 9px;
    }

    .metric-card { padding: 14px; }
    .metric-value { font-size: 22px; }
    .metric-label { font-size: 10px; }
    .panel { padding: 16px; }
    .form-grid { grid-template-columns: 1fr; }
    .field.full { grid-column: auto; }

    .table-toolbar {
        align-items: stretch;
        flex-direction: column;
    }

    .search-wrap,
    .filter-wrap {
        width: 100%;
    }

    .refresh-btn { padding: 9px 10px; }
}
</style>
</head>

<body>
<div class="app-shell">

    <aside class="sidebar">

        <div class="brand">
            <div class="brand-mark">C</div>

            <div class="brand-copy">
                <div class="brand-name">CashFlow Copilot</div>
                <div class="brand-sub">AI INVOICE ASSISTANT</div>
            </div>
        </div>

        <div class="nav-label">Workspace</div>

        <a class="nav-link active" href="#overview">
            <span class="nav-icon">▦</span>
            <span class="nav-text">Overview</span>
        </a>

        <a class="nav-link" href="#create">
            <span class="nav-icon">＋</span>
            <span class="nav-text">Create invoice</span>
        </a>

        <a class="nav-link" href="#invoices">
            <span class="nav-icon">▤</span>
            <span class="nav-text">Invoices</span>
        </a>

        <div class="sidebar-spacer"></div>

        <div class="sandbox-card">
            <div class="sandbox-title">Development environment</div>

            <div class="sandbox-note">
                This prototype uses PayPal Sandbox.
                Use test accounts and test customer details.
            </div>

            <div class="sandbox-pill">● SANDBOX MODE</div>
        </div>

    </aside>

    <div class="main">

        <header class="topbar">

            <div class="breadcrumb">
                Workspace / <strong>Overview</strong>
            </div>

            <div class="top-actions">

                <div class="connection-indicator">
                    <span id="topDot" class="dot"></span>
                    <span id="topConnection">Checking PayPal...</span>
                </div>

                <button class="refresh-btn"
                        type="button"
                        onclick="refreshDashboard()">
                    ↻ Refresh
                </button>

            </div>
        </header>

        <main class="content" id="overview">

            <section class="welcome">

                <div>
                    <div class="eyebrow">FINANCIAL WORKSPACE</div>

                    <h1>Good to see you.</h1>

                    <p>
                        Keep invoices organized, spot overdue payments,
                        and stay on top of your cash flow.
                    </p>
                </div>

                <div class="date-label" id="todayLabel"></div>

            </section>

            <section class="metrics">

                <article class="metric-card">
                    <div class="metric-top">
                        <div class="metric-label">Total invoices</div>
                        <div class="metric-icon">▤</div>
                    </div>

                    <div class="metric-value" id="totalInvoices">0</div>

                    <div class="metric-foot">
                        Invoices available in your account
                    </div>
                </article>

                <article class="metric-card">
                    <div class="metric-top">
                        <div class="metric-label">Overdue invoices</div>
                        <div class="metric-icon red">◷</div>
                    </div>

                    <div class="metric-value" id="overdueInvoices">0</div>

                    <div class="metric-foot">
                        Invoices past their due date
                    </div>
                </article>

                <article class="metric-card">
                    <div class="metric-top">
                        <div class="metric-label">Needs follow-up</div>
                        <div class="metric-icon amber">↗</div>
                    </div>

                    <div class="metric-value" id="followupInvoices">0</div>

                    <div class="metric-foot">
                        Open invoices to keep an eye on
                    </div>
                </article>

                <article class="metric-card">
                    <div class="metric-top">
                        <div class="metric-label">Currencies tracked</div>
                        <div class="metric-icon green">¤</div>
                    </div>

                    <div class="metric-value" id="currencyCount">0</div>

                    <div class="metric-foot">
                        Separate totals by currency
                    </div>
                </article>

            </section>

            <div class="section-heading">
                <div>
                    <h2>Quick actions</h2>
                    <p>Create a new invoice or check your PayPal connection.</p>
                </div>
            </div>

            <section class="work-grid">

                <article class="panel" id="create">

                    <h2 class="panel-title">Create a new invoice</h2>

                    <p class="panel-subtitle">
                        Add customer and service details to prepare a draft invoice.
                    </p>

                    <form id="invoiceForm">

                        <div class="form-grid">

                            <div class="field full">
                                <label for="email">Customer email</label>

                                <input
                                    id="email"
                                    type="email"
                                    placeholder="customer@example.com"
                                    required
                                >

                                <p class="helper">
                                    Use a PayPal Sandbox recipient when testing.
                                </p>
                            </div>

                            <div class="field full">
                                <label for="service_name">Service or item name</label>

                                <input
                                    id="service_name"
                                    maxlength="200"
                                    placeholder="Website design"
                                    required
                                >
                            </div>

                            <div class="field">
                                <label for="amount">Amount</label>

                                <input
                                    id="amount"
                                    type="number"
                                    min="0.01"
                                    max="1000000"
                                    step="0.01"
                                    placeholder="5.00"
                                    required
                                >
                            </div>

                            <div class="field">
                                <label for="currency">Currency</label>

                                <select id="currency">
                                    <option value="USD">USD — US Dollar</option>
                                    <option value="EUR">EUR — Euro</option>
                                    <option value="GBP">GBP — Pound Sterling</option>
                                </select>
                            </div>

                            <div class="field full">
                                <label for="due_date">Payment due date</label>

                                <input
                                    id="due_date"
                                    type="date"
                                    required
                                >

                                <p class="helper">
                                    Choose a date at least one day in the future.
                                </p>
                            </div>

                        </div>

                        <div class="form-actions">

                            <button
                                class="primary-btn"
                                id="createButton"
                                type="submit"
                            >
                                ＋ Create draft invoice
                            </button>

                            <span id="message"
                                  role="status"
                                  aria-live="polite"></span>

                        </div>

                    </form>

                </article>

                <article class="panel connection-panel">

                    <h2 class="panel-title">PayPal connection</h2>

                    <p class="panel-subtitle">
                        Your invoicing service connection status.
                    </p>

                    <div class="paypal-mark">P</div>

                    <div class="connection-status">
                        <span id="connectionDot" class="dot"></span>
                        <span id="connection">Checking connection...</span>
                    </div>

                    <div class="connection-detail" id="connectionDetail">
                        Checking your PayPal Sandbox credentials.
                    </div>

                    <button
                        class="secondary-btn"
                        type="button"
                        onclick="checkConnection()"
                    >
                        Check connection
                    </button>

                    <div class="outstanding-list">

                        <div class="outstanding-title">
                            ESTIMATED OUTSTANDING BY CURRENCY
                        </div>

                        <div id="outstandingAmounts">
                            <div class="currency-line">
                                <span>Loading totals...</span>
                            </div>
                        </div>

                    </div>

                </article>

            </section>

            <section class="panel table-panel" id="invoices">

                <div class="section-heading" style="margin:0 0 5px">

                    <div>
                        <h2>Invoices</h2>
                        <p>Review statuses and cash-flow suggestions.</p>
                    </div>

                    <div class="table-toolbar">

                        <div class="search-wrap">
                            <input
                                id="invoiceSearch"
                                type="search"
                                placeholder="Search invoices..."
                                aria-label="Search invoices"
                            >
                        </div>

                        <div class="filter-wrap">
                            <select id="statusFilter"
                                    aria-label="Filter by invoice status">

                                <option value="ALL">All statuses</option>
                                <option value="DRAFT">Draft</option>
                                <option value="SENT">Sent</option>
                                <option value="PAID">Paid</option>
                                <option value="CANCELLED">Cancelled</option>
                                <option value="REFUNDED">Refunded</option>

                            </select>
                        </div>

                    </div>

                </div>

                <div class="invoice-list">

                    <div class="mobile-invoices">

                        <div class="invoice-head">
                            <div>Invoice / service</div>
                            <div>Amount</div>
                            <div>Due date</div>
                            <div>Status</div>
                            <div>Copilot suggestion</div>
                            <div>Action</div>
                        </div>

                        <div id="invoicesList">
                            <div class="empty-state">
                                Loading your invoices...
                            </div>
                        </div>

                    </div>

                </div>

                <p class="footnote">
                    Outstanding totals are estimates based on invoice totals
                    and statuses. Drafts and completed invoices are excluded.
                    Partial payments may make the estimate differ from the
                    remaining balance.
                </p>

            </section>

        </main>

    </div>
</div>

<script>
const dateInput = document.getElementById("due_date");
const message = document.getElementById("message");

let allInvoices = [];

function localDateString(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");

    return `${y}-${m}-${day}`;
}

const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);

dateInput.min = localDateString(tomorrow);
dateInput.value = localDateString(tomorrow);

document.getElementById("todayLabel").textContent =
    new Intl.DateTimeFormat(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
    }).format(new Date());


function setMessage(text, type = "") {
    message.textContent = text;
    message.className = type;
}


async function checkConnection() {

    const box = document.getElementById("connection");
    const detail = document.getElementById("connectionDetail");
    const topText = document.getElementById("topConnection");
    const dot = document.getElementById("connectionDot");
    const topDot = document.getElementById("topDot");

    box.textContent = "Checking...";
    detail.textContent = "Checking your PayPal Sandbox credentials.";
    topText.textContent = "Checking PayPal...";

    dot.classList.remove("online");
    topDot.classList.remove("online");

    try {

        const response = await fetch("/api/connection");
        const data = await response.json();

        if (!response.ok || !data.connected) {
            throw new Error(
                data.error || "Check your Sandbox credentials."
            );
        }

        box.textContent = "Connected to PayPal Sandbox";

        detail.textContent =
            "Your application can reach the PayPal Sandbox service.";

        topText.textContent = "PayPal connected";

        dot.classList.add("online");
        topDot.classList.add("online");

    } catch (error) {

        box.textContent = "Connection unavailable";
        detail.textContent = error.message;
        topText.textContent = "Connection issue";

    }
}


document.getElementById("invoiceForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button = document.getElementById("createButton");
        const selectedDate = dateInput.value;

        if (!selectedDate || selectedDate < dateInput.min) {

            setMessage(
                "Choose a due date at least one day in the future.",
                "error"
            );

            return;
        }

        const payload = {

            customer_email:
                document.getElementById("email").value.trim(),

            service_name:
                document.getElementById("service_name").value.trim(),

            amount:
                document.getElementById("amount").value,

            currency:
                document.getElementById("currency").value,

            due_date: selectedDate

        };

        button.disabled = true;
        button.textContent = "Creating invoice...";

        setMessage("Creating your draft invoice...");

        try {

            const response = await fetch("/api/invoices/create", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(payload)

            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.error || "Invoice creation failed."
                );
            }

            const invoice = result.invoice || {};

            const id = invoice.id || invoice.invoice_id || "";

            setMessage(
                id
                    ? "Draft created successfully. Invoice ID: " + id
                    : "Draft created successfully. Refresh the dashboard to review it.",
                "success"
            );

            document.getElementById("service_name").value = "";
            document.getElementById("amount").value = "";

            await refreshDashboard();

        } catch (error) {

            setMessage("Error: " + error.message, "error");

        } finally {

            button.disabled = false;
            button.textContent = "＋ Create draft invoice";

        }

    }
);


async function sendInvoice(invoiceId, button) {

    if (!confirm(
        "Send invoice " + invoiceId +
        " through PayPal Sandbox to its recipient?"
    )) {
        return;
    }

    button.disabled = true;
    button.textContent = "Sending...";

    try {

        const response = await fetch("/api/invoices/send", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                invoice_id: invoiceId
            })

        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(
                result.error || "Unable to send invoice."
            );
        }

        setMessage(
            result.message || "PayPal accepted the send request.",
            "success"
        );

        await refreshDashboard();

    } catch (error) {

        setMessage("Send failed: " + error.message, "error");

        button.disabled = false;
        button.textContent = "Send invoice";

    }

}


function statusClass(status, overdue) {

    if (overdue) return "overdue";

    const value = (status || "").toUpperCase();

    if (value === "SENT" || value === "PAID") {
        return value.toLowerCase();
    }

    if (value === "DRAFT" || value === "SAVED") {
        return "draft";
    }

    return "";

}


function createCell(className, text) {

    const el = document.createElement("div");

    if (className) {
        el.className = className;
    }

    el.textContent = text;

    return el;

}


function renderInvoices() {

    const box = document.getElementById("invoicesList");

    box.replaceChildren();

    const search = document.getElementById("invoiceSearch")
        .value.trim().toLowerCase();

    const status = document.getElementById("statusFilter").value;

    const filtered = allInvoices.filter(invoice => {

        const currentStatus =
            (invoice.status || "UNKNOWN").toUpperCase();

        const searchable = [

            invoice.service_name,
            invoice.id,
            invoice.invoice_id,
            invoice.amount,
            invoice.currency,
            currentStatus

        ].join(" ").toLowerCase();

        return (
            (status === "ALL" || currentStatus === status) &&
            searchable.includes(search)
        );

    });


    if (!filtered.length) {

        const empty = document.createElement("div");

        empty.className = "empty-state";

        empty.textContent =
            "No matching invoices. Try another search or create a new invoice.";

        box.appendChild(empty);

        return;

    }


    filtered.forEach(invoice => {

        const row = document.createElement("div");

        row.className = "invoice-row";

        const id = invoice.id || invoice.invoice_id || "";

        const currentStatus =
            (invoice.status || "UNKNOWN").toUpperCase();


        const identity = document.createElement("div");

        identity.appendChild(
            createCell(
                "invoice-name",
                invoice.service_name || "Service not specified"
            )
        );

        identity.appendChild(
            createCell(
                "invoice-id",
                id ? "ID: " + id : "Invoice ID unavailable"
            )
        );

        row.appendChild(identity);


        row.appendChild(
            createCell(
                "invoice-amount",
                (invoice.currency || "USD") + " " +
                (invoice.amount ?? "N/A")
            )
        );


        row.appendChild(
            createCell(
                "invoice-due",
                invoice.due_date || "Not set"
            )
        );


        const badge = createCell(
            "status-badge " +
            statusClass(currentStatus, invoice.overdue),
            currentStatus
        );

        row.appendChild(badge);


        row.appendChild(
            createCell(
                "suggestion-text",
                invoice.suggestion ||
                "Monitor the invoice status."
            )
        );


        const action = document.createElement("div");

        if (currentStatus === "DRAFT" && id) {

            const sendButton = document.createElement("button");

            sendButton.className = "send-btn";
            sendButton.type = "button";
            sendButton.textContent = "Send invoice";

            sendButton.addEventListener(
                "click",
                () => sendInvoice(id, sendButton)
            );

            action.appendChild(sendButton);

        } else {

            action.appendChild(
                createCell("suggestion-text", "—")
            );

        }

        row.appendChild(action);

        box.appendChild(row);

    });

}


async function refreshDashboard() {

    const box = document.getElementById("invoicesList");

    box.innerHTML =
        '<div class="empty-state">Refreshing invoice data...</div>';

    try {

        const response = await fetch("/api/invoices/analysis");

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to load invoices."
            );
        }

        allInvoices = Array.isArray(data)
            ? data
            : (data.invoices || []);


        document.getElementById("totalInvoices").textContent =
            allInvoices.length;


        const overdue = allInvoices.filter(
            invoice => invoice.overdue
        );

        document.getElementById("overdueInvoices").textContent =
            overdue.length;


        const excluded = [
            "PAID",
            "CANCELLED",
            "REFUNDED",
            "DRAFT",
            "SAVED"
        ];


        const followup = allInvoices.filter(invoice =>

            !excluded.includes(
                (invoice.status || "").toUpperCase()
            )

        );

        document.getElementById("followupInvoices").textContent =
            followup.length;


        const outstanding = {};

        allInvoices.forEach(invoice => {

            const currentStatus =
                (invoice.status || "").toUpperCase();

            if (excluded.includes(currentStatus)) {
                return;
            }

            const currency = invoice.currency || "USD";

            const amount = Number(invoice.amount);

            if (Number.isFinite(amount)) {

                outstanding[currency] =
                    (outstanding[currency] || 0) + amount;

            }

        });


        const outstandingBox =
            document.getElementById("outstandingAmounts");

        outstandingBox.replaceChildren();

        const currencies = Object.keys(outstanding).sort();

        document.getElementById("currencyCount").textContent =
            currencies.length;


        if (!currencies.length) {

            outstandingBox.appendChild(
                createCell(
                    "currency-line",
                    "No outstanding sent invoices found."
                )
            );

        } else {

            currencies.forEach(currency => {

                const line = document.createElement("div");

                line.className = "currency-line";

                line.appendChild(
                    createCell("", currency)
                );

                const amount = document.createElement("strong");

                amount.textContent =
                    outstanding[currency].toFixed(2);

                line.appendChild(amount);

                outstandingBox.appendChild(line);

            });

        }


        renderInvoices();

    } catch (error) {

        allInvoices = [];

        box.replaceChildren();

        const errorBox = document.createElement("div");

        errorBox.className = "empty-state";

        errorBox.textContent =
            "Unable to load invoices: " + error.message;

        box.appendChild(errorBox);


        document.getElementById("totalInvoices").textContent = "—";
        document.getElementById("overdueInvoices").textContent = "—";
        document.getElementById("followupInvoices").textContent = "—";
        document.getElementById("currencyCount").textContent = "—";

        document.getElementById("outstandingAmounts").textContent =
            "Unable to calculate outstanding amounts.";

    }

}


document.getElementById("invoiceSearch").addEventListener(
    "input",
    renderInvoices
);

document.getElementById("statusFilter").addEventListener(
    "change",
    renderInvoices
);


document.querySelectorAll(".nav-link").forEach(link => {

    link.addEventListener("click", () => {

        document.querySelectorAll(".nav-link").forEach(item => {
            item.classList.remove("active");
        });

        link.classList.add("active");

    });

});


checkConnection();
refreshDashboard();

</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/connection")
def connection():

    try:

        result = test_paypal_connection()

        if isinstance(result, dict):
            return jsonify(result)

        return jsonify({"connected": bool(result)})

    except Exception as exc:

        app.logger.exception("PayPal connection check failed")

        return jsonify({
            "connected": False,
            "error": str(exc)
        }), 500


@app.route("/api/invoices")
def invoices():

    try:

        return jsonify(get_invoices())

    except Exception as exc:

        app.logger.exception("Unable to fetch invoices")

        return jsonify({"error": str(exc)}), 500


@app.route("/api/invoices/analysis")
def invoice_analysis():

    try:

        return jsonify([
            analyze_invoice(item)
            for item in get_invoices()
        ])

    except Exception as exc:

        app.logger.exception("Invoice analysis failed")

        return jsonify({"error": str(exc)}), 500


@app.route("/api/invoices/create", methods=["POST"])
def create_invoice():

    data = request.get_json(silent=True) or {}

    customer_email = str(
        data.get("customer_email", "")
    ).strip()

    service_name = str(
        data.get("service_name", "")
    ).strip()

    currency = str(
        data.get("currency", "USD")
    ).upper()

    due_date = str(
        data.get("due_date", "")
    ).strip()


    if not customer_email or "@" not in customer_email:

        return jsonify({
            "success": False,
            "error": "Enter a valid customer email address."
        }), 400


    if not service_name:

        return jsonify({
            "success": False,
            "error": "Enter a service name."
        }), 400


    try:

        amount = float(data.get("amount", 0))

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "error": "Enter a valid amount."
        }), 400


    if not 0 < amount <= 1000000:

        return jsonify({
            "success": False,
            "error": "Amount must be greater than zero and at most 1,000,000."
        }), 400


    try:

        selected_date = date.fromisoformat(due_date)

    except ValueError:

        return jsonify({
            "success": False,
            "error": "Select a valid due date."
        }), 400


    days_until_due = (
        selected_date - date.today()
    ).days


    if days_until_due < 1:

        return jsonify({
            "success": False,
            "error": "Choose a due date at least one day in the future."
        }), 400


    if currency not in {"USD", "EUR", "GBP"}:

        return jsonify({
            "success": False,
            "error": "Unsupported currency."
        }), 400


    try:

        created = create_draft_invoice(

            customer_email=customer_email,

            item_name=service_name,

            amount=amount,

            currency=currency,

            due_in_days=days_until_due

        )

        return jsonify({
            "success": True,
            "invoice": created
        }), 201


    except Exception as exc:

        app.logger.exception("Invoice creation failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


@app.route("/api/invoices/send", methods=["POST"])
def send_existing_invoice():

    data = request.get_json(silent=True) or {}

    invoice_id = str(
        data.get("invoice_id", "")
    ).strip()


    if not invoice_id:

        return jsonify({
            "success": False,
            "error": "Invoice ID is required."
        }), 400


    try:

        result = send_invoice(invoice_id)

        return jsonify(result)


    except Exception as exc:

        app.logger.exception("Invoice sending failed")

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
