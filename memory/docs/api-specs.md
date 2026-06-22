# API Specifications

## Base URL

`/api/v1/`

## Authentication

- GHNG number + OTP for customers
- Role-based auth (Admin, M&SS, Finance, Pre-Audit, Banking) for internal portals

---

## Customer Endpoints

### GET /allocation/my-unit
Returns the pre-allocated unit for the logged-in customer.

```json
Response 200:
{
  "ghng": "GHNG12345",
  "unit": {
    "id": "3102",
    "tower": "Tower 8",
    "towerName": "Crest",
    "floor": 31,
    "band": "B5",
    "unitNo": 2,
    "size": 322,
    "status": "PRE_ALLOCATED"
  },
  "competingCustomers": 2,
  "holdExpiresAt": null
}
```

### POST /allocation/pay
Customer pays for their current allocated / held unit.

```json
Request:
{
  "ghng": "GHNG12345",
  "unitId": "3102",
  "easebuzzTransactionId": "EBZ_XYZ123"
}

Response 200:
{
  "success": true,
  "allocatedUnit": "3102",
  "message": "Unit successfully allocated to you."
}

Response 409 (unit already taken):
{
  "success": false,
  "nextUnit": { ...unit object... },
  "holdExpiresAt": "2024-09-28T10:30:00Z"
}
```

### POST /cancellation/request
Customer initiates cancellation.

```json
Request:
{
  "ghng": "GHNG12345",
  "unitId": "3102",
  "reason": "Change of plan"
}

Response 200:
{
  "cancellationId": "CXL-001",
  "status": "PENDING_MANDS_REVIEW",
  "message": "Cancellation request submitted. Awaiting M&SS review."
}
```

### GET /cancellation/status/:cancellationId
Returns current stage of refund workflow.

```json
Response 200:
{
  "cancellationId": "CXL-001",
  "stage": "FINANCE_REVIEW",
  "stages": [
    { "name": "M&SS Review", "status": "APPROVED" },
    { "name": "Finance Review", "status": "IN_PROGRESS" },
    { "name": "Pre-Audit Review", "status": "PENDING" },
    { "name": "Banking", "status": "PENDING" }
  ],
  "refundReferenceId": null
}
```

---

## Admin Endpoints

### POST /admin/enable-preference
Enable 2nd or 3rd preference towers.

```json
Request:
{
  "preference": 2
}
Response 200: { "success": true }
```

### POST /admin/assign-unit
Manually assign a GHNG number to a unit.

```json
Request:
{
  "ghng": "GHNG99999",
  "unitId": "1501"
}
Response 200: { "success": true }
```

### GET /admin/dashboard
Returns real-time allocation state per unit and tower.

```json
Response 200:
{
  "towers": [
    {
      "towerId": "Tower 8",
      "towerName": "Crest",
      "totalUnits": 247,
      "allocated": 143,
      "competing": 12,
      "available": 92,
      "units": [...]
    }
  ]
}
```

---

## Refund Workflow Endpoints

### POST /refund/:stage/review
Used by M&SS, Finance, Pre-Audit, Banking.

```json
Request:
{
  "cancellationId": "CXL-001",
  "action": "APPROVE" | "REJECT",
  "reason": "optional rejection reason",
  "refundReferenceId": "REF_BANK_001"   // Banking only
}

Response 200:
{
  "success": true,
  "nextStage": "PRE_AUDIT_REVIEW" | "COMPLETE" | "REJECTED"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden (wrong role) |
| 404  | Unit / Customer not found |
| 409  | Conflict (unit already taken) |
| 429  | Too Many Requests (rate limit) |
| 500  | Internal Server Error |
