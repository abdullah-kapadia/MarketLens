# MarketLens Frontend — Environment Setup Guide

**Document 12 of 12** | Frontend-specific

---

## 1. Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Node.js | 18.17+ (LTS recommended) | `node --version` |
| npm | 9+ (comes with Node.js) | `npm --version` |
| Git | 2.30+ | `git --version` |
| Backend running | — | `curl http://localhost:8000/api/v1/health` |

### Install Node.js

**Windows:** Download from [nodejs.org](https://nodejs.org/) (LTS version) or use:
```bash
winget install OpenJS.NodeJS.LTS
```

**macOS:**
```bash
brew install node@18
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 2. Project Initialization

### 2.1 Create Next.js Project

```bash
npx create-next-app@latest marketlens-frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*" \
  --use-npm
```

When prompted:
- **Would you like to use TypeScript?** → Yes
- **Would you like to use ESLint?** → Yes
- **Would you like to use Tailwind CSS?** → Yes
- **Would you like to use `src/` directory?** → No
- **Would you like to use App Router?** → Yes
- **Would you like to customize the default import alias?** → Yes → `@/*`

### 2.2 Navigate to Project

```bash
cd marketlens-frontend
```

---

## 3. Dependencies

### 3.1 Install All Dependencies

```bash
npm install react-pdf @react-pdf-viewer/core pdfjs-dist clsx
```

### 3.2 package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-pdf": "^9.1.0",
    "pdfjs-dist": "^4.4.0",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "@types/node": "^20.14.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.0"
  }
}
```

### 3.3 Dependency Purposes

| Package | Purpose |
|---------|---------|
| `next` | React framework with App Router, SSR, file-based routing |
| `react` / `react-dom` | UI library |
| `react-pdf` | Render PDF documents inline in the browser |
| `pdfjs-dist` | PDF.js worker (required by react-pdf) |
| `clsx` | Conditional CSS class merging utility |
| `tailwindcss` | Utility-first CSS framework |
| `typescript` | Type safety |

---

## 4. Environment Variables

### 4.1 `.env.example`

```bash
# MarketLens Frontend Environment Variables
# Copy this file to .env.local and update values

# ===========================================
# API Configuration
# ===========================================

# Backend API URL (no trailing slash)
# Default: http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# ===========================================
# Feature Flags
# ===========================================

# Enable mock data mode (bypasses backend, uses local mock data)
# Values: true | false
# Default: false
NEXT_PUBLIC_MOCK_MODE=false

# Enable debug logging in browser console
# Values: true | false
# Default: false
NEXT_PUBLIC_DEBUG=false
```

### 4.2 Variable Reference

| Variable | Required | Default | Type | Description |
|----------|----------|---------|------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | string | Backend API base URL. No trailing slash. |
| `NEXT_PUBLIC_MOCK_MODE` | No | `false` | boolean | When `true`, uses hardcoded mock data instead of real API calls. Useful for frontend development without backend. |
| `NEXT_PUBLIC_DEBUG` | No | `false` | boolean | Enables verbose console logging of SSE events, API calls, and state transitions. |

### 4.3 Setup

```bash
cp .env.example .env.local
```

Edit `.env.local` with your values. The `.env.local` file is gitignored by default.

> **Note:** All frontend env vars must be prefixed with `NEXT_PUBLIC_` to be accessible in the browser bundle. Never put secrets in frontend env vars — they are embedded in the client-side JavaScript.

---

## 5. Configuration Files

### 5.1 `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "ml-bg": "#0f172a",
        "ml-card": "#1e293b",
        "ml-border": "#334155",
        "ml-text": "#f1f5f9",
        "ml-muted": "#94a3b8",
        "ml-bullish": "#10b981",
        "ml-bearish": "#ef4444",
        "ml-neutral": "#f59e0b",
        "ml-accent": "#3b82f6",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
      animation: {
        "slide-in": "slideIn 150ms ease-out",
        "fade-in": "fadeIn 200ms ease-out",
        "pulse-dot": "pulseDot 1.5s ease-in-out infinite",
      },
      keyframes: {
        slideIn: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

### 5.2 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "es2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 5.3 `next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for Docker deployment
  output: "standalone",

  // Webpack config for react-pdf
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
};

module.exports = nextConfig;
```

### 5.4 `app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --ml-bg: #0f172a;
  --ml-card: #1e293b;
  --ml-border: #334155;
}

body {
  @apply bg-ml-bg text-ml-text;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Custom scrollbar styling (Webkit browsers) */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: var(--ml-bg);
}

