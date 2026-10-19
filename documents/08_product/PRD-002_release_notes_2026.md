---
doc_id: PRD-002
title: Release Notes – 2026
department: Product Management
owner: product-ops@orbitra.io
version: 2026.10
status: active
last_updated: 2026-10-14
applies_to: all employees
classification: Internal
tags: [release notes, changelog, new features, deprecation, 2026, copilot, connect]
---

# Release Notes – 2026

## Release 26.10 (14 October 2026)
- **Copilot Agents (beta):** Copilot can now execute multi-step actions (e.g., create a vendor in NetSuite after approval) with human-in-the-loop confirmation. Enterprise only, opt-in via admin console.
- **Parallel approvals with quorum:** e.g., "any 2 of 3 approvers".
- **Connect:** new connectors for Zoho People, Freshservice and Oracle Fusion HCM.
- **Fixed:** timezone bug where SLA timers ignored daylight saving in US/UK regions.

## Release 26.08 (12 August 2026)
- **Insights:** natural-language querying ("show average approval time by department last quarter").
- **Flow:** version history with side-by-side diff and one-click restore.
- **Mobile:** offline approvals queue (syncs when back online).

## Release 26.06 (16 June 2026)
- **EU/UK data residency** generally available for Enterprise (eu-west-2).
- **Copilot:** workflow generation now supports Hindi, Spanish, French and German prompts.
- **Deprecation notice:** Legacy Forms v1 will be **retired on 31 January 2027**. Customers must migrate to Forms v2 (migration tool in Admin → Forms → Migrate).

## Release 26.04 (14 April 2026)
- **Audit log export** to Splunk and Datadog.
- **SCIM provisioning** for Okta and Azure AD on Growth plan (previously Enterprise only).

## Release 26.02 (10 February 2026)
- **Copilot GA** for Growth and Enterprise.
- **Connect:** SAP S/4HANA connector v2 with change data capture.

## Release cadence
Major releases every 2 months (second Tuesday of even months). Hotfixes weekly. Customer-facing notes are published at docs.orbitra.io/changelog.
