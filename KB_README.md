# Orbitra Technologies – Synthetic Internal Knowledge Base

A complete, fictional company knowledge base for building and evaluating **Self-RAG** and **Agentic RAG** internal assistants (an "OrbitBot" that deflects employee questions and tickets).

> Orbitra Technologies is a fictional ~1,450-person B2B SaaS company (HQ Bengaluru; offices in Pune, Hyderabad, Austin, London). All people, phone numbers, URLs and figures are invented. Today's reference date in the data is **19 Oct 2026**.

## Folder structure
```
orbitra_kb/
├── 00_company/            About, leadership & levels, glossary, announcements
├── 01_hr/                 Leave (India/US/UK), holidays, payroll, benefits, hybrid work,
│   │                      performance, onboarding, exit, code of conduct, POSH,
│   │                      referral & mobility, ESOPs & rewards
│   └── archive/           SUPERSEDED leave policy v4 (deliberate distractor)
├── 02_it/                 Support & SLAs, devices, VPN, accounts/MFA/access,
│                          acceptable use & AI tools, troubleshooting
├── 03_security/           InfoSec & data classification, incident/phishing reporting
├── 04_finance/            Expenses, travel, procurement, corporate card
├── 05_admin_facilities/   Office guide, transport, OrbitDesk ticketing guide
├── 06_legal_compliance/   Contracts/NDA, privacy & anti-bribery, whistleblower
├── 07_engineering/        Dev onboarding, git & code review, deployments, on-call
├── 08_product/            Product overview & plans, release notes
├── 09_sales_cs/           Support SLAs & escalation, pricing & discounts
├── 10_learning/           L&D budget, certifications
├── 11_faq/faqs.json       55 curated Q&A pairs with source doc IDs
├── data/
│   ├── employee_directory.csv   220 synthetic employees (structured lookups / SQL tool)
│   └── ticket_history_2026.csv  600 past OrbitDesk tickets (Jan–Oct 2026)
└── eval/eval_questions.jsonl    50 graded test questions with ground truth + gold docs
```

## Document format
Every Markdown doc has YAML front-matter you can load as chunk metadata:

| Field | Use in RAG |
|---|---|
| `doc_id` | Citation key; cross-references between docs use these IDs |
| `status` | `active` or `superseded` → filter or let the critic reject stale chunks |
| `version`, `effective_date`, `last_updated`, `supersedes` / `superseded_by` | Recency & conflict resolution |
| `applies_to` | Region/role filtering (India vs US vs UK, engineers only, etc.) |
| `classification` | Access control demo (Internal / Confidential) |
| `department`, `owner`, `tags` | Routing, hybrid search boosts, "who to contact" fallbacks |

Docs are table-heavy and cross-linked on purpose (e.g. FIN-001 → COM-002 approval matrix), which makes chunking strategy and multi-hop retrieval matter.

## Built-in challenges for Self-RAG / Agentic RAG
| Challenge | Where | What a good system does |
|---|---|---|
| Superseded content | `01_hr/archive/…v4_SUPERSEDED.md` (paternity 5 days, carry-forward 25, comp-off 30) vs active v5 (10 / 30 / 60) | Critic marks old chunk as not-supported/outdated; answer cites v5 |
| Region-specific answers | HR-LV-001/002/003, FIN-001 §7, HR-WFH-001 | Ask or infer location; never mix India EL into a US answer |
| Similar-but-different facts | Internal IT P1 SLA (IT-001, 15 min) vs customer P1 (CS-001, 30 min) | Retrieve the right context |
| Multi-hop | Notice period + EL encashment; expense + approval matrix; freeze + holiday | Decompose and retrieve iteratively |
| Calculations | Per diem half-days, notice buyout, on-call allowance | Use a calculator tool or careful reasoning |
| Time-sensitive | Holiday calendar, announcements, freeze windows | Use current date |
| Unanswerable | US dental benefits, pet insurance, net profit | Abstain + route to the right contact/ticket |
| Actions | "What's my leave balance?", "Raise a ticket" | Call tools instead of answering from text |

