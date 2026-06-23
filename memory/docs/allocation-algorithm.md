# Allocation Algorithm — Detailed Specification

## Overview

EstateAllocator uses a **band-drop, fastest-finger-first** algorithm to allocate 2,223 units to thousands of registered customers on a competitive launch day. This document is the authoritative spec for implementing the core algorithm.

---

## Phase 1: Pre-Allocation (Before Allocation Day 1)

**Trigger:** Allocation Day 1 preparation (by 28th Sep)  
**Goal:** Assign 3 registered customers to every unit across all active towers.

### Rules
1. Active towers on Day 1 = 1st Preference towers only (sequences 1–9).
2. Each of the 2,223 units gets exactly 3 GHNG-numbered customers assigned.
3. Customer is assigned a **specific unit** (e.g., Unit 3102 = Tower 8, Floor 31, Unit 02).
4. Bands apply only for drop logic — pre-allocation distributes across all floors.

### GHNG Mapping
- Target list: 5,000 GHNG numbers mapped to units for Day 1.
- 3 customers per unit × 2,223 units = 6,669 slots → covered by 5,000 active + waiting pool.

---

## Phase 2: Allocation Day 1 (28th Sep) — Competitive Booking

### Session Start
- Customer logs in with GHNG number.
- System displays pre-allocated unit with competition count (other customers on same unit).

### Competitive Outcome: Case 1 — Outcompeted
**Scenario:** Another customer pays for Ankit's pre-allocated unit 3102.

```
1. Unit 3102 (Tower 8, Floor 31, B5) → taken by competitor
2. Algorithm triggers for Ankit:
   a. Drop to B4 (Floor 22–28)
   b. Check floors top to bottom starting at Floor 28
   c. Check units left to right starting at Unit 2801
   d. First available unit found → e.g., Unit 2805
3. System presents Unit 2805 to Ankit with competition pool
   (pre-allocated customers + missed customers from earlier session)
4. Ankit pays → Unit 2805 allocated to Ankit
```

### Competitive Outcome: Case 2 — Late Login / Hold Expiry
**Scenario:** Ankit doesn't login on time; system holds a unit for him.

```
1. Unit 3102 taken by competitor while Ankit is inactive
2. Algo finds Next Available Unit → Unit 2805
3. Algo holds Unit 2805 for Ankit for 30 minutes
   (or until another customer pays — whichever comes first)
4. Before Ankit logs in, Unit 2805 is taken by another customer
5. Algo finds next → Unit 1601
6. Ankit logs in, sees Unit 1601, pays → allocated
```

**Hold rules:**
- Hold duration: **30 minutes** per slot
- Hold breaks immediately if another customer pays for the held unit
- System continuously finds and holds the next available unit for displaced customers

### Competitive Outcome: Case 3 — Tower Exhausted
**Scenario:** Ankit's pre-allocated unit is 702 (Tower 8, Floor 7). All bands in Tower 8 are fully allocated.

```
1. Unit 702 not paid → algo looks for next unit in Tower 8
2. No bands remain in Tower 8 → Tower Change triggered
3. Algo moves to next tower in sequence (Tower 9 — Triumph)
4. Starts from B5 of Tower 9 (Floor 35 downwards)
5. Checks left to right units
6. Next Available Unit for Ankit: Unit 2601 (Tower 9)
7. Ankit pays → Unit 2601 allocated
```

---

## Phase 3: Allocation Day 2 (2nd Oct) — Open Booking

- Pre-allocation is **disabled**.
- All registered customers compete freely.
- First-come-first-served (BookMyShow-style seat selection).
- Band-drop logic still applies if a unit is taken before checkout.

---

## Macro Rules Summary

| # | Rule |
|---|------|
| 1 | Floors segmented into 4 bands (7 floors each). Pre-allocation uses all floors. |
| 2 | 3 customers pre-allocated per unit. All 3 compete simultaneously on session open. |
| 3a | If one of 4 customers books → other 3 are moved per band-drop logic. |
| 3b | If none books in 15 min → dummy customer books it; displaces all non-paying customers. |
| 4i | Drop logic: customer drops to next band within same tower (B5→B4→B3→B1+B2). |
| 4ii | Within band: search top to bottom floor. |
| 4iii | Within floor: search left to right (same unit type only). |
| 5 | Max 10 customers on one unit at any time. 11th auto-routes to next available unit. |
| 6 | Dummy user blocks unit after 15 minutes of in-activity. |

---

## Algorithm Pseudocode

```
PRE_ALLOCATION:
  for each unit in activeTowers:
    assignedCustomers = pickNext3FromGHNGList()
    unit.preAllocated = assignedCustomers

ON_UNIT_TAKEN(displacedCustomer, displacedFromUnit):
  nextUnit = findNextAvailableUnit(displacedCustomer, displacedFromUnit)
  if nextUnit:
    holdUnit(nextUnit, displacedCustomer, durationMinutes=30)
    notifyCustomer(displacedCustomer, nextUnit)

findNextAvailableUnit(customer, fromUnit):
  tower = fromUnit.tower
  band  = getBand(fromUnit.floor)

  while tower in towerSequence:
    band = band - 1  // drop one band
    while band >= B1:
      for floor in band.floors (top to bottom):
        for unit in floor.units (left to right, same type):
          if unit.status == AVAILABLE and unit.waitingCount < 10:
            return unit
      band = band - 1

    // no bands left in tower, move to next
    tower = nextInSequence(tower)
    band  = B5

  return null

INACTIVITY_CHECK (runs every minute):
  for each unit with status == COMPETING:
    if unit.lastActivity > 15 minutes:
      dummyCustomer.book(unit)
      for customer in unit.waitingCustomers:
        triggerDrop(customer, unit)
```

---

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| 11th customer tries to join a unit | Auto-route to next available unit |
| All units in all active towers exhausted | Customer shown "No units available" |
| Admin assigns GHNG to a unit already being competed for | Customer sees the unit but fastest-finger still applies |
| Customer's hold expires before they log in | Algo finds new next available unit, new hold starts |
| 2nd/3rd preference not yet enabled by admin | Algo does not route to those towers |
