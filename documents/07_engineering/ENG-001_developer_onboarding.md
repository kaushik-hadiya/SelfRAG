---
doc_id: ENG-001
title: Developer Onboarding and Local Environment Setup
department: Engineering – Developer Experience
owner: devex@orbitra.io
version: 7.0
status: active
last_updated: 2026-09-25
applies_to: engineers, data scientists, SREs
classification: Internal
tags: [developer onboarding, setup, github, repos, local environment, docker, devbox, first pr, monorepo, tech stack]
---

# Developer Onboarding

## 1. Week 1 goals
1. Get access (GitHub, AWS non-prod, Vault, Datadog, PagerDuty – viewer).
2. Set up the local environment.
3. Ship your **first PR** (a "good first issue" from your team's Jira board) by the end of week 2.

## 2. Access checklist
| System | How to get access |
|---|---|
| GitHub org `orbitra` | Automatic after **Secure Coding** training completion; your EM approves team membership |
| AWS (non-prod) | AWS SSO via Okta tile; request role in OrbitDesk → IT → Application Access |
| Vault | Auto-provisioned with GitHub team mapping |
| Datadog | Okta tile (read-only by default) |
| PagerDuty | Added by your EM when you join an on-call rotation (after 3 months) |
| Jira / Confluence | Auto-provisioned |

## 3. Tech stack
| Layer | Technology |
|---|---|
| Backend services | Go (core services), Java 21 / Spring Boot (legacy Flow engine), Python 3.12 (Data/AI) |
| Frontend | TypeScript, React 19, Next.js |
| Data | PostgreSQL 16 (Aurora), Redis, Kafka (MSK), ClickHouse (Insights), S3 |
| AI | Orbitra Copilot uses Claude via Amazon Bedrock; internal vector store on pgvector |
| Infra | AWS, Kubernetes (EKS), Terraform, ArgoCD, GitHub Actions |
| Observability | Datadog (metrics, APM, logs), Sentry (frontend errors), PagerDuty |

## 4. Repositories
- `orbitra/platform` – monorepo for Go services (Bazel build)
- `orbitra/flow-engine` – Java workflow engine
- `orbitra/web` – frontend monorepo (pnpm + Turborepo)
- `orbitra/insights` – analytics services
- `orbitra/infra` – Terraform and Helm charts (write access: Platform team only)
- `orbitra/copilot` – AI services

## 5. Local setup
1. Install Homebrew-based toolchain: run `curl -fsSL https://dev.orbitra.internal/bootstrap.sh | bash` (requires VPN). It installs Go, Node (via fnm), Java (via SDKMAN), Docker Desktop, kubectl, and the `orb` CLI.
2. `orb login` (Okta SSO) then `orb dev up` to start local dependencies (Postgres, Redis, Kafka) in Docker.
3. For heavy workloads use a **Devbox** (cloud dev environment): `orb devbox create --size large`. Devboxes auto-stop after 2 hours idle.
4. Seed data: `orb db seed --profile demo`.

Common issues: Docker out of memory → allocate ≥ 8 GB in Docker Desktop settings; `orb dev up` fails on port 5432 → stop any local Postgres (`brew services stop postgresql`).

## 6. Help
Slack **#dev-help** (DevEx team responds within 2 business hours), office hours Thursdays 4 PM IST.
