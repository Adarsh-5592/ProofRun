# ProofRun Frontend

> Execute AI-generated code. Safely. Verify everything.

ProofRun is an AI-powered code generation and secure execution platform. This directory contains the React/TypeScript frontend.

## Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.7 | Type safety |
| Vite | 6 | Build tool and dev server |
| Tailwind CSS | 3.4 | Utility-first styling |
| React Router | 7 | Client-side routing |
| Axios | 1.7 | HTTP client |
| Lucide React | 0.469 | Icon library |
| react-syntax-highlighter | 15 | Python code highlighting |

## Folder Structure

```
frontend/
├── public/                   # Static assets
├── src/
│   ├── assets/               # Images, fonts, etc.
│   ├── components/
│   │   ├── common/           # Reusable atoms (StatusBadge, ErrorAlert, LoadingSpinner)
│   │   ├── layout/           # AppLayout (sidebar + main area)
│   │   ├── dashboard/        # Dashboard-specific widgets
│   │   ├── editor/           # Code editor components
│   │   └── execution/        # Execution display components
│   ├── context/
│   │   └── AuthContext.tsx   # Global auth state (user, login, logout)
│   ├── hooks/                # Custom React hooks
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── GeneratePage.tsx
│   │   ├── TaskHistoryPage.tsx
│   │   └── ExecutionHistoryPage.tsx
│   ├── services/
│   │   ├── api.ts            # Axios instance + error helpers
│   │   ├── auth.ts           # Auth API calls + token management
│   │   ├── tasks.ts          # Code generation API
│   │   └── executions.ts     # Execution API + health check
│   ├── types/
│   │   └── index.ts          # All TypeScript interfaces/types
│   ├── App.tsx               # Router + route protection
│   ├── main.tsx              # React entry point
│   └── index.css             # Tailwind directives + global styles
├── .env.example              # Environment variable template
├── .env                      # Local env (not committed)
├── index.html                # Vite HTML entry
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## Installation

```bash
cd frontend
npm install
# or
pnpm install
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Backend API base URL — no trailing slash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

> The variable must be prefixed with `VITE_` to be exposed to the browser bundle.

## Development

```bash
# Start the dev server on port 3000
npm run dev
# or
pnpm dev
```

The dev server proxies `/api` requests to `http://localhost:8000` to avoid CORS issues during local development.

**Prerequisites:** The FastAPI backend must be running at `http://localhost:8000`.

## Production Build

```bash
npm run build
# or
pnpm build
```

The production build output is in `dist/`. Serve with any static file server or via the FastAPI `StaticFiles` mount.

## Backend Connection

The frontend talks exclusively to the ProofRun backend API. All AI code generation goes through the backend — the frontend never calls any AI provider directly.

Configure `VITE_API_BASE_URL` to point to the deployed backend.

## Backend APIs Used

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register |
| `POST` | `/api/v1/auth/login` | Login (returns JWT) |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `POST` | `/api/v1/generate` | Generate code from prompt |
| `POST` | `/api/v1/execute` | Execute code in Docker sandbox |
| `GET` | `/api/v1/tasks` | Paginated task history |
| `GET` | `/api/v1/executions` | Paginated execution history |
| `GET` | `/api/v1/health` | Backend health check |

## Authentication

- JWT Bearer tokens stored in `localStorage` under `proofrun_token`.
- Tokens are attached to every authenticated request via Axios interceptor.
- 401 responses automatically clear the token and redirect to `/login`.
- Passwords are never logged or stored client-side.

## Features

- ✅ Landing page with feature tour and security highlights
- ✅ Registration (full name, email, password with client-side validation)
- ✅ Login with JWT token management
- ✅ Protected routes (redirects unauthenticated users to login)
- ✅ Dashboard with backend health indicator, recent tasks, and recent executions
- ✅ AI code generation workspace with prompt input and Python syntax highlighting
- ✅ Explicit "Run Code" button — code never executes automatically
- ✅ Full execution result display (stdout, stderr, exit code, security flags)
- ✅ Task history page with pagination and expandable code view
- ✅ Execution history page with pagination and expandable details
- ✅ Responsive layout (desktop, tablet, mobile)
- ✅ Dark developer-focused theme
- ✅ Network/server error handling

## Git Branch

This frontend is developed on `feature/frontend-member3`.
