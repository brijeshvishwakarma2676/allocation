# Backlog

| # | Task | Priority | Area | Notes |
|---|------|----------|------|-------|
| 1 | Define tech stack (frontend, backend, DB, hosting) | P0 | Architecture | Unblocks all implementation |
| 2 | Set up project repo and CI/CD pipeline | P0 | DevOps | |
| 3 | Design database schema and run migrations | P0 | Backend | See docs/database.md |
| 4 | Implement pre-allocation engine (GHNG → unit mapping) | P0 | Backend | 5,000 GHNG target |
| 5 | Implement band-drop algorithm (Next Available Unit) | P0 | Backend | See docs/allocation-algorithm.md |
| 6 | Implement hold logic (30-min unit hold per customer) | P0 | Backend | |
| 7 | Implement dummy customer / 15-min inactivity trigger | P0 | Backend | Background job / timer |
| 8 | Implement 10-customer cap per unit | P0 | Backend | |
| 9 | Implement tower sequencing and preference gates | P0 | Backend | Admin toggles 2nd/3rd pref |
| 10 | Customer-facing allocation session UI | P0 | Frontend | Show unit, competition, hold timer |
| 11 | Easebuzz payment integration | P0 | Backend | Payment gateway |
| 12 | Refund workflow — multi-stage approval engine | P0 | Backend | M&SS→Finance→Pre-Audit→Banking |
| 13 | Admin panel — inventory gate controls | P0 | Frontend | Enable/disable preference groups |
| 14 | Admin panel — manual GHNG-to-unit assignment | P0 | Frontend | |
| 15 | Admin dashboard — real-time unit/tower view | P0 | Frontend | Allocated + waitlisted |
| 16 | M&SS refund dashboard (pipeline view with stage status) | P0 | Frontend | Green check / red cross |
| 17 | Allocation Day 2 — open booking mode (BookMyShow style) | P0 | Backend+Frontend | No pre-allocation |
| 18 | Load testing for 10,000+ concurrent users | P1 | QA | Must pass before Day 1 |
| 19 | Customer notification on unit change (SMS / in-app) | P1 | Backend | |
| 20 | Audit log for all unit state transitions | P1 | Backend | |
| 21 | Tower-level analytics (fill rate, drop rate, time-to-allocate) | P2 | Backend | Post-event |
| 22 | Final allocation report export | P2 | Backend | Post-event |
