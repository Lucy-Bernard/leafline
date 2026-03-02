# Plant ID - Project Summary

## Project Overview

**Plant ID** is an AI-powered plant identification and diagnostic application featuring an innovative **Diagnostic Kernel** - an autonomous AI agent that dynamically generates and executes Python code to diagnose plant health issues through interactive conversations.

### Core Innovation: The Diagnostic Kernel

Unlike traditional chatbots, the Diagnostic Kernel uses a revolutionary cyclical execution model:

1. AI analyzes the current diagnosis context (plant data, conversation history, internal state)
2. AI generates executable Python code that determines the next logical step
3. Code executes safely in a RestrictedPython sandbox
4. Actions update state and may trigger more cycles
5. Process continues until AI decides to ask user a question or provide final diagnosis

This creates a truly autonomous diagnostic agent that can gather information, form hypotheses, and make decisions - all driven by AI-generated code.

---

## Technology Stack

### Backend (Python FastAPI)

- **Framework**: FastAPI 0.116.2+
- **Language**: Python 3.13
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Authentication**: Supabase Auth with JWT
- **AI/ML Services**:
  - **OpenRouter/Together.ai**: LLM for diagnostic kernel and chat
  - **Plant.id API**: Plant identification from images
- **Code Execution**: RestrictedPython 7.0+ (secure sandbox)
- **Package Management**: uv (modern Python package manager)
- **Code Quality**: Ruff (linting & formatting)
- **Deployment**: Heroku

### Frontend (Next.js)

- **Framework**: Next.js (latest, with Turbopack)
- **Language**: TypeScript 5
- **UI Library**: React 19
- **Component Library**: Radix UI + ShadCN UI
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand 5.0
- **Validation**: Zod 4.1
- **Authentication**: Supabase SSR
- **Deployment**: Heroku

---

## Architecture

Both backend and frontend follow **Hexagonal Architecture** (Ports & Adapters) with strict separation of concerns and dependency inversion.

### Backend Architecture

#### Core Principles

- **Dependency Inversion**: All dependencies point inward toward the application core
- **Application core has ZERO knowledge of external technologies** (databases, APIs, HTTP)
- **Interfaces (ports) define contracts between layers**
- **Implementations (adapters) are injected via constructors**

#### Directory Structure

```
api/
├── main.py                    # FastAPI entry point
├── config/                    # DI container, database, CORS
│   ├── container.py          # Dependency injection wiring
│   ├── database.py           # SQLAlchemy async session
│   └── cors.py               # CORS configuration
├── controller/                # PRIMARY ADAPTERS (HTTP endpoints)
│   ├── plant_controller.py
│   ├── chat_controller.py
│   └── diagnosis_controller.py
├── dto/                       # Data Transfer Objects
│   ├── plant_creation_dto.py
│   ├── diagnosis_start_dto.py
│   └── diagnosis_update_dto.py
├── service/                   # PRIMARY PORTS (business logic interfaces)
│   ├── plant_service.py
│   ├── chat_service.py
│   ├── diagnosis_service.py
│   └── impl/                 # Application core implementations
│       ├── plant_service.py
│       ├── chat_service_impl.py
│       └── diagnosis_service_impl.py
├── repository/                # SECONDARY PORTS (data persistence interfaces)
│   ├── plant_repository.py
│   ├── chat_repository.py
│   ├── diagnosis_repository.py
│   └── impl/                 # Secondary adapters (SQLAlchemy)
│       ├── plant_repository_impl.py
│       ├── chat_repository_impl.py
│       └── diagnosis_repository_impl.py
├── adapter/                   # SECONDARY PORTS (external service interfaces)
│   ├── ai_adapter.py         # LLM interface
│   ├── plant_id_adapter.py   # Plant identification interface
│   ├── sandbox_executor.py   # Code execution interface
│   ├── storage_adapter.py    # File storage interface
│   └── impl/                 # Secondary adapters (concrete implementations)
│       ├── openrouter_adapter.py
│       ├── plant_id_adapter_impl.py
│       ├── sandbox_executor_impl.py
│       └── supabase_storage_adapter.py
├── domain/                    # THE CORE (framework-agnostic)
│   ├── model/                # Pydantic models (business entities)
│   │   ├── plant.py
│   │   ├── diagnosis_session.py
│   │   ├── chat_message.py
│   │   └── care_schedule.py
│   ├── orm/                  # SQLAlchemy ORM models (persistence detail)
│   │   ├── plant_orm.py
│   │   ├── diagnosis_session_orm.py
│   │   └── chat_message_orm.py
│   ├── enum/                 # Application enumerations
│   │   ├── diagnosis_status.py
│   │   ├── message_role.py
│   │   └── prompt_type.py
│   ├── error/                # Custom exceptions
│   │   └── errors.py
│   └── prompt/               # AI system prompts
│       ├── diagnosis_kernel_prompt.txt
│       ├── general_plant_discussion_prompt.txt
│       └── plant_care_prompt.txt
├── factory/                   # Factory patterns for complex object creation
│   └── care_schedule_factory.py
└── middleware/                # Request/response interceptors
    └── auth_middleware.py    # JWT validation
```

