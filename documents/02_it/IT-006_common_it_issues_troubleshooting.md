---
doc_id: IT-006
title: Common IT Issues – Self-Help Troubleshooting Guide
department: Corporate IT
owner: it-servicedesk@orbitra.io
version: 6.4
status: active
last_updated: 2026-10-01
applies_to: all employees
classification: Internal
tags: [troubleshooting, printer, wifi, zoom, slack, outlook, email, calendar, slow laptop, disk space, bluetooth, screen sharing, meeting room, how-to]
---

# Common IT Issues – Self-Help

## Office Wi-Fi
- Network: **Orbitra-Corp** (employees, auto-connect via certificate). **Orbitra-Guest** for visitors (sponsor approval via portal, valid 24 h).
- Not connecting to Orbitra-Corp? Forget the network and reconnect; your device certificate renews automatically. If your laptop was off the network for 60+ days, connect via VPN once to renew the certificate.
- Do not connect company laptops to Orbitra-Guest.

## Printing
- Use **Orbitra-SecurePrint** queue (pre-installed). Print jobs are held until you badge in at any printer (follow-me printing).
- Jobs are deleted if not released within 24 hours.
- Colour printing requires selecting "Colour" and is limited to 100 pages/month per user.
- Printer offline? Check the printer screen; if it shows an error, report via OrbitDesk → Admin → "Printer" (printers are managed by Facilities, not IT).

## Slow laptop
1. Restart (many issues are fixed by a restart; laptops not restarted for 7+ days are prompted).
2. Check for pending OS updates.
3. Free disk space: keep at least 15% free. Empty Downloads and Trash; Docker users run `docker system prune`.
4. Check Activity Monitor/Task Manager for runaway processes.
5. Still slow → OrbitDesk → IT → "Performance issue" (P3).

## Email and calendar (Google Workspace)
- Mailbox size: 30 GB. Archive old mail rather than deleting if needed for audit.
- Recover a deleted email: Trash keeps items for 30 days; after that IT can restore up to 25 days more via ticket.
- Shared calendar access: ask the owner to share; for room calendars see ADM-001.
- Out-of-office: Gmail → Settings → Vacation responder. Also set Slack status.

## Zoom / Google Meet
- Use Zoom for external meetings and Google Meet for internal.
- Screen sharing not working on Mac: System Settings → Privacy & Security → Screen Recording → enable Zoom/Chrome, then restart the app.
- Meeting room AV: rooms have Zoom Rooms controllers; tap "Meet Now" or join with the room code. AV issue → call Facilities ext. 2222.

## Slack
- Can't find a channel? It may be private—ask a member to add you.
- Guest (external) access to Slack Connect channels requires Security approval via OrbitDesk.
- Message retention: 2 years for channels, 1 year for DMs.

## Bluetooth headset not working
Remove the device, re-pair. On Windows, update the Intel Bluetooth driver from Company Portal.

## Disk encryption / compliance warnings
If you see "Device not compliant" in Okta, open Company Portal (Windows) or Self Service (Mac) → "Check compliance". Usually it requires an OS update or enabling FileVault/BitLocker.
