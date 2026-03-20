# LeafLine

An AI-powered plant identification and diagnostic application featuring an advanced, interactive diagnostic system.

## Tech Stack

**Frontend:**

- Next.js (React)
- TypeScript
- Tailwind CSS
- ShadCN UI Components

**Backend:**

- FastAPI (Python)
- Supabase (PostgreSQL + Auth)

**AI/ML:**

- Together.ai (LLM for diagnostic system)
- Plant.id (Plant identification)

## Getting Started

### Prerequisites

```bash
brew install node
```

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables (see `.env.local.example`)

3. Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Features

- **Plant Identification**: Upload photos to identify plants using AI
- **Diagnostic Kernel**: AI-driven diagnostic conversations with cyclical execution
- **Plant Care**: Track and manage your plant collection
- **Chat**: Have in-depth conversations about plant care

## Architecture

The frontend follows a hexagonal architecture pattern with strict separation of concerns:

- `/app` - Next.js routes and pages
- `/components` - React components
- `/lib` - Core application logic
  - `/adapters` - External API integrations
  - `/hooks` - Business logic and state orchestration
  - `/store` - Zustand state management
  - `/schemas` - Zod validation schemas
  - `/types` - TypeScript type definitions

## Deployment

The application is deployed on Heroku.