#### Architectural Flow

**Primary Side (External → Core):**

```
HTTP Request → Controller (Primary Adapter)
           → Service Interface (Primary Port)
           → Service Implementation (Application Core)
```

**Secondary Side (Core → External):**

```
Service Implementation → Repository/Adapter Interface (Secondary Port)
                     → Repository/Adapter Implementation (Secondary Adapter)
                     → External System (Database, API)
```

**Key Rules:**

1. **DTOs are mandatory** for all controller input/output
2. **Services receive DTOs**, validate with Pydantic models
3. **Repositories handle ORM ↔ Domain model conversion**
4. **Services NEVER see ORM models**
5. **All dependencies injected via constructors**
6. **DI container (`config/container.py`) wires everything together**

### Frontend Architecture

#### Core Principles

- **Separation of Concerns**: UI, business logic, and external services are completely decoupled
- **Components are "dumb"**: Only render UI based on props
- **Hooks orchestrate logic**: Custom hooks contain all business logic
- **Adapters handle external communication**: API calls isolated in adapter layer
- **Zod schemas validate all data**: Type safety at runtime

#### Directory Structure

```
ui/
├── app/                       # Next.js App Router
│   ├── page.tsx              # Landing page
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles
│   ├── auth/                 # Authentication pages
│   ├── dashboard/            # Main dashboard
│   └── plants/               # Plant management pages
│       ├── [id]/            # Dynamic plant detail routes
│       └── diagnoses/       # Diagnosis routes
├── components/                # React components (UI only)
│   ├── ui/                   # Primitive components (Button, Input, Card)
│   ├── feature/              # Composite feature components
│   │   ├── plant-card.tsx
│   │   ├── diagnosis-chat.tsx
│   │   └── care-schedule-display.tsx
│   ├── ai-elements/          # AI-specific UI components
│   ├── auth-button.tsx
│   ├── login-form.tsx
│   └── theme-switcher.tsx
├── lib/                       # Application Core (UI-agnostic)
│   ├── adapters/             # SECONDARY ADAPTERS (external APIs)
│   │   ├── plant-api.adapter.ts
│   │   ├── diagnosis-api.adapter.ts
│   │   ├── chat-api.adapter.ts
│   │   └── supabase-auth.adapter.ts
│   ├── hooks/                # PRIMARY PORTS (business logic orchestration)
│   │   ├── use-plants.ts
│   │   ├── use-plant-details.ts
│   │   ├── use-active-diagnosis.ts
│   │   ├── use-diagnoses.ts
│   │   ├── use-active-chat.ts
│   │   ├── use-chats.ts
│   │   └── use-auth.ts
│   ├── store/                # State management (Zustand)
│   │   └── plant.store.ts
│   ├── schemas/              # Zod validation schemas (domain models)
│   │   ├── plant.schema.ts
│   │   ├── diagnosis.schema.ts
│   │   ├── chat.schema.ts
│   │   └── auth.schema.ts
│   ├── types/                # TypeScript interfaces & adapter ports
│   │   ├── plant.types.ts
│   │   ├── diagnosis.types.ts
│   │   └── chat.types.ts
│   ├── config/               # Configuration (API endpoints, constants)
│   │   └── api.config.ts
│   ├── supabase/             # Supabase client utilities
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── middleware.ts
│   └── utils.ts              # Pure utility functions
├── middleware.ts              # Next.js middleware (auth)
└── public/                    # Static assets
```

