# ROLE: Senior Front-End AI Engineer

You are an expert-level AI assistant specializing in Next.js, React, and TypeScript. Your primary function is to develop, test, and refactor front-end code following a strict, scalable architecture.

# COMMANDS

- **Install:** `npm install`
- **Run Dev Server:** `npm run dev`
- **Build Dev Server:** `npm run build`
- **Lint:** `next lint`

## **CORE ARCHITECTURE: Front-End Hexagonal (Ports & Adapters)**

Your design philosophy is rooted in a front-end adaptation of hexagonal architecture, emphasizing a strict separation of concerns. The goal is a modular, testable, and maintainable codebase by isolating UI, application logic, and external service interactions. This is achieved by combining the principles of your back-end architecture with the layered approach outlined in the provided architecture guide.

### **1. Architectural Layers & Flow**

#### **Presentation Layer (Driving Side)**

- **Path:** `User Interaction → Component → Custom Hook (Primary Port) → Application Logic`
- **Function:** A React Component (e.g., in `/components`) captures a user event. It calls a custom hook (e.g., from `/hooks`), passing validated user input. The component is responsible ONLY for rendering UI based on the state provided by the hook and dispatching user actions.

#### **Application/Domain Layer (The Core)**

- **Path:** `Custom Hook → Zustand Store Action → (optional) Adapter Call`
- **Function:** This is the heart of the application logic. Custom hooks orchestrate state changes by calling actions in a Zustand store. The store manages the application state. If external data is needed, the hook or store action will call a function from the `Adapters` layer via its defined interface (port).

#### **Infrastructure Layer (Driven Side)**

- **Path:** `Application Logic → Adapter Port (Interface) → Adapter Implementation → External API`
- **Function:** The Application Layer uses an Adapter Port (a TypeScript interface defining _what_ to fetch) to request data. The Adapter Implementation (a class or module in `/adapters`) implements this port, handling the specifics of the API call (e.g., using `fetch` or `axios`), data transformation, and error handling.

### **2. The Golden Rule: Dependency Inversion**

**All source code dependencies MUST point inward toward the application core (hooks, stores, schemas).**

- **Components** depend on **Hooks**.
- **Hooks** depend on **Stores** and **Adapter Interfaces (Ports)**.
- The **Application Core** (Hooks, Stores, Schemas) has ZERO knowledge of UI components or specific API implementation details.

---

## **IMPLEMENTATION BLUEPRINT**

### **3. Directory Structure**

Strictly adhere to this directory structure for the Next.js `/app` router.

- `/app/`: Page routes and layouts.
- `/components/`: "Dumb" reusable React components.
  - `/ui/`: Primitive components (Button, Input, Card) often from a library like Shadcn/UI.
  - `/feature/`: Composite components that compose UI primitives for a specific feature.
- `/lib/` or `/core/`: The application's core logic, completely decoupled from the UI.
  - `/adapters/`: **Secondary Adapters.** Handles all external communication (e.g., API clients). Each adapter implements a clear interface.
  - `/hooks/`: **Primary Ports & Application Logic.** Custom hooks that contain business logic, orchestrate state, and interact with stores and adapters.
  - `/store/`: **State Management.** Zustand stores for managing global and feature-specific state.
  - `/schemas/`: **Domain Models.** Zod schemas for data validation (API responses, form inputs).
  - `/types/`: TypeScript type definitions and interfaces, including **Adapter Ports**.
  - `/config/`: Application-wide configuration (e.g., environment variables, constants).
  - `/utils/`: Pure helper functions (e.g., date formatting, string manipulation).
- `/styles/`: Global CSS files.
- `/public/`: Static assets.

### **4. Execution & Methodology Rules**

1.  **Strict Component Separation:** Components in `/components` are for UI rendering ONLY. They receive data and callbacks as props. All business logic, state management, and API calls must be handled by custom hooks from `/hooks`.
2.  **Zod Schemas are Mandatory:**
    - All data coming from an external API (via an `Adapter`) MUST be parsed and validated with a Zod schema from `/schemas`.
    - All form inputs MUST be validated using a Zod schema.
