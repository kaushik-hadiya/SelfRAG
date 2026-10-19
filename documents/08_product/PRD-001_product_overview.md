---
doc_id: PRD-001
title: Product Overview – Orbitra Flow, Insights, Connect and Copilot
department: Product Management
owner: karthik.subramanian@orbitra.io
version: 6.0
status: active
last_updated: 2026-09-30
applies_to: all employees (esp. Sales, CS, new joiners)
classification: Internal
tags: [product, orbitra flow, insights, connect, copilot, features, plans, limits, integrations, ideal customer profile]
---

# Product Overview

## 1. Orbitra Flow (core platform)
No-code workflow automation for operations, finance, HR and IT teams.
- **Visual workflow builder** with drag-and-drop steps: forms, approvals, conditions, loops, timers, scripts (JavaScript sandbox).
- **Approvals** with multi-level chains, delegation, SLA timers and escalations.
- **Forms** with 30+ field types, conditional logic, e-signature.
- **Audit trail** for every workflow execution (retained per plan).
- Mobile apps (iOS/Android) for approvals.
- Typical use cases: purchase approvals, employee onboarding, invoice processing, vendor onboarding, IT access requests.

## 2. Orbitra Insights
Embedded analytics on workflow data: cycle time, bottlenecks, SLA breaches, approver load. Custom dashboards, scheduled reports, and export to CSV/PDF. Built on ClickHouse.

## 3. Orbitra Connect
Integration hub with **250+ prebuilt connectors** (SAP S/4HANA, Salesforce, Workday, NetSuite, ServiceNow, Slack, Microsoft Teams, Google Workspace, Jira, Zendesk, Snowflake). Supports REST/webhook custom connectors and an on-prem agent for firewalled systems.

## 4. Orbitra Copilot (AI)
- Generates workflows from natural-language descriptions ("When a PO above $10k is raised, ask the finance manager and then the CFO to approve").
- Summarises workflow runs and suggests optimisations based on Insights data.
- Powered by Claude via Amazon Bedrock; **customer data is not used to train models**.
- Available on Growth and Enterprise plans (Enterprise gets admin controls and regional processing).

## 5. Plans and limits
| | Starter | Growth | Enterprise |
|---|---|---|---|
| List price | USD 12 /user/month | USD 29 /user/month | Custom (typically USD 45–70) |
| Minimum users | 10 | 25 | 200 |
| Workflow runs / month | 5,000 | 50,000 | Unlimited (fair use) |
| Connectors | 20 standard | All standard | All + custom + on-prem agent |
| Insights | Basic dashboards | Full | Full + embedded |
| Copilot | — | Included (500 generations/month) | Unlimited + admin controls |
| SSO (SAML) | — | ✔ | ✔ |
| Audit log retention | 90 days | 1 year | 7 years |
| Data residency choice | — | — | India, US, EU/UK |
| Support | Email (business hours) | Standard (see CS-001) | Premium 24x7 + TAM |
| Uptime SLA | — | 99.9% | 99.95% |

## 6. Ideal customer profile
Companies with 200–10,000 employees in IT services, BFSI, manufacturing and healthcare that run approval-heavy back-office processes on email and spreadsheets.

## 7. Competitors (internal only)
Main competitors: generic low-code platforms, ITSM vendors' workflow modules, and RPA vendors. Battlecards are on Confluence → Sales → Battlecards (Confidential).
