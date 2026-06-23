# Architecture

## System Overview

A high-concurrency real-time allocation engine for real estate launches. The core is a band-drop algorithm that manages unit pre-assignment and competitive booking across 18 towers and 35 floors.

---

## Project Scale

| Metric | Value |
|--------|-------|
| Total Towers (active on Day 1) | 9 (1st Preference) |
| Total Units | 2,223 |
| Units per Tower | 247 |
| Total Floors per Tower | 35 |
| Units per Floor | 8 |
| Customers per Unit (pre-allocated) | 3 |
| Max Customers per Unit (cap) | 10 |
| Estimated Registrations | 8,000–10,000+ |
| GHNG Mappings (Day 1 target) | 5,000 |

---

## Tower Sequence

| Seq | Tower No | Tower Name | Preference |
|-----|----------|-----------|------------|
| 1   | Tower 8  | Crest     | 1st (RERA Approved) |
| 2   | Tower 9  | Triumph   | 1st |
| 3   | Tower 10 | Crown     | 1st |
| 4   | Tower 13 | Prestige  | 1st |
| 5   | Tower 14 | Horizon   | 1st |
| 6   | Tower 15 | Radiance  | 1st |
| 7   | Tower 6  | Aspire    | 1st |
| 8   | Tower 7  | Blossom   | 1st |
| 9   | Tower 12 | Pinnacle  | 1st |
| 10  | Tower 16 | Fortune   | 2nd (Not RERA) |
| 11  | Tower 17 | Bright    | 2nd |
| 12  | Tower 18 | Grand     | 2nd |
| 13  | Tower 1  | Dawn      | 3rd (Not RERA) |
| 14  | Tower 2  | Aura      | 3rd |
| 15  | Tower 3  | Glory     | 3rd |
| 16  | Tower 4  | Pride     | 3rd |
| 17  | Tower 5  | Grace     | 3rd |
| 18  | Tower 11 | Prime     | 3rd |

> By default, only 1st Preference towers are active. Admin enables 2nd/3rd.

---

## Floor Band Segmentation

35 floors divided into 4 Bands (7 floors each):

| Band | Floor Range |
|------|-------------|
| B5   | Floor 29–35 |
| B4   | Floor 22–28 |
| B3   | Floor 15–21 |
| B1+B2 | Floor 01–14 |

---

## Unit Layout per Floor

| Unit | Size (sq ft) |
|------|-------------|
| Unit 1 | 322 |
| Unit 2 | 322 |
| Unit 3 | 621 |
| Unit 4 | 484 |
| Unit 5 | 322 |
| Unit 6 | 322 |
| Unit 7 | 484 |
| Unit 8 | 621 |

---

## Core Algorithm: Band-Drop Next Available Unit

```
function findNextAvailableUnit(customer, displacedFromUnit):

  currentTower = customer.tower
  currentBand  = getBand(displacedFromUnit.floor)

  while currentTower exists in sequence:
    nextBand = currentBand - 1   // Drop one band (B5→B4→B3→B1+B2)

    while nextBand >= B1:
      for floor in nextBand (top to bottom):
        for unit in floor (left to right, same unit type):
          if isAvailable(unit) and activeCustomers(unit) < 10:
            return unit

      nextBand = nextBand - 1

    // No bands left in current tower — move to next tower in sequence
    currentTower = nextTower(currentTower)
    currentBand  = B5   // Restart from Band 5 in new tower

  return null  // All units exhausted
```

---

## Key State Machine: Unit Status

```
AVAILABLE
  → PRE_ALLOCATED   (3 customers assigned)
  → HOLD            (customer displaced, held for 30 min)
  → COMPETING       (session open, customers racing to pay)
  → ALLOCATED       (payment confirmed)
  → CANCELLED       (customer cancellation initiated)
  → REFUND_PENDING  (in refund workflow)
```

---

## Timers & Thresholds

| Event | Timer |
|-------|-------|
| Hold duration per unit (per customer slot) | 30 minutes |
| Inactivity before dummy customer triggers | 15 minutes |
| Max customers competing on one unit | 10 |

---

## Admin Controls

- **Inventory gate:** Enable/disable 2nd and 3rd preference towers.
- **Manual GHNG assignment:** Assign a registration number to a specific unit. Customer then competes normally (fastest-finger-first still applies if others are competing).
- **Dashboard:** Per-unit and per-tower view of allocated + waitlisted customers.

---

## Refund Workflow Architecture

```
Customer Cancels
  → Double confirmation
  → [Cancellation Bucket]
       ↓
  M&SS Review (Nikesh Solanki — 91523 13464)
    Reject → notify customer with reason
    Approve → [Finance Bucket]
       ↓
  Finance Review
    Reject → notify M&SS with reason
    Approve → [Pre-Audit Bucket]
       ↓
  Pre-Audit Review
    Reject → notify Finance + M&SS with reason
    Approve → [Banking Bucket]
       ↓
  Banking
    Reject → notify Pre-Audit + Finance + M&SS with reason
    Execute → enter Refund Reference ID
              (visible to M&SS, Finance, Pre-Audit)
       ↓
  [REFUND COMPLETE]
```

M&SS master dashboard shows all cases with stage (green check = approved, red cross = rejected).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | _To be defined_ |
| Backend | _To be defined_ |
| Database | _To be defined_ |
| Payment Gateway | Easebuzz |
| Hosting | _To be defined_ |
