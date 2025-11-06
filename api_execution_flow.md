# Plant Care API Execution Flow

```mermaid
graph TD
    A[Client Request] --> B[FastAPI App]
    B --> C[Authentication Middleware]
    C --> D{Token Valid?}
    D -->|No| E[HTTP 401 Unauthorized]
    D -->|Yes| F[Plant Controller]
    
    F --> G[Extract User ID from Token]
    G --> H[Plant Service]
    
    H --> I[Validate Plant Name]
    I --> J[Get System Prompt from Repository]
    J --> K[AI Adapter - Together.ai]
    K --> L[Generate Care Schedule via AI]
    L --> M[Care Schedule Factory]
    M --> N[Parse AI Response to CareSchedule]
    
    N --> O[Create Plant Domain Model]
    O --> P[Plant Repository]
    P --> Q[Convert to PlantORM]
    Q --> R[Database Session]
    R --> S[Save to Database]
    S --> T[Return Plant to Client]
    
    %% Error Handling
    I -->|Invalid| U[InvalidPlantNameError]
    K -->|Error| V[AI Service Error]
    M -->|Parse Error| W[JSON Parse Error]
    P -->|DB Error| X[Database Error]
    
    U --> Y[HTTP 400 Bad Request]
    V --> Z[HTTP 500 Internal Error]
    W --> Z
    X --> Z
    
    %% Dependencies
    subgraph "Dependency Injection Container"
        AA[Container]
        BB[Plant Service]
        CC[AI Adapter]
        DD[Plant Repository]
        EE[Prompt Repository]
        FF[Care Schedule Factory]
    end
    
    %% External Services
    subgraph "External Services"
        GG[Together.ai API]
        HH[Plant ID API]
        II[Supabase Auth]
    end
    
    %% Data Flow
    subgraph "Data Models"
        JJ[PlantCreationDTO]
        KK[Plant Domain Model]
        LL[CareSchedule]
        MM[PlantORM]
    end
    
    %% Connections
    B --> AA
    AA --> BB
    AA --> CC
    AA --> DD
    AA --> EE
    AA --> FF
    
    K --> GG
    C --> II
    
    F --> JJ
    H --> KK
    M --> LL
    P --> MM
```

## Key Components

### 1. **Entry Point** (`main.py`)
- FastAPI application initialization
- Dependency injection container setup
- Router registration

### 2. **Authentication** (`auth_middleware.py`)
- JWT token verification using Supabase
- User ID extraction from token
- Security validation

### 3. **Controller Layer** (`plant_controller.py`)
- HTTP endpoint handling
- Request/response mapping
- Error handling and HTTP status codes

### 4. **Service Layer** (`plant_service.py`)
- Business logic orchestration
- Plant name validation
- Care schedule generation coordination

### 5. **Adapters** (`ai_adapter.py`, `plant_id_adapter.py`)
- External service integration
- Together.ai for AI completions
- Plant ID API for plant identification

### 6. **Repository Layer** (`plant_repository_impl.py`)
- Data persistence
- Domain model to ORM conversion
- Database operations

### 7. **Factory** (`care_schedule_factory.py`)
- AI response parsing
- JSON to domain model conversion
- Error handling for malformed responses

### 8. **Domain Models**
- `Plant`: Core plant entity
- `CareSchedule`: Plant care instructions
- `PlantCreationDTO`: Request data transfer object

## Execution Flow Details

1. **Request Reception**: Client sends POST request to `/api/v1/plants/`
2. **Authentication**: JWT token validated against Supabase
3. **Controller Processing**: Request mapped to DTO and user ID extracted
4. **Service Orchestration**: Plant service coordinates the creation process
5. **AI Integration**: System prompt retrieved and sent to Together.ai
6. **Response Processing**: AI response parsed into CareSchedule object
7. **Persistence**: Plant entity saved to database via repository
8. **Response**: Created plant returned to client

## Error Handling

- **Authentication Errors**: 401 Unauthorized
- **Validation Errors**: 400 Bad Request  
- **Service Errors**: 500 Internal Server Error
- **Database Errors**: 500 Internal Server Error
