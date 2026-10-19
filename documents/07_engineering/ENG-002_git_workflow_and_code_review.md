---
doc_id: ENG-002
title: Git Workflow, Pull Requests and Code Review Guidelines
department: Engineering
owner: arjun.kulkarni@orbitra.io
version: 4.1
status: active
last_updated: 2026-06-02
applies_to: all engineers
classification: Internal
tags: [git, branching, pull request, code review, approvals, commit message, ci, testing, coverage, codeowners]
---

# Git Workflow and Code Review

## 1. Branching
- **Trunk-based development** on `main`. Short-lived feature branches (< 3 days).
- Branch naming: `<type>/<JIRA-KEY>-short-description`, e.g. `feat/FLOW-1234-bulk-approve`.
- Use **feature flags** (LaunchDarkly) for incomplete features instead of long-lived branches.

## 2. Commit messages
Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`. Include the Jira key.

## 3. Pull request requirements
| Requirement | Rule |
|---|---|
| Approvals | **1 approval** for most repos; **2 approvals** for services tagged `tier-0` (auth, billing, flow-engine core) and for `orbitra/infra` |
| CODEOWNERS | At least one approval from a code owner of the changed path |
| CI | All checks green (build, unit tests, lint, SAST via Semgrep, dependency scan via Snyk) |
| Test coverage | New code must have ≥ **80%** line coverage; overall coverage cannot drop |
| PR size | Aim for < 400 lines changed; larger PRs must be justified in the description |
| Description | What, why, how tested, screenshots for UI, rollback plan for risky changes |

## 4. Reviewer expectations
- First review within **1 business day** (4 business hours for PRs labelled `urgent`).
- Be kind and specific; prefix optional comments with "nit:".
- Reviewers check correctness, security, readability, tests, and observability (logs/metrics).
- Authors resolve all comments or explain why not.

## 5. Merging
Squash-merge only. The author merges after approval. Merging to `main` triggers deploy to **staging** automatically (see ENG-003).

## 6. Secrets in code
CI blocks commits containing secrets (Gitleaks). If a secret is committed, **rotate it immediately** and inform #sec-incidents — deleting the commit is not enough.
