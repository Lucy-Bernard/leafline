# Commands

| Task    | Command                                            |
| ------- | -------------------------------------------------- |
| Install | `uv sync`                                          |
| Run     | `uv run fastapi dev main.py`                       |
| Lint    | `uv run ruff check .`                              |
| Format  | `uv run ruff format .`                             |
| Test    | `uv run pytest path/to/test_file.py::test_name -v` |

---

# Architecture

This project uses **Hexagonal Architecture** (also called Ports & Adapters). The idea is simple: **the core business logic never knows anything about the outside world** (databases, HTTP, third-party APIs). Everything external talks to the core through interfaces (called "ports"), and the concrete implementations (called "adapters") live on the outside.

## How a Request Flows Through the App

### Incoming request (someone calls your API):

```
HTTP Request
  → Controller        (receives the request, packages it into a DTO)
  → Service Interface (the contract — what can be done)
  → Service Impl      (the actual logic)
  → Domain Model      (the core data/business rules)
```

### Outgoing call (your app needs to hit a DB or external API):

```
Service Impl
  → Repository/Adapter Interface  (the contract — what storage/external calls look like)
  → Repository/Adapter Impl       (the actual SQLAlchemy query or API call)
  → Database / External API
```

## The One Rule That Matters Most

> **Dependencies always point inward.** The core (services, domain) never imports from controllers, repositories, or adapters. Those outer layers import from the core — never the reverse.

---

# Folder Structure

```
/config/              # Database setup, dependency injection wiring, env config
/controller/          # API endpoints — receive requests, return responses
/dto/                 # Data shapes passed between controllers and services
/service/             # Service interfaces (what the app can do)
  /impl/              # Actual service implementations (how it does it)
/repository/          # Repository interfaces (what storage operations look like)
  /impl/              # Actual DB implementations (SQLAlchemy, etc.)
/adapter/             # External service interfaces (payment, email, etc.)
  /impl/              # Actual external service implementations
/domain/
  /model/             # Pydantic models — validation and business rules
  /orm/               # SQLAlchemy ORM models — DB-specific, never leave this layer
  /enum/              # Shared enumerations
  /error/             # Custom exception classes
  /prompt/            # AI prompt templates
/factory/             # Complex object creation logic
/decorators/          # Custom decorators (auth, logging, task queues)
/callback/            # Async/AI event handlers
/template/            # Reusable execution templates
```

---

# Rules to Follow

## 1. Every `impl` must have an interface

If you create `service/impl/user_service.py`, there must be a matching interface at `service/user_service_interface.py` that it implements.

## 2. Controllers only speak DTOs

All data coming into or going out of a controller must be a DTO from `/dto/`. No raw dicts, no ORM models.

## 3. Keep ORM models out of the service layer

ORM models (`/domain/orm/`) are a database detail. The repository layer maps between ORM models and Pydantic models. Services only ever see Pydantic models — never SQLAlchemy objects.

**Validation happens at the top of every service method:**

```python
validated = MyPydanticModel.model_validate(dto.model_dump())
```

## 4. Inject dependencies — never instantiate them inside a class

Wrong:

```python
class UserService:
    def __init__(self):
        self.repo = UserRepository()  # ❌ hardcoded dependency
```

Right:

```python
class UserService:
    def __init__(self, repo: UserRepositoryInterface):  # ✅ injected
        self.repo = repo
```

All wiring happens in `/config/` — that's the only place objects are created and connected.

**Dependency flow:** `Controller → Service → Repository / Adapter / Factory`

## 5. Unit of Work for agent/autonomous services

Any service that touches "agent autonomy" features must use the Unit of Work pattern to keep operations transactional (required for taskiq compatibility).

---

# Python Style

```python
# Exception handling — always name it `error`, never `e`
try:
    ...
except Exception as error:
    logging.exception(error)  # only use logging.exception inside except blocks

# Type annotations — use X | Y union syntax
def get_user(user_id: int | None = None) -> User | None:
    ...

# Type checking
if isinstance(value, str):  # ✅
    ...
```

---

# Writing Tests

## Step 1: Write the plan first, code second

Before any test code, document your test plan covering:

- **Input Partitions** — different categories of valid/invalid inputs
- **Output Partitions** — different categories of results
- **Input Combinations** — how inputs interact
- **Boundary Analysis** — exact edges, just inside, just outside

## Step 2: Test design approach

- **Primary:** Black-box (spec-based) — test behavior from the outside based on requirements
- **Secondary:** White-box (structural) — ensure every branch in the code is hit

## Step 3: Implementation rules

**Every test must follow this naming format:**

```
IP.1.test_valid_email       # Input Partition
OP.1.test_returns_user      # Output Partition
IPC.1.test_name_and_email   # Input Combination Partition
BA.1.test_empty_string      # Boundary Analysis
```

**Group tests by partition in the file** — don't scatter them randomly.

**Use `pytest.mark.parametrize`** when testing the same logic with multiple values:

```python
@pytest.mark.parametrize("email", ["", " ", None])
def test_BA_1_invalid_email(email):
    ...
```
