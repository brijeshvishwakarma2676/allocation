# Business Requirements Document (BRD)

## Project Overview

**Project Name:** Naigaon Allocation Logic & Algorithm  
**Client:** House of Abhinandan Lodha  
**Property:** Residential Development, Naigaon

A technology-driven flat allocation system for a large-scale residential launch event. The system pre-assigns units to registered customers and runs a real-time competitive allocation on Launch Day.

---

## Business Objectives

1. Fairly allocate 2,223 residential units across 18 towers to thousands of registered customers on launch day.
2. Prioritize RERA-approved towers (1st Preference) before opening non-RERA inventory.
3. Automate unit movement when customers fail to pay — eliminating manual intervention.
4. Handle a high-concurrency event (estimated 8,000–10,000+ registrations) without system conflict.
5. Provide admin control to intervene in edge cases while maintaining algorithmic fairness.
6. Enable a seamless refund workflow across M&SS, Finance, Pre-Audit, and Banking departments.

---

## Stakeholders

| Role | Name / Contact |
|------|---------------|
| Strategy Team | Internal (enables 2nd/3rd preference inventory) |
| M&SS SPOC | Nikesh Solanki — 91523 13464 |
| Finance Team | Internal |
| Pre-Audit Team | Internal |
| Banking Team | Internal |
| Tech Team | VernoraTech / OpenSpace |

---

## Business Requirements

### BR-1: Tower Preference Sequencing
- Allocations must start from 1st Preference towers (RERA Approved) only.
- 2nd and 3rd Preference towers open only on admin/strategy team command.
- Tower sequence within each preference group must be strictly followed (see Tower Sequence table in `architecture.md`).

### BR-2: Pre-Allocation
- Every unit must have exactly 3 registered customers pre-assigned before Allocation Day 1.
- Pre-allocation is based on GHNG registration numbers (target mapping list: 5,000).

### BR-3: Competitive Allocation — Fastest Finger First
- On Allocation Day 1 (28th Sep), each unit is competed for by 3 pre-allocated customers simultaneously.
- The first customer to pay secures the unit.
- Remaining 2 customers automatically drop to the next available unit per the algorithm.

### BR-4: Inactivity / No-Show Handling
- If no customer pays within **15 minutes**, a **dummy customer** takes over and books the unit.
- Displaced customers are pushed to the next available unit as per algo logic.
- The system holds a unit for a customer for **30 minutes** or until allocated to another customer — whichever comes first.

### BR-5: Customer Cap per Unit
- **Maximum 10 customers** can be waiting/competing on a single unit at any time.
- The 11th customer must be assigned the next available unit automatically.

### BR-6: Allocation Day 2 (2nd Oct)
- No pre-allocation. Open booking for all registered customers.
- Process similar to BookMyShow.com — first-come, first-served.

### BR-7: Refund Process
- Multi-department approval chain: M&SS → Finance → Pre-Audit → Banking.
- Customer must confirm cancellation twice before it enters the workflow.
- All departments can view full customer details + Easebuzz Transaction ID at their stage.
- Final refund reference ID entered by Banking is visible to all departments.

### BR-8: Admin Controls
- Admin can manually assign a GHNG number to a specific unit (customer then views and books it).
- Fastest-finger-first logic supersedes admin placement if other customers are competing.
- Dashboard view of allocated and waitlisted customers per unit and per tower.

---

## Constraints & Assumptions

- Only RERA-approved towers (1st Preference) are active on Allocation Day 1 by default.
- Registration-to-unit ratio is estimated at ~3:1 (3 customers per unit in the waiting pool).
- The system must handle concurrent sessions at scale (estimated 8,000–10,000 simultaneous users).
- Band-drop logic is the primary mechanism for unit movement — no random assignment.
- Easebuzz is the payment gateway.

---

## Success Criteria

- All 2,223 units allocated within Allocation Day 1 or Day 2 without manual reconciliation.
- Zero double-booking of units.
- Refund requests processed through the multi-department workflow without data loss.
- Admin dashboard reflects real-time allocation and waitlist state per unit and tower.