## Evaluation set (`eval/eval_questions.jsonl`)
Fields: `qid`, `type`, `difficulty`, `question`, `ground_truth`, `gold_docs`, optional `distractor_docs`, `expected_behavior`, `notes`.
Types: `single_hop`, `multi_hop`, `numerical`, `version_conflict`, `region_specific`, `ambiguous`, `temporal`, `policy_judgment`, `unanswerable`, `agentic_action`, `procedural`.

Suggested metrics: retrieval recall@k against `gold_docs`, answer correctness (LLM-judge vs `ground_truth`), faithfulness/groundedness, abstention accuracy on `unanswerable`, superseded-citation rate on `version_conflict`, tool-call accuracy on `agentic_action`.

## Ticket history (`data/ticket_history_2026.csv`)
Columns: `ticket_id, created_at, requester_id, requester_location, category, subcategory, subject, description, priority, status, resolution, resolution_time_hours, kb_article, deflectable_by_kb, csat`.
~75% of tickets are flagged `deflectable_by_kb = True` (answerable from the KB). Use it to:
- measure **ticket deflection**: replay ticket subjects through the bot and check whether it answers from `kb_article`;
- build a **ticket-routing classifier** / tool that pre-fills category & priority;
- show a "before vs after" deflection dashboard.

## Suggested agent tools (to mock)
| Tool | Backed by |
|---|---|
| `search_kb(query, filters)` | Vector/hybrid index over the Markdown docs |
| `lookup_employee(name/email/id)` | `employee_directory.csv` |
| `get_leave_balance(employee_id)` | Mock PeopleHub API (generate random balances) |
| `create_ticket(category, subcategory, summary, priority)` | Append to a tickets table |
| `search_similar_tickets(text)` | `ticket_history_2026.csv` |
| `calculator(expression)` | For per diem / buyout / allowance maths |
| `get_current_date()` | Returns 2026-10-19 for reproducible evals |

## Document index
| ID | Title |
|---|---|
| COM-001 | About Orbitra Technologies |
| COM-002 | Leadership, Org Structure and Job Levels |
| COM-003 | Glossary |
| COM-004 | Company Announcements (Jul–Oct 2026) |
| HR-LV-001 | Leave Policy – India (v5 active; v4 archived) |
| HR-LV-002 | PTO Policy – US |
| HR-LV-003 | Annual Leave Policy – UK |
| HR-HOL-2026 | Holiday Calendar 2026 – India |
| HR-PAY-001 | Payroll, Salary and Tax – India |
| HR-BEN-001 | Benefits and Insurance – India |
| HR-WFH-001 | Hybrid / Remote / WFA Policy |
| HR-PERF-001 | Performance, Promotions, Increments |
| HR-ONB-001 | New Joiner Onboarding Guide |
| HR-EXIT-001 | Resignation and Exit |
| HR-COC-001 | Code of Conduct |
| HR-POSH-001 | POSH Policy |
| HR-TA-001 | Referral Programme and Internal Mobility |
| HR-COMP-001 | ESOPs, RSUs, Recognition |
| IT-001 | IT Support and Service Catalog |
| IT-002 | Laptop and Device Policy |
| IT-003 | VPN Setup and Troubleshooting |
| IT-004 | Accounts, Passwords, MFA, Access |
| IT-005 | Acceptable Use and AI Tools |
| IT-006 | Common IT Issues – Self-Help |
| SEC-001 | Information Security and Data Classification |
| SEC-002 | Incident and Phishing Reporting |
| FIN-001 | Expense Reimbursement |
| FIN-002 | Business Travel |
| FIN-003 | Procurement and Vendor Payments |
| FIN-004 | Corporate Card |
| ADM-001 | Office and Facilities Guide |
| ADM-002 | Employee Transport – India |
| ADM-003 | OrbitDesk Ticketing Guide |
| LEG-001 | Contracts, NDAs, Signing Authority |
| LEG-002 | Data Privacy and Anti-Bribery |
| LEG-003 | Whistleblower Policy |
| ENG-001 | Developer Onboarding |
| ENG-002 | Git Workflow and Code Review |
| ENG-003 | Environments and Deployment |
| ENG-004 | On-Call and Incident Management |
| PRD-001 | Product Overview and Plans |
| PRD-002 | Release Notes 2026 |
| CS-001 | Customer Support SLAs and Escalation |
| SAL-001 | Pricing, Discounts, Deal Desk |
| LND-001 | Learning & Development |
