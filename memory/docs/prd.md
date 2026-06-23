# Product Requirements Document (PRD)

## Product Vision

A real-time, high-concurrency unit allocation platform for real estate launches. The system automates pre-allocation, competitive booking, cascading unit-drop logic, refunds, and admin oversight — all without human intervention during the live event.

---

## Target Users

| User Type | Description |
|-----------|-------------|
| Registered Customer | Has a GHNG number, participates in allocation |
| Admin / Strategy Team | Controls inventory gates, can manually assign units |
| M&SS Team | Reviews and approves cancellation/refund requests |
| Finance Team | Second-level refund approver |
| Pre-Audit Team | Third-level refund approver |
| Banking Team | Final refund executor |

---

## Features & Requirements

### P0 — Must Have

#### F1: Pre-Allocation Engine
- Pre-assign 3 customers per unit across all active towers before Allocation Day 1.
- Customers assigned based on GHNG number mapping (target: 5,000 mappings).
- Band assignment: 35 floors split into 4 bands of 7 floors each.
  - B5: Floor 29–35
  - B4: Floor 22–28
  - B3: Floor 15–21
  - B1+B2: Floor 01–14

#### F2: Competitive Allocation (Fastest Finger First)
- When a customer's session opens, they see their pre-allocated unit.
- System shows competition (other pre-allocated + missed customers on same unit).
- First customer to pay secures the unit; others immediately drop to next available.

#### F3: Band-Drop Algorithm (Next Available Unit)
- When a customer is displaced, the algorithm finds the next available unit:
  1. Drop one band within the same tower (B5 → B4 → B3 → B2+B1)
  2. Within the band, search **top to bottom** floor
  3. Within the floor, search **left to right** unit
- If no bands remain in the current tower → move to next tower in sequence (starting from B5 of that tower).

#### F4: Hold Logic
- System holds the next available unit for the displaced customer for **30 minutes** or until it's taken by another customer (whichever comes first).
- If hold expires, algo finds the next available unit again.

#### F5: Dummy Customer / Inactivity Lock
- If no customer pays within **15 minutes** on a unit → dummy customer books the unit.
- Displaced non-paying customers are moved to next available unit.
- Dummy user blocks the unit post **15 minutes of inactivity**.

#### F6: Customer Cap per Unit
- Max **10 customers** on a single unit at any time.
- 11th customer auto-routes to next available unit.

#### F7: Tower Sequencing
- System respects the 18-tower sequence (see architecture.md).
- 1st Preference towers (RERA Approved): active by default.
- 2nd and 3rd Preference towers: opened by admin/strategy team only.

#### F8: Allocation Day 2 — Open Booking
- No pre-allocation on Day 2 (2nd Oct).
- Open first-come-first-served booking for all registered customers.
- UX similar to BookMyShow.com seat selection.

#### F9: Refund Workflow
- Customer-initiated cancellation → double confirmation → cancellation bucket.
- Sequential approval chain: M&SS → Finance → Pre-Audit → Banking.
- Each stage: view full details + Easebuzz Transaction ID, approve or reject with reason.
- Rejection notifies all upstream departments with reason.
- Banking enters refund reference ID (visible to all departments).
- M&SS master dashboard shows all cases with stage status (green check / red cross).

#### F10: Admin Panel
- Toggle 2nd/3rd preference inventory on/off.
- Manually assign a GHNG number to a specific unit.
- Dashboard: allocated + waitlisted customers per unit and per tower.

### P1 — Should Have

- Real-time seat map view (tower/floor/unit grid) for admin.
- Customer-facing countdown timer (30-minute hold expiry).
- Notification to customer on unit change (SMS / in-app).
- Audit log of all unit state transitions.

### P2 — Nice to Have

- Customer can express preference for a floor range before allocation day.
- Tower-level analytics (fill rate, drop rate, average time to allocate).
- Export of final allocation report post-event.

---

## Out of Scope

- Payment gateway integration (Easebuzz assumed pre-integrated).
- CRM / ERP sync (handled separately).
- Physical registration process.

---

## Acceptance Criteria

- Zero units double-booked during a concurrent allocation session.
- Band-drop algorithm finds next available unit in < 2 seconds under load.
- Dummy customer triggers exactly at 15-minute mark, no sooner.
- Refund workflow correctly gates each stage (no skipping M&SS → Finance → Pre-Audit → Banking).
- Admin GHNG override works but is superseded by faster-paying competing customers.
