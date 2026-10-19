---
doc_id: IT-003
title: VPN (Orbitra SecureConnect) – Setup and Troubleshooting
department: Corporate IT
owner: it-network@orbitra.io
version: 2.6
status: active
last_updated: 2026-09-02
applies_to: all employees
classification: Internal
tags: [vpn, secureconnect, globalprotect, remote access, troubleshooting, connection error, portal, how-to]
---

# VPN – Orbitra SecureConnect

Orbitra SecureConnect (based on Palo Alto GlobalProtect) is required to access internal systems (Confluence, OrbitDesk, PeopleHub admin pages, internal dashboards, staging environments) from outside the office. Slack, Gmail, Okta and Zoom do **not** need VPN.

## Setup
1. SecureConnect is pre-installed on every company laptop. If missing, install from **Orbitra App Store** (Self Service on Mac / Company Portal on Windows).
2. Portal address: **vpn.orbitra.io**
3. Sign in with your Okta credentials and approve the Okta Verify push.
4. Choose gateway: **Auto (recommended)**, or manually: India-South (Bengaluru), India-West (Pune), US-Central (Austin), EU-London.

## Troubleshooting
| Symptom | Fix |
|---|---|
| "Portal not reachable" | Check internet. Try a hotspot. Ensure the portal is vpn.orbitra.io (not vpn.orbitra.com). |
| Stuck at "Connecting…" | Disconnect, quit the app, reopen. On Mac: `sudo killall PanGPS`; on Windows restart the "PanGPS" service. |
| Okta push not received | Open Okta Verify and pull to refresh; check phone time is set to automatic. Use the 6-digit code as fallback. |
| "Authentication failed" | Your password may have expired. Reset at **orbitra.okta.com → Forgot password**, wait 5 minutes, retry. |
| Connected but internal sites don't open | Flush DNS (Mac: `sudo dscacheutil -flushcache`; Windows: `ipconfig /flushdns`). Switch gateway to a nearer one. |
| Slow speed on VPN | Use Auto gateway; avoid running large downloads; video calls do not need VPN (split tunnelling is enabled for Zoom/Slack/Google). |
| "HIP check failed" | Your laptop is non-compliant (OS update pending, disk encryption off, or antivirus disabled). Install pending updates and restart. |
| VPN works at home but not at a hotel | Hotel networks may block UDP; SecureConnect will fall back to TCP 443 automatically—wait 60 seconds. If it still fails, use a mobile hotspot. |

If none of the above works, raise OrbitDesk → IT → "VPN issue" with a screenshot and the output of **Help → Collect Logs**. If you are fully blocked, call Ext. 4000 (treated as P2).