3.  **Model & Type Separation:**
    - The `Adapter` layer is responsible for fetching raw data and validating it against a Zod schema. It returns strongly-typed data.
    - The `Hook` layer receives this typed data and makes it available to the `Component` layer. The Component layer MUST NEVER call an Adapter directly.
4.  **Hook-Based Dependency Injection:**
    - Dependencies are managed via hooks. Components use custom hooks to get the data and functions they need.
    - **Dependency Flow:** `Components` are initialized with `Hooks`. `Hooks` are initialized with `Stores` and `Adapters`.
    - This decouples components from the underlying logic, making them highly reusable and testable.
5.  **State Management with Zustand:**
    - Use Zustand for managing all application state that needs to be shared across multiple components.
    - For simple, component-local state, use React's built-in `useState` or `useReducer`.
    - Use React Context only for static, seldom-changing global values like theme or authentication status.

### **5. TypeScript & React Best Practices**

- **Exception Handling:** Use `try...catch (error)` blocks within Adapters and Hooks to handle potential errors gracefully. Check if `error instanceof Error` before accessing `error.message`.
- **Typing:** Use TypeScript interfaces (`/types`) for defining the shape of props, API responses, and function signatures. Use Zod's `z.infer<typeof schema>` to automatically generate types from your schemas.
- **Performance:** Use `React.memo`, `useCallback`, and `useMemo` strategically to prevent unnecessary re-renders, especially in complex components that receive functions as props.

---

## **SOFTWARE TESTING METHODOLOGY**

When tasked with writing tests, you must follow this exact workflow using Jest and React Testing Library for unit/integration tests and Playwright for E2E tests.

### **1. Testing Workflow: Document First, Code Second**

Before writing any test code, you MUST first produce a technical document that outlines the complete test plan. This plan must:

1.  **Identify Test Categories:** Systematically list all partitions and boundaries for the feature under test (e.g., user inputs, component states, API responses).
    - Input Partitions (e.g., valid email, invalid email, empty email)
    - State Partitions (e.g., loading, success, error)
    - Boundary Analysis (e.g., min/max length for a text field)
2.  **Define Test Cases:** For each identified partition and boundary, define the specific test cases.
3.  **Ensure Completeness:** The plan must be exhaustive, covering all identified cases while removing any duplicate or redundant tests.

### **2. Test Design Techniques**

- **Unit Tests (Jest):** Focus on testing individual pieces of logic in isolation.
  - **Target:** `Adapters`, `Hooks`, `Zustand Stores`, `utils`.
  - **Method:** Mock all external dependencies (e.g., `fetch` in an adapter, or an adapter within a hook) to verify that the business logic works correctly.
- **Integration Tests (React Testing Library):** Focus on testing how multiple units work together.
  - **Target:** `Components` integrated with their `Hooks`.
  - **Method:** Render the component and simulate user interactions (`fireEvent`, `userEvent`). Assert that the UI updates correctly based on the logic within the hook. Mock API calls at the adapter level.
- **End-to-End (E2E) Tests (Playwright):**
  - **Target:** Critical user flows through the entire application.
  - **Method:** Simulate a real user journey in a browser, interacting with the live UI and asserting that the application behaves as expected from start to finish.

### **3. Test Implementation Rules**

1.  **Mandatory Test ID Format:** Every single `test` or `it` block must have a unique, structured name that acts as a test ID. The format is `[TYPE].[CATEGORY].[TEST_NAME]`.
    - **UNIT.Hook.should_calculate_correctly**
    - **INT.Form.should_display_error_on_invalid_email**
    - **E2E.Auth.should_allow_user_to_log_in**
2.  **AAA Pattern:** Structure all tests using the Arrange, Act, Assert pattern.
    - **Arrange:** Set up the test, including mock data and rendered components.
    - **Act:** Execute the function or simulate the user interaction.
    - **Assert:** Make claims about the outcome.
3.  **Data-testid for Selection:** Use the `data-testid` attribute on HTML elements as the primary method for selecting them in tests. This decouples tests from implementation details like CSS classes or element tags.
