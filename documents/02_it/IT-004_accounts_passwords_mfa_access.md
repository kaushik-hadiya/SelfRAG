---
doc_id: IT-004
title: Accounts, Passwords, MFA and Application Access
department: Corporate IT & Security
owner: iam@orbitra.io
version: 3.3
status: active
last_updated: 2026-07-11
applies_to: all employees and contractors
classification: Internal
tags: [password, reset, okta, mfa, account locked, sso, access request, new phone, application owners, github access, aws access]
---

# Accounts, Passwords, MFA and Access

## 1. Single sign-on (Okta)
All company applications are accessed through **orbitra.okta.com**. Your username is your email address.

## 2. Password rules
- Minimum **14 characters**; must not contain your name or "orbitra".
- Passwords expire every **180 days**; you receive reminders 14, 7 and 1 day before expiry.
- Last 10 passwords cannot be reused.
- **Self-service reset:** orbitra.okta.com → "Forgot password?" → verify with Okta Verify or SMS. Takes 2 minutes.
- On Mac, after a reset, the laptop login password syncs on next login while connected to the internet (Okta Platform SSO). If it doesn't sync, connect to the office Wi-Fi or VPN and lock/unlock the screen.

## 3. Account lockout
After **5 failed attempts** your account is locked for **30 minutes** and then unlocks automatically. To unlock immediately, use self-service unlock at orbitra.okta.com or call Ext. 4000.

## 4. Multi-factor authentication (MFA)
- **Okta Verify** push is mandatory. SMS is allowed only as a backup factor.
- Admin and production access require a **YubiKey** (hardware key), issued by IT Security.
- **Changed or lost your phone?** Raise OrbitDesk → IT → "MFA reset". IT will verify your identity on a video call (keep your employee ID card ready) and reset the factor within 4 business hours. Do not ask colleagues to share MFA codes.

## 5. Requesting application access
Raise OrbitDesk → IT → "Application Access", pick the application. The request is routed to the app owner.

| Application | App owner (approver) | Notes |
|---|---|---|
| Jira / Confluence | IT (auto-approved for employees) | — |
| GitHub (orbitra org) | Engineering Manager | Requires secure coding training complete |
| AWS console (non-prod) | Platform team (#eng-platform) | Via AWS SSO; read-only by default |
| AWS console (prod) | VP Engineering + Security | Time-bound (max 8 hours) via "Break-glass" in OrbitDesk |
| Salesforce | Sales Ops (salesops@orbitra.io) | Licence cost charged to department |
| Figma | Design Ops | Editor seats limited; viewers free |
| Tableau / Insights internal dashboards | Data team (#data-ai) | — |
| NetSuite | Finance (Kavita Shah) | Finance team only |
| PeopleHub admin | HR Ops | HR only |

**Access reviews:** App owners review access every quarter. Unused access (90 days) is automatically removed.

## 6. Contractors
Contractor accounts expire at contract end date or after 90 days, whichever is earlier; the sponsoring manager must extend via OrbitDesk.
