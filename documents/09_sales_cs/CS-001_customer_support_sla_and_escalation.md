---
doc_id: CS-001
title: Customer Support Tiers, SLAs and Escalation Process
department: Customer Success & Support
owner: emily.carter@orbitra.io
version: 3.4
status: active
last_updated: 2026-07-15
applies_to: Support, Customer Success, Sales, Engineering
classification: Internal
tags: [customer support, sla, priority, escalation, zendesk, tam, customer escalation, support hours, p1]
---

# Customer Support SLAs and Escalation

## 1. Support tiers
| Plan | Support tier | Hours | Channels |
|---|---|---|---|
| Starter | Basic | Business hours (customer region), Mon–Fri | Email, help center |
| Growth | Standard | 24x5 | Email, chat, help center |
| Enterprise | Premium | **24x7** for P1/P2; 24x5 otherwise | Email, chat, phone, dedicated Slack Connect, **TAM** |

## 2. Customer ticket priorities and first-response SLAs
| Priority | Definition | Basic | Standard | Premium |
|---|---|---|---|---|
| **P1 – Urgent** | Production down / critical business process blocked for most users | 8 business hrs | 2 hours | **30 minutes** |
| **P2 – High** | Major feature impaired, no workaround | 1 business day | 4 hours | 2 hours |
| **P3 – Normal** | Partial impairment, workaround exists | 2 business days | 1 business day | 8 hours |
| **P4 – Low** | Question, feature request | 3 business days | 2 business days | 1 business day |

All customer tickets are in **Zendesk**. Engineering escalations are created as Jira issues in the **ESC** project from Zendesk.

## 3. Internal escalation path for customer issues
1. **L1 Support** (triage, known issues, how-to) → 2. **L2 Support** (deep product, logs) → 3. **Engineering on-call** via Jira ESC (for bugs/outages; P1 pages PagerDuty directly) → 4. **Support Manager** and **TAM** → 5. **VP Customer Success** (Emily Carter) for executive escalations.
- Any P1 for an Enterprise customer automatically notifies the account's TAM and AE.
- If a customer P1 relates to a platform outage, declare an incident (ENG-004).

## 4. Customer escalations by Sales/CS
If a customer is unhappy at an executive level, open an **Executive Escalation** in Salesforce (Case type: Exec Escalation). The VP CS assigns an executive sponsor within 1 business day.

## 5. Service credits
For Enterprise uptime below 99.95% in a month: 5% credit (99.0–99.95%), 10% (95–99%), 25% (< 95%) of monthly fees, on customer request within 30 days. Credits are approved by the VP CS and Finance.

## 6. Who can access customer data
Only Support L2+, assigned TAMs and on-call engineers, through the **Support Console** with the customer's access grant (Admin → Support Access → Allow for 72 hours). See SEC-001.