#### Architectural Flow

**Presentation → Application → Infrastructure:**

```
User Interaction → Component → Custom Hook (Primary Port)
                             → Zustand Store Action
                             → Adapter Interface (Secondary Port)
                             → Adapter Implementation
                             → External API
```

**Key Rules:**

1. **Components never call adapters directly** - always through hooks
2. **All API responses validated with Zod schemas**
3. **Hooks manage state via Zustand stores**
4. **Adapters implement interfaces defined in types**
5. **Type safety via `z.infer<typeof Schema>`**

---

## Core Features & Execution Flows

### 1. Plant Identification & Creation

**User Flow:**

1. User uploads plant image
2. Image sent to Plant.id API for identification
3. AI generates care schedule using LLM
4. Plant entity created in database
5. User can view/manage plant in dashboard

**Backend Execution:**

```
POST /api/v1/plants
→ plant_controller.create_plant()
  → Validates DTO
  → Extracts user_id from JWT
  → plant_service.create_plant()
    → plant_id_adapter.identify_plant(image)
    → ai_adapter.get_completion(plant_care_prompt)
    → care_schedule_factory.parse_ai_response()
    → plant_repository.create(plant)
      → Maps Plant → PlantORM
      → Saves to PostgreSQL
    → Returns Plant domain model
  → Returns HTTP 201 with plant data
```

**Security:**

- JWT validation in auth_middleware
- User-scoped queries (can only access own plants)
- Image upload to Supabase Storage

### 2. General Plant Chat

**User Flow:**

1. User starts chat about plant care
2. AI responds with plant knowledge
3. Conversation history persisted
4. User can have multiple chat sessions

**Backend Execution:**

```
POST /api/v1/chats/start
→ chat_controller.start_chat()
  → chat_service.start_chat()
    → Creates ChatMessage with user prompt
    → ai_adapter.get_completion(general_plant_prompt)
    → Creates ChatMessage with AI response
    → chat_repository.save_messages()
    → Returns conversation
```

**Key Difference from Diagnosis:**

- Simple request-response chat
- No code generation or execution
- Stateless AI responses

### 3. The Diagnostic Kernel (★ Core Innovation)

**The Revolutionary Feature:** An autonomous AI agent that generates and executes Python code to dynamically diagnose plant issues.

#### How It Works

**User Flow:**

1. User reports plant problem: "My plant has brown spots"
2. AI enters cyclical diagnostic process:
   - **Cycle 1**: AI generates code to fetch plant data → executes → continues
   - **Cycle 2**: AI generates code to log hypothesis → executes → continues
   - **Cycle 3**: AI generates code to ask question → executes → pauses for user
3. User answers: "They get 6 hours of direct sun"
4. AI continues cycles:
   - **Cycle 4**: AI generates code to update confidence → executes → continues
   - **Cycle 5**: AI generates code to conclude diagnosis → executes → ends
5. User receives diagnosis: "Sun Scorch - Move to indirect light"

#### The Kernel Cycle (Heart of the System)

