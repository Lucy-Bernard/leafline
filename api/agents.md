# Commands

- Install: `uv sync`
- Run: `uv run fastapi dev main.py`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Single test: `uv run pytest path/to/test_file.py::test_function_name -v`

## **CORE ARCHITECTURE: Hexagonal (Ports & Adapters)**

Your design philosophy is rooted in hexagonal architecture, Domain-Driven Design (DDD), and SOLID principles. The primary goal is a modular, testable, and maintainable codebase achieved through strict separation of concerns and dependency inversion.

### **1. Architectural Flow**

#### **Primary (Driving) Side Flow: External Input to Application**

- **Path:** `External Actor (e.g., UI, API call) → Primary Adapter (Controller) → Primary Port (Service Interface) → Application Service → Domain Model`
- **Function:** The Primary Adapter (e.g., a FastAPI controller) receives an external request, transforms it into a command or query using a Data Transfer Object (DTO), and invokes the corresponding Application Service via its port (interface).

#### **Secondary (Driven) Side Flow: Application to External Output**

- **Path:** `Application Service → Secondary Port (Repository/Adapter Interface) → Secondary Adapter (Implementation) → External System (e.g., DB, API)`
- **Function:** The Application Service performs its logic and uses a Secondary Port (e.g., a repository interface) to request data or actions. The Secondary Adapter (e.g., a SQLAlchemy repository implementation) implements this port to interact with the external system.

### **2. The Golden Rule: Dependency Inversion**

**All source code dependencies MUST point inward toward the application core.**

- Adapters (Controllers, Repositories) depend on Ports (Service/Repository Interfaces).
- The Application Core (Services, Domain Models) has ZERO knowledge of outside technologies or frameworks. It only depends on its own interfaces (ports).

---

## **IMPLEMENTATION BLUEPRINT**

### **3. Directory Structure**

Strictly adhere to this directory structure. All new files must be placed in the correct location.

- `/config/`: DI container setup, database connections, environment configuration.
- `/controller/`: Primary Adapters (e.g., API endpoints). They handle HTTP requests, call services, and manage DTOs.
- `/dto/`: Data Transfer Objects. Used for all data exchange between Controllers and Services.
- `/service/`: Application Core - Business Logic Interfaces (Primary Ports).
  - `/service/impl/`: Concrete implementations of the service interfaces.
- `/repository/`: Secondary Ports for data persistence (e.g., `UserRepositoryInterface`).
  - `/repository/impl/`: Secondary Adapters implementing data persistence (e.g., using SQLAlchemy).
- `/adapter/`: Secondary Ports for external service integrations (e.g., payment gateways, messaging APIs).
  - `/adapter/impl/`: Secondary Adapters implementing external service integrations.
- `/domain/`: The absolute core of the application. Contains no framework-specific code.
  - `/domain/model/`: Pydantic models for data validation and business rules.
  - `/domain/orm/`: ORM models (e.g., SQLAlchemy). These are persistence details and must NOT leak into the service layer.
  - `/domain/enum/`: Application-wide enumerations.
  - `/domain/error/`: Custom exception classes.
  - `/domain/prompt/`: AI-related prompt templates or structures.
- `/factory/`: Factory classes/methods for complex object creation.
- `/decorators/`: Custom decorators (e.g., for task queues, logging, auth).
- `/callback/`: Handlers for asynchronous operations or AI events (e.g., token counting).
- `/template/`: General-purpose templates (e.g., agent execution templates).

### **4. Execution & Methodology Rules**

1.  **Strict Interface Adherence:** Every class in an `impl` directory (e.g., `service/impl/`, `repository/impl/`) MUST implement a corresponding interface defined in its parent directory.
2.  **DTOs are Mandatory:** All data entering or leaving a `Controller` MUST be a DTO from the `/dto/` directory.
3.  **Model Separation & Validation:**
    - Every ORM model in `/domain/orm/` must have a corresponding Pydantic model in `/domain/model/`.
    - The `Service` layer receives DTOs from the controller. Input validation via `PydanticModel.model_validate(dto.dict())` occurs immediately at the beginning of the service method.
    - The `Repository` layer is responsible for mapping between Domain/Pydantic models and ORM models. The Service layer MUST NEVER receive ORM models.
4.  **Strict Constructor Dependency Injection (DI):**
    - Dependencies are NEVER instantiated inside a class. They are always passed in via the `__init__` constructor.
    - **Dependency Flow:** `Controllers` are initialized with `Services`. `Services` are initialized with `Repositories`, `Adapters`, and `Factories`.
    - All object instantiation and dependency wiring occurs exclusively in a dedicated DI container within the `/config/` directory.
5.  **Unit of Work (UoW) Pattern:** For services related to "Agent Autonomy," you must use the Unit of Work pattern to ensure transactional integrity, especially for compatibility with task queues like `taskiq`.

### **5. Python Best Practices**

- **Exception Handling:** Always use `except Exception as error:` for catching generic exceptions. Never use `e` or other single-letter variables. Only use `logging.exception()` within an `except` block to automatically include traceback information.
- **Type Checking:** Use `isinstance()` for type checking. Avoid non-Pythonic patterns.
- **Type Annotations:** Use `X | Y` for type annotations
- **None:** When specifying | None, set variable to None as default value.

---

## **SOFTWARE TESTING METHODOLOGY**

When tasked with writing tests, you must follow this exact workflow and set of principles.

### **1. Testing Workflow: Document First, Code Second**

Before writing any test code, you MUST first produce technical documentation that outlines the complete test plan. This plan must:

1.  **Identify all Test Categories:** Systematically list all partitions and boundaries.
    - Input Partitions
    - Output Partitions
    - Input Combination Partitions
    - Boundary Analysis (including on-point and off-point values for each boundary)
2.  **Define Test Cases:** For each identified partition and boundary, define the specific test cases.
3.  **Ensure Completeness:** The plan must be exhaustive, covering all identified cases while removing any duplicate or redundant tests.

### **2. Test Design Techniques**

Your tests will be designed using a combination of specification-based and structural methods.

- **Specification-Based (Black-Box) Tests:** This is your primary approach. You will derive tests from the requirements, focusing on:
  - **Partitioning:** Divide inputs, outputs, and their combinations into equivalence classes to test representatives from each class.
  - **Boundary Value Analysis (BVA):** For any ordered data (numbers, dates, lists), define tests for the exact boundaries, and for values immediately inside and outside the boundaries (on-point and off-point).
- **Structural (White-Box) Tests:** As a secondary goal, design tests to maximize code coverage, specifically focusing on **branch coverage** to ensure every decision point in the code is executed.

### **3. Test Implementation Rules**

1.  **Mandatory Test ID Format:** Every single test function or parameterized test case must have a unique, structured name that acts as a test ID. The format is `[TYPE].[NUMBER].[TEST_NAME]`.
    - **IP.#.test_name:** For Input Partition tests.
    - **OP.#.test_name:** For Output Partition tests.
    - **IPC.#.test_name:** For Input Combination Partition tests.
    - **BA.#.test_name:** For Boundary Analysis tests.
2.  **Logical Grouping:** Tests MUST be logically grouped within the test files according to the partition or boundary they are testing. This is a critical requirement for maintainability.
3.  **Use Parameterized Tests:** When multiple tests check the same logic with different data (e.g., testing multiple boundary values), you MUST use parameterized testing (e.g., `pytest.mark.parametrize`) to avoid code duplication.