::-webkit-scrollbar-thumb {
  background: var(--ml-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

/* Firefox scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--ml-border) var(--ml-bg);
}

/* react-pdf page styling */
.react-pdf__Page__canvas {
  max-width: 100% !important;
  height: auto !important;
}
```

---

## 6. Directory Structure Setup

Create the following directory structure after project initialization:

```bash
mkdir -p components hooks lib public
```

Final structure:

```
marketlens-frontend/
├── app/
│   ├── layout.tsx          # Root layout (dark class, Inter font, metadata)
│   ├── page.tsx            # Single page → renders Dashboard
│   └── globals.css         # Tailwind + custom styles
├── components/
│   ├── Dashboard.tsx
│   ├── Sidebar.tsx
│   ├── StockList.tsx
│   ├── ReportHistory.tsx
│   ├── StockHeader.tsx
│   ├── AnalyzeButton.tsx
│   ├── ReasoningPanel.tsx
│   ├── ReasoningStep.tsx
│   ├── ReportViewer.tsx
│   ├── QuickStats.tsx
│   ├── EmptyState.tsx
│   └── LoadingState.tsx
├── hooks/
│   └── useAgentStream.ts
├── lib/
│   ├── api.ts
│   └── types.ts
├── public/
│   └── logo.svg
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
├── package.json
├── .env.example
├── .env.local            # (gitignored)
├── Dockerfile
└── .gitignore
```

---

## 7. Mock Data Mode

For frontend development without a running backend, enable mock mode:

```bash
# .env.local
NEXT_PUBLIC_MOCK_MODE=true
```

Create `lib/mock-data.ts`:

```typescript
import { Stock, AgentStep, ReportSummary, AgentResult } from "./types";

export const MOCK_STOCKS: Stock[] = [
  {
    ticker: "OGDC",
    name: "Oil & Gas Development Company",
    sector: "Energy",
    current_price: 118.5,
    change_percent: -2.3,
    last_updated: "2026-02-10",
  },
  {
    ticker: "TRG",
    name: "TRG Pakistan",
    sector: "Technology",
    current_price: 145.75,
    change_percent: 3.8,
    last_updated: "2026-02-10",
  },
  {
    ticker: "PSO",
    name: "Pakistan State Oil",
    sector: "Energy",
    current_price: 215.0,
    change_percent: -1.1,
    last_updated: "2026-02-10",
  },
  {
    ticker: "LUCK",
    name: "Lucky Cement",
    sector: "Cement",
    current_price: 780.0,
    change_percent: 0.5,
    last_updated: "2026-02-10",
  },
  {
    ticker: "ENGRO",
    name: "Engro Corporation",
    sector: "Conglomerate",
    current_price: 320.5,
    change_percent: 1.2,
    last_updated: "2026-02-10",
  },
];

export const MOCK_REASONING_STEPS: AgentStep[] = [
  {
    type: "reasoning",
    content: "Loading OGDC price data for the last 6 months to assess the overall trend.",
    iteration: 1,
    timestamp: new Date().toISOString(),
  },
  {
    type: "tool_call",
    tool_name: "load_stock_data",
    tool_input: { ticker: "OGDC", period: "6M" },
    iteration: 1,
    timestamp: new Date().toISOString(),
  },
  {
    type: "observation",
    tool_name: "load_stock_data",
    content: "OGDC: Current PKR 118.50, down 16.6% over 6M. Range: 112-142. Avg volume: 5.2M shares/day.",
    iteration: 1,
    timestamp: new Date().toISOString(),
  },
  {
    type: "reasoning",
    content: "Significant decline of 16.6%. Let me check RSI to see if the stock is oversold.",
    iteration: 2,
    timestamp: new Date().toISOString(),
  },
  {
    type: "tool_call",
    tool_name: "calculate_indicator",
    tool_input: { ticker: "OGDC", indicator: "RSI", params: { period: 14 } },
    iteration: 2,
    timestamp: new Date().toISOString(),
  },
  {
    type: "observation",
    tool_name: "calculate_indicator",
    content: "RSI(14) = 32.1 — Oversold territory. Selling pressure may be exhausting.",
    iteration: 2,
    timestamp: new Date().toISOString(),
  },
];

export function simulateMockStream(
  onStep: (step: AgentStep) => void,
  onComplete: () => void
): () => void {
  let index = 0;
  const interval = setInterval(() => {
    if (index < MOCK_REASONING_STEPS.length) {
      onStep(MOCK_REASONING_STEPS[index]);
      index++;
    } else {
      clearInterval(interval);
      onComplete();
    }
  }, 1500);

  return () => clearInterval(interval); // cleanup function
}
```

---

## 8. Running the Application

### 8.1 Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

**Hot reload** is enabled — changes to components update instantly.

### 8.2 Production Build

```bash
npm run build
npm run start
```

### 8.3 Type Checking

```bash
npx tsc --noEmit
```

### 8.4 Linting

```bash
npm run lint
```

---

## 9. Docker

### 9.1 Dockerfile

```dockerfile
FROM node:18-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build the application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variables
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### 9.2 Build & Run

```bash
# Build image
docker build -t marketlens-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://host.docker.internal:8000 \
  marketlens-frontend
```

> **Note:** When running in Docker, the backend URL must use `host.docker.internal` (on Docker Desktop) or the container network address to reach the backend container.

### 9.3 Docker Compose (from project root)

```yaml
# docker-compose.yml (frontend section)
frontend:
  build:
    context: ./marketlens-frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://backend:8000
  depends_on:
    - backend
```

---

## 10. Troubleshooting

### 10.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Module not found: react-pdf` | Missing dependency | `npm install react-pdf pdfjs-dist` |
| PDF not rendering | PDF.js worker not configured | Add `pdfjs.GlobalWorkerOptions.workerSrc` in ReportViewer |
| Canvas error with react-pdf | SSR trying to use canvas | Add `canvas: false` to next.config.js webpack config |
| CORS error on API calls | Backend CORS not configured | Ensure backend has `http://localhost:3000` in CORS origins |
| SSE stream not working | Backend not returning event-stream | Check `Content-Type: text/event-stream` on backend response |
| Blank page on load | Hydration mismatch | Ensure components using browser APIs are client-only (`"use client"`) |
| Styles not applying | Tailwind not scanning files | Check `content` paths in `tailwind.config.ts` |
| Mock mode not working | Env var not set | Ensure `NEXT_PUBLIC_MOCK_MODE=true` in `.env.local` and restart dev server |
| Port 3000 in use | Another app running | Kill the process: `npx kill-port 3000` or use `npm run dev -- -p 3001` |
| TypeScript errors | Type mismatch with backend | Regenerate types from API_CONTRACT.md |

### 10.2 Verifying Backend Connection

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check if CORS is working (from browser console)
fetch("http://localhost:8000/api/v1/stocks")
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

# Test SSE endpoint
curl -N -X POST http://localhost:8000/api/v1/analyze/OGDC
```

### 10.3 Debug Mode

Enable debug logging:

```bash
# .env.local
NEXT_PUBLIC_DEBUG=true
```

This logs to browser console:
- Every SSE event received
- State transitions in useAgentStream
- API call URLs and responses
- Component render counts (in development)

---

*Reference: [README.md](README.md) for project overview, [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for component specs, [TECH_SPEC.md](TECH_SPEC.md) for technical details.*