```python
async def _run_kernel_cycle(session: DiagnosisSession):
    """
    THE DIAGNOSTIC KERNEL - Cyclical AI-driven process

    Loop until AI decides to ask user or conclude:
    1. Build prompt with full context (plant data, history, AI state)
    2. AI generates Python code determining next step
    3. Execute code in RestrictedPython sandbox
    4. Extract action from code result
    5. Dispatch action:
       - GET_PLANT_VITALS → fetch data, continue loop
       - LOG_STATE → save hypothesis, continue loop
       - ASK_USER → return question, exit loop (pause)
       - CONCLUDE → return diagnosis, exit loop (end)
    """
    max_iterations = 20
    iterations = 0

    while iterations < max_iterations:
        # 1. Build prompt with diagnosis_context
        llm_prompt = self._build_kernel_prompt(session.diagnosis_context)

        # 2. AI generates executable Python code
        code = self._ai_adapter.get_completion(
            system_prompt=self._get_kernel_system_prompt(),
            user_prompt=llm_prompt
        )

        # 3. Execute code in sandbox
        result = await self._sandbox_executor.execute_code(
            code=code,
            params={"diagnosis_context": session.diagnosis_context}
        )

        # 4. Extract action
        action = result.get("action")
        payload = result.get("payload")

        # 5. Dispatch action
        if action == "GET_PLANT_VITALS":
            # Fetch plant data, update context, continue loop
            plant = await self._plant_repository.get_by_id(...)
            session.diagnosis_context["plant_vitals"] = plant.to_dict()
            continue

        elif action == "LOG_STATE":
            # Save AI hypothesis, update context, continue loop
            session.diagnosis_context["state"].update(payload)
            continue

        elif action == "ASK_USER":
            # Return question to user, exit loop
            session.diagnosis_context["conversation_history"].append({
                "role": "assistant",
                "message": payload["question"]
            })
            return DiagnosisAskResponse(ai_question=payload["question"])

        elif action == "CONCLUDE":
            # Return final diagnosis, exit loop
            session.diagnosis_context["result"] = payload
            return DiagnosisConcludeResponse(result=payload)
```

#### AI-Generated Code Examples

**Example 1: First Cycle - Get Plant Data**

```python
diagnosis_context = params["diagnosis_context"]

if diagnosis_context.get("plant_vitals") is None:
    result = {"action": "GET_PLANT_VITALS", "payload": {}}
else:
    result = {"action": "ASK_USER", "payload": {"question": "How much sun?"}}
```

**Example 2: Hypothesis Formation**

```python
diagnosis_context = params["diagnosis_context"]
conversation = diagnosis_context.get("conversation_history", [])

# User mentioned brown spots on leaves getting sun
result = {
    "action": "LOG_STATE",
    "payload": {
        "hypothesis": "sun_scorch",
        "confidence": 0.7,
        "evidence": ["brown_spots", "direct_sun_exposure"]
    }
}
```

**Example 3: Ask Follow-up Question**

```python
diagnosis_context = params["diagnosis_context"]
state = diagnosis_context.get("state", {})

if state.get("hypothesis") == "sun_scorch":
    result = {
        "action": "ASK_USER",
        "payload": {
            "question": "Are the brown spots crispy or soft and mushy?"
        }
    }
```

**Example 4: Final Conclusion**

```python
diagnosis_context = params["diagnosis_context"]
state = diagnosis_context.get("state", {})

if state.get("confidence", 0) > 0.8:
    result = {
        "action": "CONCLUDE",
        "payload": {
            "finding": "Sun Scorch",
            "recommendation": "Move plant to bright, indirect light. Water only when top 2 inches of soil are dry."
        }
    }
```

#### The diagnosis_context (JSONB stored in PostgreSQL)

```json
{
  "initial_prompt": "My plant has brown spots on leaves",
  "conversation_history": [
    { "role": "user", "message": "My plant has brown spots on leaves" },
    { "role": "assistant", "message": "How many hours of direct sun?" },
    { "role": "user", "message": "About 6 hours" },
    { "role": "assistant", "message": "Are the spots crispy or mushy?" },
    { "role": "user", "message": "Crispy and dry" }
  ],
  "state": {
    "hypothesis": "sun_scorch",
    "confidence": 0.85,
    "evidence": ["brown_spots", "direct_sun", "crispy_texture"],
    "ruled_out": ["overwatering", "fungal_infection"]
  },
  "plant_vitals": {
    "name": "Monstera Deliciosa",
    "care_schedule": {
      "watering": "Every 1-2 weeks",
      "light": "Bright, indirect light",
      "humidity": "60-80%"
    }
  },
  "result": {
    "finding": "Sun Scorch",
    "recommendation": "Move to bright, indirect light. Water when top 2\" soil dry."
  }
}
```

#### Security: The Sandbox Executor

**Critical Security Component** - AI-generated code could be malicious or buggy.

**RestrictedPython Sandbox Implementation:**

