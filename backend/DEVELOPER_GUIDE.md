# Developer Guide — `hm-crm-*` Microservices

Single reference for onboarding to any CRM microservice. Covers folder structure, exception handling, logging, response format, and code writing conventions.

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Exception Handling](#2-exception-handling)
3. [Response Format](#3-response-format)
4. [Logging](#4-logging)
5. [Code Writing Conventions](#5-code-writing-conventions)
6. [Middleware Stack](#6-middleware-stack)
7. [Server Startup](#7-server-startup)

---

## 1. Folder Structure

```
hm-crm-<your-service-name>/
│
├── main.py                        # FastAPI app entry point
├── __init__.py
├── requirements.txt
├── docker-compose.yml
│
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── controller/            # Business logic layer
│       │   └── __init__.py
│       └── endpoint/              # Route definitions
│           └── __init__.py
│
├── config/                        # App config, env vars, settings
│   └── __init__.py
│
├── constants/                     # Enums, static values, messages
│   └── __init__.py
│
├── database/                      # DB connection, session setup
│   └── __init__.py
│
├── exceptions/                    # Custom exception classes
│   └── __init__.py
│
├── helpers/                       # Utility/helper functions
│   └── __init__.py
│
├── middlewares/                   # Custom middleware (auth, RBAC, etc.)
│   └── __init__.py
│
├── models/                        # SQLAlchemy ORM table definitions
│   └── __init__.py
│
├── schemas/                       # Pydantic + Marshmallow schemas
│   └── __init__.py
│
├── services/                      # External service integrations
│   └── __init__.py
│
├── worker/                        # Background tasks / Celery / Kafka
│   └── __init__.py
│
├── templates/                     # Email/HTML templates
│   └── images/
│
└── tests/
    └── __init__.py
```

### Layer Responsibilities

| Folder | Role |
|---|---|
| `endpoint/` | HTTP route handlers — thin, only parse request & delegate to controller |
| `controller/` | Business logic — orchestrates DB queries, services, helpers |
| `models/` | SQLAlchemy ORM table definitions |
| `schemas/` | Pydantic DTOs for request/response; Marshmallow for complex validation |
| `services/` | 3rd-party integrations (email, S3, payment, etc.) |
| `worker/` | Async background jobs (Celery, Kafka consumers) |
| `helpers/` | Pure utility functions shared across layers |
| `config/` | Env loading via Pydantic `BaseSettings` |
| `middlewares/` | JWT auth, CORS, RBAC |
| `exceptions/` | Custom HTTP/domain exception classes |
| `constants/` | Enums, string messages, magic values |

---

## 2. Exception Handling

### Exception Hierarchy (`exceptions/exceptions.py`)

All custom exceptions inherit from `BaseAPIException` which inherits from Python's `Exception`.

```python
class BaseAPIException(Exception):
    def __init__(self, message, status_code=400, error=None,
                 available_amount=None, required_amount=None):
        self.message = message
        self.status_code = status_code
        self.error = error
```

| Exception Class | HTTP Status | When to Use |
|---|---|---|
| `ValidationError` | 422 | Invalid input, failed schema validation |
| `UnauthorizedError` | 401 | Missing or invalid token |
| `ForbiddenError` | 403 | Authenticated but no permission |
| `NotFoundError` | 404 | Resource does not exist |
| `InternalServerError` | 500 | Unexpected server failure |
| `InsufficientBalanceError` | 402 | Payment-related failures |
| `PydanticValidationError` | 422 | Pydantic model validation with field-level errors |

### Raising Exceptions in Controllers

```python
from exceptions import NotFoundError, ValidationError
from constants import messages

# Simple raise
raise NotFoundError(message=messages.USER_NOT_FOUND)

# With error detail dict
raise ValidationError(errors={"field": "Invalid value"})

# Raise as HTTPException via generate_response (used for flow control)
raise response_parser.generate_response(
    status_code=status.HTTP_400_BAD_REQUEST,
    message=messages.NO_DATA_FOUND
)
```

### Try-Catch Pattern in Controllers

Every controller wraps its main logic in try-except. The exception is logged and a structured response is returned — never let raw exceptions bubble up to the endpoint.

```python
import logging
from helpers import response_parser
from constants import messages

logger = logging.getLogger(__name__)

def some_controller(payload: dict, db: Session, current_user_id: int):
    try:
        # ... business logic ...
        return response_parser.generate_response(
            status_code=200,
            message=messages.DATA_FOUND,
            data=result
        )
    except Exception as e:
        logger.exception(f"some_controller failed: {e}")
        return response_parser.generate_response(
            status_code=500,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False
        )
```

### Pydantic Validation — Structured Field Errors

`PydanticValidationError` automatically extracts field-level errors from Pydantic's `exc.errors()`:

```json
{
  "status_code": 422,
  "message": "Validation error",
  "data": {},
  "success": false,
  "error": {
    "field_name": ["error message"],
    "nested.field": ["error message"]
  }
}
```

---

## 3. Response Format

All API responses follow a single unified schema (`schemas/api_response.py`):

```json
{
  "status_code": 200,
  "message": "Data found successfully",
  "data": {},
  "success": true
}
```

### `generate_response()` — `helpers/response_parser.py`

Always use this helper. Never return raw dicts or construct `JSONResponse` manually in controllers.

```python
from helpers.response_parser import generate_response
from fastapi import status

# Success — returns JSONResponse
return generate_response(
    status_code=status.HTTP_200_OK,
    message="Data found",
    data={"key": "value"}
)

# Error — returns HTTPException, must be raised
raise generate_response(
    status_code=status.HTTP_400_BAD_REQUEST,
    message="Something went wrong",
    success=False
)
```

**Rules:**
- `200, 201, 202, 204` → returns `JSONResponse`
- Any other status code → returns `HTTPException` (must be `raise`d)
- `data` defaults to `[]`; pass a `dict` or `list` as needed

### Marshmallow Error Extraction

Use `extract_marshmallow_error()` to normalize a Marshmallow `ValidationError` into a single string:

```python
from helpers.response_parser import extract_marshmallow_error
from marshmallow import ValidationError as MarshmallowError

try:
    validated = MySchema().load(payload)
except MarshmallowError as e:
    msg = extract_marshmallow_error(e)
    raise generate_response(status_code=422, message=msg, success=False)
```

---

## 4. Logging

### Setup (`main.py`)

Logging is configured at app startup using a custom `ArchiveRotatingFileHandler`:

- Format: `%(asctime)s - %(levelname)s - %(message)s`
- Default level: `ERROR`
- Log file: `APP_LOG_FILE` env var (default `app.log`)
- Max size: `APP_LOG_MAX_BYTES` env var (default 20 MB)
- On rollover: archived to `log_archive/` with `<index>_<start>_to_<end>_app.log` naming

### Module-Level Logger Pattern

Declare at the top of every controller, helper, or service file. Never use `print()` for errors.

```python
import logging

logger = logging.getLogger(__name__)

# Inside a function:
logger.exception(f"Failed to fetch order: {e}")   # logs full traceback — use inside except
logger.error(f"Order not found: order_id={oid}")   # known error state, no traceback
logger.info("Order list fetched successfully")      # significant non-error events
```

**When to use which level:**
| Method | When |
|---|---|
| `logger.exception(msg)` | Inside `except` block — auto-attaches full traceback |
| `logger.error(msg)` | Known error condition without an active exception |
| `logger.info(msg)` | Significant non-error events |
| `logger.debug(msg)` | Avoid in production-facing paths |

### Audit Logging (`helpers/logging_helper.py`)

For business-level audit trails (who changed what, from → to, when), use `action_logs()`. Stored in MongoDB via the `audit_log` library.

```python
from helpers.logging_helper import action_logs

action_logs(
    db=db,
    action="appointment_rescheduled",   # maps to a pre-defined log text template
    order_appointment_id=appt_id,
    updated_by=current_user_id,
    old_value=old_date,
    new_value=new_date,
)
```

40+ action types are supported with pre-defined message templates in `logging_helper.py`.

---

## 5. Code Writing Conventions

### Controller (`api/v1/controller/<feature>_controller.py`)

- One function per API action, plain functions (not classes)
- Signature: `def <action>_controller(payload: dict, db: Session, current_user_id: int)`
- Always declare `logger` and `env_vars` at module top
- Wrap body in `try/except Exception`; log the exception; return error response
- Return value is always the result of `generate_response()`

```python
import logging
from sqlalchemy.orm import Session
from helpers import response_parser
from helpers.get_env_vars import get_settings
from constants import messages

logger = logging.getLogger(__name__)
env_vars = get_settings()

def create_something_controller(payload: dict, db: Session, current_user_id: int):
    try:
        # validate → query → compute → respond
        return response_parser.generate_response(
            status_code=200,
            message=messages.DATA_FOUND,
            data=result
        )
    except Exception as e:
        logger.exception(f"create_something_controller: {e}")
        return response_parser.generate_response(
            status_code=500,
            message=messages.INTERNAL_SERVER_ERROR,
            success=False
        )
```

### Endpoint (`api/v1/endpoint/<feature>_endpoint.py`)

- Routes are thin: validate input → call controller → return result
- Always inject `current_user` via `Depends(get_current_user)`
- Always inject `db` via `Depends(get_db)`
- Validate request body with Marshmallow schema before passing to controller
- No business logic in endpoints

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.db_engine import get_db
from helpers.jwt_token import get_current_user
from schemas.user_schema import User
from schemas import some_schema
from api.v1.controller.some_controller import some_action_controller

router = APIRouter()

@router.post("/action")
def some_action(
    request_data: some_schema.SomeRequestModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validated = some_schema.SomeMarshSchema().load(request_data.model_dump())
    return some_action_controller(
        payload=validated,
        db=db,
        current_user_id=current_user.id,
    )
```

### Schemas

- Use **Pydantic** for request/response body models
- Use **Marshmallow** for complex validation (cross-field, DB-dependent checks)
- Keep schema files per feature: `schemas/<feature>_schema.py`

### Constants & Messages

All user-facing strings live in `constants/messages.py`. Never hardcode message strings in controllers or endpoints.

```python
# constants/messages.py
DATA_FOUND = "Data found successfully."
NO_DATA_FOUND = "No data found."
INTERNAL_SERVER_ERROR = "Something went wrong. Please try again."
VALIDATION_ERROR = "Validation error."
```

### Database Queries

- Session is always passed as a dependency, never imported globally
- Use `crm_db_service.crud.common_actions.crud.get_records` for simple reads
- Use `update_data` / `add_data` from the same module for writes
- For complex queries, use SQLAlchemy ORM directly: `.query()`, `.filter()`, `.join()`

---

## 6. Middleware Stack

Applied in `main.py` in this order:

```
Request
    ↓
CORSMiddleware
    └── Allows all origins (configure per env if needed)
    ↓
TokenVerificationMiddleware
    ├── Extracts Bearer token from Authorization header
    ├── Decodes JWT (python-jose)
    ├── Fetches admin user from DB
    └── Populates request.state.user
    ↓
RBACMiddleware  (available, currently commented out)
    └── Validates role/permissions via external RBAC engine
    ↓
Route Handler
    └── Access current user via Depends(get_current_user)
```

Paths listed in `constants/EXCLUDED_PATHS` skip both auth middlewares (webhooks, docs, public endpoints).

---

## 7. Server Startup

| Environment | Server | Config |
|---|---|---|
| Linux (dev) | Uvicorn | `reload=True`, port from `settings.port` |
| Linux (prod) | Uvicorn | `reload=False`, port from `settings.port` |
| Non-Linux (Mac/Windows) | Gunicorn + UvicornH11Worker | 8 workers, 2 threads, 120s timeout, 1000 max requests |
