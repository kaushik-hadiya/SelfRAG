---
doc_id: SEC-001
title: Information Security Policy and Data Classification
department: Information Security
owner: daniel.brooks@orbitra.io
version: 5.1
status: active
last_updated: 2026-05-30
applies_to: all employees, contractors, vendors with system access
classification: Internal
tags: [security, data classification, restricted, confidential, encryption, clean desk, sharing data, customer data, iso 27001, soc 2]
---

# Information Security Policy

Orbitra is **ISO 27001:2022** certified and has a **SOC 2 Type II** report (renewed annually in August). Every employee is responsible for protecting Orbitra and customer information.

## 1. Data classification
| Class | Examples | Rules |
|---|---|---|
| **Public** | Website content, published blogs, public docs | No restrictions |
| **Internal** | Policies, org charts, internal announcements, this knowledge base | Share only with employees/contractors |
| **Confidential** | Financials, roadmaps, contracts, source code, customer names, employee salaries (individual) | Need-to-know; share externally only under NDA; encrypt in transit |
| **Restricted** | Customer production data, personal data (PII), credentials/secrets, payment data, health data, M&A information | Strictly need-to-know; never in email/Slack/AI tools; stored only in approved systems; access logged |

If a document has no label, treat it as **Internal**.

## 2. Handling rules
- **Sharing externally:** use Google Drive with link restricted to named people (no "anyone with the link"), set expiry. Confidential files require an NDA in place (see LEG-001).
- **Customer data** may only be accessed for a valid support ticket, with the customer's consent where required, via the approved support console (never by copying to local machines).
- **Secrets** (API keys, passwords) must be stored in **HashiCorp Vault** (engineering) or **1Password** (teams). Never in code, Slack or Confluence.
- **Clean desk / clear screen:** lock your screen when away (Win+L / Ctrl+Cmd+Q). Auto-lock after 5 minutes.
- **Printing** Restricted data is not allowed.
- **Encryption:** all laptops have full-disk encryption; data at rest in production is encrypted with AES-256.

## 3. Third-party tools and vendors
Any new tool processing Internal data or above needs a **Security & Privacy review** (OrbitDesk → Security → "Vendor review"), typically 10 business days. See FIN-003 for procurement.

## 4. Security training
Annual security awareness training and quarterly phishing simulations are mandatory. Clicking a simulated phishing link triggers a 10-minute micro-training.

## 5. Exceptions
Policy exceptions are requested via OrbitDesk → Security → "Policy exception", must have a business justification, and are valid for max 6 months.