```python
class SandboxExecutorImpl:
    """
    Executes AI-generated code in heavily restricted environment.

    Security Model:
    - NO file system access (no 'open', no 'os' module)
    - NO network access (no HTTP requests, sockets)
    - NO imports (except whitelisted 'json')
    - NO dangerous builtins (eval, exec, __import__, compile)
    - LIMITED scope (can only access params dict)

    What code CAN do:
    - Basic Python: if/else, loops, variables, functions
    - Math operations: +, -, *, /, etc.
    - Dictionary/list operations
    - Access diagnosis_context from params
    - Set 'result' variable
    """

    def _create_safe_builtins(self) -> dict[str, Any]:
        """
        Whitelist approach: Only allow explicitly safe operations.
        Anything not in this dict is completely unavailable.
        """
        safe_builtins = safe_globals.copy()
        safe_builtins["json"] = json  # Only allowed module
        safe_builtins["len"] = len
        safe_builtins["str"] = str
        safe_builtins["int"] = int
        safe_builtins["dict"] = dict
        safe_builtins["list"] = list
        # ... only safe built-ins
        # Explicitly BLOCKED: open, __import__, eval, exec, os, sys, subprocess
        return safe_builtins

    async def execute_code(self, code: str, params: dict) -> dict:
        """
        Execute AI code with security layers:
        1. Validate syntax with Python AST parser
        2. Compile with RestrictedPython (blocks dangerous operations)
        3. Execute in isolated environment with only safe builtins
        4. Extract and return 'result' variable
        """
        # Syntax validation
        ast.parse(code)

        # RestrictedPython compilation
        compiled_code = compile_restricted(code, filename="<user_code>", mode="exec")

        # Isolated execution environment
        exec_globals = {
            "__builtins__": self._safe_builtins,
            "params": params
        }
        exec_locals = {}

        # Execute code
        exec(compiled_code, exec_globals, exec_locals)

        # Extract result
        return exec_locals["result"]
```

**Why This Is Secure:**

- **Compile-time security**: RestrictedPython blocks dangerous operations during compilation
- **Runtime security**: Only whitelisted functions available
- **Memory isolation**: Code can't access server memory, just the params dict
- **No side effects**: Code can't modify files, make network calls, or execute shell commands

#### Frontend Integration

**useActiveDiagnosis Hook:**

```typescript
export function useActiveDiagnosis(
  adapter: IDiagnosisAdapter,
  plantId: string,
) {
  const [messages, setMessages] = useState<DiagnosisMessage[]>([]);
  const [status, setStatus] = useState<DiagnosisStatus>("idle");
  const [result, setResult] = useState<DiagnosisResult | null>(null);

  const startDiagnosis = async (prompt: string) => {
    // Send initial problem to backend
    const response = await adapter.startDiagnosis(plantId, prompt);

    if (response.status === "COMPLETED") {
      // AI concluded immediately
      setResult(response.result);
    } else {
      // AI asked question - wait for user input
      setMessages([
        { role: "user", message: prompt },
        { role: "assistant", message: response.ai_question },
      ]);
      setStatus("pending_input");
    }
  };

  const sendMessage = async (message: string) => {
    // Continue diagnosis with user's answer
    const response = await adapter.continueDiagnosis(diagnosisId, message);

    if (response.status === "COMPLETED") {
      setResult(response.result);
    } else {
      setMessages((prev) => [
        ...prev,
        { role: "user", message },
        { role: "assistant", message: response.ai_question },
      ]);
    }
  };

  return { messages, status, result, startDiagnosis, sendMessage };
}
```

---

## Data Models

### Domain Models (Pydantic)

**Plant:**

```python
class Plant:
    id: str
    user_id: str
    name: str
    species: str | None
    care_schedule: CareSchedule
    image_url: str | None
    created_at: datetime
    updated_at: datetime
```

**CareSchedule:**

```python
class CareSchedule:
    watering_schedule: str
    light_requirements: str
    temperature_range: str
    humidity_level: str
    fertilizing_schedule: str
    soil_type: str
    common_issues: str
```

**DiagnosisSession:**

```python
class DiagnosisSession:
    id: str
    plant_id: str
    status: DiagnosisStatus  # PENDING_USER_INPUT, COMPLETED, CANCELLED
    diagnosis_context: dict[str, Any]  # JSONB - contains everything
    created_at: datetime
    updated_at: datetime
```

**ChatMessage:**

```python
class ChatMessage:
    id: str
    general_chat_id: str
    role: MessageRole  # USER, ASSISTANT
    content: str
    created_at: datetime
```

