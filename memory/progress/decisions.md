# Decision Log

## Decision 1: Tower Allocation Sequence
**Date:** (from source doc)  
**Decision:** 18 towers are sequenced into 3 preference groups. By default, only 1st Preference (RERA-approved) towers are active on Allocation Day 1.  
**Rationale:** RERA-approved towers carry higher buyer confidence and regulatory clearance; must be sold first.  
**Outcome:** Admin can enable 2nd/3rd preference towers in real time based on Day 1 demand.

---

## Decision 2: Band Segmentation (4 Bands of 7 Floors)
**Date:** (from source doc)  
**Decision:** 35 floors divided into 4 bands (B5: 29–35, B4: 22–28, B3: 15–21, B1+B2: 01–14).  
**Rationale:** Bands create a fair cascading drop mechanism — customers displaced from high floors move to progressively lower floors rather than random units, preserving a sense of fairness.  
**Outcome:** Band-drop is the primary unit movement mechanism.

---

## Decision 3: 3 Customers per Unit Pre-Allocation
**Date:** (from source doc)  
**Decision:** Pre-allocate exactly 3 registered customers per unit.  
**Rationale:** Registration-to-unit ratio is ~2.8:1 at the time of document creation, expected to reach ~3:1 by Allocation Day. Three customers create competitive pressure without overwhelming customers with too many competitors.  
**Outcome:** GHNG mapping list of 5,000 numbers to be prepared.

---

## Decision 4: Dummy Customer / 15-Minute Inactivity Rule
**Date:** (from source doc)  
**Decision:** If no customer pays within 15 minutes of a unit session opening, a dummy customer books the unit and displaces non-paying customers.  
**Rationale:** Prevents units from being locked indefinitely by non-responsive customers, keeping allocation moving at pace.  
**Outcome:** System must implement a background timer per unit session.

---

## Decision 5: Max 10 Customers per Unit
**Date:** (from source doc)  
**Decision:** No more than 10 customers can wait on a single unit at any point.  
**Rationale:** More than 10 simultaneous competitors creates an unmanageable UX and system load per unit.  
**Outcome:** 11th customer auto-routed to next available unit immediately.

---

## Decision 6: Two Allocation Days
**Date:** (from source doc)  
**Decision:** Allocation Day 1 (28th Sep) = pre-allocated competitive booking. Allocation Day 2 (2nd Oct) = open first-come-first-served for all registered customers.  
**Rationale:** Day 1 rewards registered customers with a pre-allocated unit advantage. Day 2 clears remaining inventory openly.  
**Outcome:** System must support two distinct booking modes.

---

## Decision 7: Multi-Stage Refund Approval (M&SS → Finance → Pre-Audit → Banking)
**Date:** (from source doc)  
**Decision:** Refunds require sequential sign-off from four internal departments before money is returned.  
**Rationale:** Internal compliance and financial controls require multi-level approval for fund disbursement.  
**Outcome:** System needs a configurable workflow engine with role-based access per stage.
