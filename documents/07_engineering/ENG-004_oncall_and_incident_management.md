---
doc_id: ENG-004
title: On-Call and Production Incident Management
department: Engineering – SRE
owner: sre@orbitra.io
version: 4.3
status: active
last_updated: 2026-09-05
applies_to: engineers in on-call rotations, engineering managers, support
classification: Internal
tags: [on-call, pagerduty, incident, sev1, sev2, severity, postmortem, rca, incident commander, status page, freeze, on-call allowance]
---

# On-Call and Incident Management

## 1. Severity levels
| Severity | Definition | Example | Ack time | Update cadence |
|---|---|---|---|---|
| **SEV1** | Full outage or data loss/security breach affecting many customers | app.orbitra.io down in a region | **5 min** | Every 30 min |
| **SEV2** | Major feature broken or severe degradation for many customers; no workaround | Workflow executions delayed > 15 min | **15 min** | Every 60 min |
| **SEV3** | Partial degradation; workaround exists; limited customers | One connector failing | 1 hour | Daily |
| **SEV4** | Minor bug, cosmetic, internal-only | Typo on dashboard | Next business day | — |

## 2. Declaring an incident
Anyone can declare an incident: in Slack type `/incident declare` → choose severity → a channel `#inc-YYYYMMDD-<short-name>` is created, the on-call is paged and an **Incident Commander (IC)** is assigned (on-call EM for SEV1/2).

## 3. Roles
- **Incident Commander:** coordinates, decides, does not debug.
- **Ops lead:** hands-on investigation and mitigation.
- **Comms lead:** updates the public status page (status.orbitra.io) and Customer Support (for SEV1/2, first public update within **20 minutes**).
- **Scribe:** maintains the timeline.

## 4. Postmortems
- Required for **SEV1 and SEV2** (optional for SEV3).
- Draft within **5 business days** using the Confluence template "Blameless Postmortem".
- Reviewed in the weekly Reliability Review (Wednesdays 5 PM IST).
- Action items tracked in Jira with label `postmortem`; SEV1 action items must close within 30 days.

## 5. Freeze windows (FY27)
| Freeze | Dates |
|---|---|
| Diwali freeze | 6 Nov 2026 – 10 Nov 2026 |
| Year-end / Quiet Week | 21 Dec 2026 – 4 Jan 2027 |
| Fiscal year close | 25 Mar 2027 – 2 Apr 2027 |
Only SEV1/SEV2 fixes are allowed during freezes, with VP Engineering approval.

## 6. On-call rotation and compensation
- Rotations are weekly (Monday 10 AM to Monday 10 AM), follow-the-sun between India and US for tier-0 services.
- Engineers join on-call after **3 months** of tenure and shadowing two shifts.
- **On-call allowance (India):** INR 3,000 per weekday on call and INR 5,000 per weekend/holiday day on call; plus 1 comp-off if paged for > 2 hours on a weekend/holiday. US: USD 400 per week. UK: GBP 300 per week.
- Claim via PeopleHub → Payroll → "On-call allowance" by the 20th of the month (auto-filled from PagerDuty schedules).
- Swap shifts via PagerDuty overrides; inform your team channel.