### Database Schema (PostgreSQL via Supabase)

**plants table:**

- id (uuid, primary key)
- user_id (uuid, foreign key to auth.users)
- name (text)
- species (text, nullable)
- care_schedule (jsonb)
- image_url (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)

**diagnosis_sessions table:**

- id (uuid, primary key)
- plant_id (uuid, foreign key to plants)
- status (text)
- diagnosis_context (jsonb) ← **Stores entire conversation & AI state**
- created_at (timestamp)
- updated_at (timestamp)

**general_chats table:**

- id (uuid, primary key)
- user_id (uuid, foreign key to auth.users)
- title (text)
- created_at (timestamp)
- updated_at (timestamp)

**chat_messages table:**

- id (uuid, primary key)
- general_chat_id (uuid, foreign key to general_chats)
- role (text)
- content (text)
- created_at (timestamp)

---

## API Endpoints

### Authentication

All endpoints require JWT Bearer token in `Authorization` header.

### Plants

- `POST /api/v1/plants` - Create plant from image
- `GET /api/v1/plants` - List user's plants
- `GET /api/v1/plants/{id}` - Get plant details
- `DELETE /api/v1/plants/{id}` - Delete plant

### Diagnosis

- `POST /api/v1/diagnoses/{plant_id}/start` - Start diagnosis
  - Body: `{"prompt": "My plant has brown spots"}`
  - Returns: `{"diagnosis_id": "...", "status": "...", "ai_question": "..."}`
- `POST /api/v1/diagnoses/{id}/continue` - Continue diagnosis
  - Body: `{"message": "About 6 hours of sun"}`
  - Returns: `{"status": "...", "ai_question": "..."}` or `{"status": "COMPLETED", "result": {...}}`
- `GET /api/v1/diagnoses/{id}` - Get diagnosis session
- `DELETE /api/v1/diagnoses/{id}` - Delete diagnosis
- `GET /api/v1/plants/{plant_id}/diagnoses` - List plant's diagnoses

### Chat

- `POST /api/v1/chats/start` - Start general chat
- `POST /api/v1/chats/{id}/continue` - Continue chat
- `GET /api/v1/chats/{id}` - Get chat history
- `GET /api/v1/chats` - List user's chats
- `DELETE /api/v1/chats/{id}` - Delete chat

---

## Testing Methodology

### Backend Testing (Python)

**Philosophy: Document First, Code Second**

Before writing tests, create a technical document outlining:

1. **Test Categories**: Input/Output partitions, boundary analysis
2. **Test Cases**: Specific tests for each partition
3. **Completeness**: Exhaustive coverage without redundancy

**Test Design Techniques:**

- **Specification-Based (Primary)**: Black-box testing from requirements
  - Partitioning: Equivalence classes for inputs/outputs
  - Boundary Value Analysis: On-point and off-point values
- **Structural (Secondary)**: White-box testing for branch coverage

**Test Implementation Rules:**

1. **Mandatory Test ID Format**: `[TYPE].[NUMBER].[TEST_NAME]`
   - `IP.1.test_valid_plant_name` (Input Partition)
   - `OP.2.test_returns_care_schedule` (Output Partition)
   - `IPC.3.test_empty_string_and_none` (Input Combination)
   - `BA.4.test_min_length_boundary` (Boundary Analysis)

2. **Logical Grouping**: Group tests by partition/boundary
3. **Parameterized Tests**: Use `pytest.mark.parametrize` for similar tests

**Example Test Structure:**

```python
# IP.1: Valid plant names should create plant successfully
@pytest.mark.parametrize("plant_name", [
    "Monstera Deliciosa",
    "Snake Plant",
    "Fiddle Leaf Fig"
])
async def test_IP_1_valid_plant_names(plant_name):
    # Arrange
    dto = PlantCreationDTO(plant_name=plant_name)

    # Act
    plant = await plant_service.create_plant(dto, user_id)

    # Assert
    assert plant.name == plant_name
    assert plant.care_schedule is not None
```

### Frontend Testing (TypeScript)

**Test Types:**

1. **Unit Tests (Jest)**: Test hooks, adapters, utils in isolation
2. **Integration Tests (React Testing Library)**: Test components with hooks
3. **E2E Tests (Playwright)**: Test critical user flows

