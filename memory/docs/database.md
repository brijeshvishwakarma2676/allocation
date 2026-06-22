# Database Design

## Key Entities

### towers
| Column | Type | Notes |
|--------|------|-------|
| id | string | e.g., "Tower8" |
| name | string | e.g., "Crest" |
| preference | int | 1, 2, or 3 |
| sequence | int | 1–18 |
| is_active | bool | admin-controlled |
| total_floors | int | 35 |
| units_per_floor | int | 8 |

### units
| Column | Type | Notes |
|--------|------|-------|
| id | string | e.g., "3102" = Tower 8, Floor 31, Unit 02 |
| tower_id | FK | → towers |
| floor | int | 1–35 |
| band | enum | B1, B2, B3, B4, B5 |
| unit_no | int | 1–8 |
| size_sqft | int | 322 / 484 / 621 |
| status | enum | AVAILABLE, PRE_ALLOCATED, HOLD, COMPETING, ALLOCATED, CANCELLED |
| allocated_to_ghng | string | null until allocated |
| allocated_at | timestamp | |

### customers
| Column | Type | Notes |
|--------|------|-------|
| ghng | string (PK) | registration number |
| name | string | |
| phone | string | |
| registered_at | timestamp | |
| unit_type_preference | string | 1BHK / 2BHK etc. |

### unit_allocations
Tracks which customers are competing/waiting on which unit.

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | |
| unit_id | FK | → units |
| ghng | FK | → customers |
| status | enum | PRE_ALLOCATED, COMPETING, ALLOCATED, DISPLACED, HOLD |
| hold_expires_at | timestamp | null unless HOLD |
| assigned_at | timestamp | |
| paid_at | timestamp | null until payment |
| easebuzz_txn_id | string | null until payment |

### cancellations
| Column | Type | Notes |
|--------|------|-------|
| id | string | CXL-001 etc. |
| ghng | FK | → customers |
| unit_id | FK | → units |
| reason | text | customer provided |
| stage | enum | MANDS_REVIEW, FINANCE_REVIEW, PRE_AUDIT_REVIEW, BANKING, COMPLETE, REJECTED |
| created_at | timestamp | |
| refund_reference_id | string | entered by Banking |

### cancellation_stage_log
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | |
| cancellation_id | FK | → cancellations |
| stage | enum | |
| action | enum | APPROVED, REJECTED |
| actor_role | string | MANDS, FINANCE, PRE_AUDIT, BANKING |
| reason | text | on rejection |
| actioned_at | timestamp | |

---

## Key Indexes

- `units(tower_id, floor, band, status)` — for fast next-available-unit lookup
- `unit_allocations(unit_id, status)` — for counting waiting customers per unit
- `unit_allocations(ghng, status)` — for customer's current unit
- `cancellations(stage)` — for department dashboards

---

## Constraints

- `unit_allocations`: max 10 rows with status IN (PRE_ALLOCATED, COMPETING, HOLD) per `unit_id`
- `units.status`: only one customer can have `status = ALLOCATED` per unit
- Soft deletes only — no hard deletes on unit_allocations (audit trail)
