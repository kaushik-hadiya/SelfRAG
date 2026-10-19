---
doc_id: ENG-003
title: Environments, Deployment Process and Release Management
department: Engineering – Platform
owner: platform@orbitra.io
version: 5.2
status: active
last_updated: 2026-08-19
applies_to: all engineers
classification: Internal
tags: [deployment, release, environments, staging, production, argocd, rollback, canary, aws regions, change management]
---

# Environments and Deployment

## 1. Environments
| Environment | Purpose | URL pattern | Data |
|---|---|---|---|
| dev (local / devbox) | Individual development | localhost / *.devbox.orbitra.dev | Synthetic |
| staging | Integration testing, QA, demos | *.staging.orbitra.dev | Synthetic + anonymised |
| sandbox | Customer-facing test environment | *.sandbox.orbitra.io | Customer test data |
| production | Live customers | app.orbitra.io (+ regional) | Real customer data (Restricted) |

## 2. Production regions
| Region | AWS region | Customers |
|---|---|---|
| India (primary) | ap-south-1 (Mumbai) | India & APAC |
| US | us-east-1 (N. Virginia) | Americas |
| EU/UK | eu-west-2 (London) | EMEA (data residency) |

## 3. Deployment pipeline
1. Merge to `main` → GitHub Actions builds the image → auto-deploy to **staging** via ArgoCD.
2. Automated integration and smoke tests run on staging (~20 min).
3. Promote to production with `orb release promote <service> --to prod` or the "Promote" button in the Release Dashboard.
4. Production deploys use a **canary**: 5% traffic for 15 minutes → 25% → 100%, with automatic rollback if error rate rises above 1% or p99 latency rises by 30%.

## 4. Deployment windows
- Allowed: **Monday–Thursday, 10:00 AM – 6:00 PM local time** of the deploying team.
- **No production deploys on Fridays, weekends or public holidays** without an approved exception.
- Freeze windows: see ENG-004 §5.
- Emergency hotfixes during restricted windows require approval from the on-call Engineering Manager **and** be linked to an active incident or Jira P0.

## 5. Rollback
`orb release rollback <service>` restores the previous version within ~3 minutes. Database migrations must be backward-compatible (expand–contract pattern) so rollbacks are safe.

## 6. Change management for tier-0 services
Changes to tier-0 services need a change record in Jira (CHG project) with risk assessment, approved by the service owner, at least 24 hours before deploy.