**Test Implementation Rules:**

1. **Test ID Format**: `[TYPE].[CATEGORY].[TEST_NAME]`
   - `UNIT.Hook.should_calculate_correctly`
   - `INT.Form.should_display_error_on_invalid_email`
   - `E2E.Auth.should_allow_user_to_log_in`

2. **AAA Pattern**: Arrange, Act, Assert
3. **data-testid**: Use for element selection (decouples from implementation)

---

## Development Workflow

### Backend Setup

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd api
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run development server
uv run fastapi dev main.py

# Lint & format
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest path/to/test_file.py -v
```

### Frontend Setup

```bash
# Install dependencies
cd ui
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Environment Variables

**Backend (.env):**

```bash
ENVIRONMENT=local  # local, dev, prod
OPENROUTER_API_KEY=your_key
PLANT_ID_API_KEY=your_key
DATABASE_URL=your_supabase_db_url
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_key
SUPABASE_JWT_SECRET=your_secret
```

**Frontend (.env.local):**

```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Deployment

### Backend (Heroku)

- **Procfile**: `web: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- **Environment**: Set all variables in Heroku config
- **Database**: Supabase (external)

### Frontend (Heroku)

- **Procfile**: `web: npm run start`
- **Build**: `npm run build`
- **Port**: Dynamic via `$PORT` environment variable

---

## Key Design Decisions

### Why Hexagonal Architecture?

- **Testability**: Business logic testable without external dependencies
- **Flexibility**: Can swap technologies (e.g., switch from OpenRouter to OpenAI) without changing core
- **Maintainability**: Clear boundaries between layers
- **Domain-Centric**: Business rules are first-class citizens

### Why RestrictedPython for Code Execution?

- **Security**: Whitelist approach prevents dangerous operations
- **Dynamic Behavior**: Enables AI to dynamically control diagnosis flow
- **Sandboxing**: OS-level isolation without Docker overhead
- **Python-Native**: No need for separate runtime or language

### Why Diagnostic Kernel vs Simple Chat?

- **Autonomy**: AI actively directs conversation, not just responding
- **Stateful Logic**: AI maintains hypotheses and confidence across cycles
- **Dynamic Actions**: AI can fetch data, log state, ask questions, or conclude
- **Better Diagnosis**: Structured approach leads to higher quality diagnoses

### Why Zustand vs Redux?

- **Simplicity**: Less boilerplate, easier to understand
- **Performance**: No unnecessary re-renders
- **TypeScript**: Excellent TS support out of the box
- **Flexibility**: Can be used for global or local state

---

## Future Considerations

### Potential Rust Implementation of Sandbox

If implementing similar sandbox functionality in Rust (as discussed):

**Recommended Approach: Rhai Scripting Language**

- **Why**: Embedded scripting language, sandboxed by default, Rust-like syntax
- **Security**: No file I/O, network, or OS access (like RestrictedPython)
- **Performance**: Much faster than subprocess Python
- **Integration**: Drop-in replacement with similar security guarantees

**Alternative: WebAssembly Sandbox**

- Strongest isolation (OS-level)
- Can compile Python or Rust to WASM
- More complex setup

**Why NOT Execute Rust Dynamically**:

- Rust doesn't support dynamic code execution
- Use embedded scripting language instead
- Provides same sandboxing guarantees

---

## Critical Files for Understanding

### Backend

1. `api/service/impl/diagnosis_service_impl.py` - The Diagnostic Kernel implementation
2. `api/adapter/impl/sandbox_executor_impl.py` - RestrictedPython security
3. `api/domain/prompt/diagnosis_kernel_prompt.txt` - AI instructions
4. `api/config/container.py` - Dependency injection wiring
5. `api/main.py` - Application entry point

### Frontend

1. `ui/lib/hooks/use-active-diagnosis.ts` - Diagnosis UI orchestration
2. `ui/lib/adapters/diagnosis-api.adapter.ts` - Diagnosis API client
3. `ui/lib/schemas/diagnosis.schema.ts` - Zod validation
4. `ui/app/plants/[id]/diagnoses/page.tsx` - Diagnosis UI

---
