# Commands

| Task       | Command         |
| ---------- | --------------- |
| Install    | `npm install`   |
| Dev Server | `npm run dev`   |
| Build      | `npm run build` |
| Lint       | `next lint`     |

---

# Architecture

This project uses a **front-end adaptation of Hexagonal Architecture**. The core idea is the same as the backend version: **business logic never knows about the outside world.** Components don't talk to APIs. APIs don't bleed into components. Everything communicates through defined interfaces.

There are three layers:

## Layer 1 — Presentation (UI)

> Components + what the user sees and interacts with

```
User clicks something
  → Component           (captures the event, renders UI)
  → Custom Hook         (handles all the logic)
```

Components are "dumb." They only render what they're given and call functions they're given. No logic lives here.

## Layer 2 — Application Core (Logic)

> Hooks + Zustand stores — this is where the real work happens

```
Custom Hook
  → Zustand Store       (manages shared state)
  → Adapter (if external data is needed)
```

Hooks orchestrate everything. They call store actions to update state and call adapters to fetch data.

## Layer 3 — Infrastructure (External)

> Adapters — anything that talks to the outside world

```
Hook calls an Adapter Interface (port)
  → Adapter Implementation    (does the actual fetch/axios call)
  → External API
```

Adapters handle fetching, transforming, and validating raw API data. They return clean, typed data back to the hook.

## The One Rule That Matters Most

> **Dependencies always point inward.** Components depend on hooks. Hooks depend on stores and adapter interfaces. The core (hooks, stores, schemas) never imports from components or specific adapter implementations.

---

# Folder Structure

```
/app/                     # Next.js pages and layouts (routing only)
/components/
  /ui/                    # Primitive components: Button, Input, Card (Shadcn, etc.)
  /feature/               # Composed components for a specific feature
/lib/  (or /core/)
  /adapters/              # Fetch logic — implements adapter interfaces, validates responses
  /hooks/                 # All business logic — orchestrate state + adapter calls
  /store/                 # Zustand stores for shared state
  /schemas/               # Zod schemas — validate API responses and form inputs
  /types/                 # TypeScript interfaces, including adapter port definitions
  /config/                # Env variables, constants
  /utils/                 # Pure helper functions (formatting, string utils, etc.)
/styles/                  # Global CSS
/public/                  # Static assets
```

---

# Rules to Follow

## 1. Components are for rendering only

No API calls, no business logic, no direct store access inside a component. If a component needs data or needs to trigger something, it uses a hook.

```tsx
// ✅ Component delegates everything to a hook
function UserProfile() {
  const { user, isLoading, handleSave } = useUserProfile();
  return <div>...</div>;
}

// ❌ Component calls an adapter directly
function UserProfile() {
  const user = await userAdapter.getUser(); // never do this
}
```

## 2. All external data must be validated with Zod

Every API response that comes through an adapter must be parsed through a Zod schema from `/schemas`. Same goes for form inputs.

```ts
// /schemas/user.schema.ts
export const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

export type User = z.infer<typeof UserSchema>; // free TypeScript type from your schema
```

## 3. Adapters return typed data — hooks consume it

The adapter's job is: fetch → validate with Zod → return typed result. The hook's job is to call the adapter and update state. The component never calls an adapter.

```
Component → Hook → Adapter Interface → Adapter Impl → API
```

## 4. State management rules

- **Zustand** — for state shared across multiple components
- **useState / useReducer** — for state that's local to one component
- **React Context** — only for static/rarely-changing values like theme or auth status

## 5. Dependency injection via hooks

Components get everything through hooks. This keeps components reusable and easy to test.

**Dependency flow:** `Component → Hook → Store + Adapter`

---

# TypeScript & React Style

```ts
// Exception handling — always check the type before using .message
try {
  ...
} catch (error) {
  if (error instanceof Error) {
    console.error(error.message)
  }
}

// Generate types from Zod schemas instead of writing them twice
export type User = z.infer<typeof UserSchema>

// Performance — use these when passing functions/values to child components
const handleClick = useCallback(() => { ... }, [dependency])
const expensiveValue = useMemo(() => compute(), [dependency])
const MemoizedComponent = React.memo(MyComponent)
// Don't use these everywhere — only when you actually have a re-render problem
```

---

# Writing Tests

**Stack:** Jest + React Testing Library for unit/integration, Playwright for E2E.

## Step 1: Write the plan first, code second

Before any test code, document your test plan covering:

- **Input Partitions** — categories of valid/invalid user inputs (e.g. valid email, empty email, too-long email)
- **State Partitions** — UI states to cover (e.g. loading, success, error)
- **Boundary Analysis** — exact edges (e.g. min/max character length for a field)

## Step 2: What to test and how

| Test Type   | Tool                  | Target                                   | How                                              |
| ----------- | --------------------- | ---------------------------------------- | ------------------------------------------------ |
| Unit        | Jest                  | Adapters, Hooks, Stores, utils           | Mock all external deps (fetch, adapters)         |
| Integration | React Testing Library | Components wired to their hooks          | Render, simulate interactions, assert UI updates |
| E2E         | Playwright            | Critical user flows (login, checkout...) | Real browser, full journey, no mocks             |

## Step 3: Implementation rules

**Every test must follow this naming format:**

```
UNIT.Hook.should_return_error_when_api_fails
INT.LoginForm.should_display_error_on_invalid_email
E2E.Auth.should_allow_user_to_log_in
```

**Structure every test with AAA:**

```ts
it("UNIT.UserAdapter.should_parse_valid_response", () => {
  // Arrange — set up mock data
  const mockResponse = { id: "1", name: "Lucy", email: "lucy@test.com" };

  // Act — run the thing you're testing
  const result = UserSchema.safeParse(mockResponse);

  // Assert — verify the outcome
  expect(result.success).toBe(true);
});
```

**Use `data-testid` to select elements in tests** — don't rely on CSS classes or tag names, those change:

```tsx
<button data-testid="submit-btn">Submit</button>;

// in your test:
screen.getByTestId("submit-btn");
```
