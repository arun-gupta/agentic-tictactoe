This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

### Quick Start (Recommended)

From the **project root**, run the setup script that starts both the backend API and UI:

```bash
./start_ui.sh
```

This script will:
- **Auto-activate Python virtual environment** (if found: `venv/`, `.venv/`, or `env/`)
- Install UI dependencies if needed
- Start the backend API on http://localhost:8000
- Start the UI development server on http://localhost:3000
- Handle cleanup when you press Ctrl+C

**Note:** The script automatically detects and activates your Python virtual environment. If you prefer to use a specific venv, activate it first before running the script.

### Manual Start

If you prefer to run things manually:

1. **Start the backend API** (from project root):
   ```bash
   uvicorn src.api.main:app --reload
   ```

2. **Install dependencies and start UI** (from `src/ui` directory):
   ```bash
   npm install
   npm run dev
   ```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Testing

Run the comprehensive test suite with Vitest:

```bash
# Run tests in watch mode
npm test

# Run tests once (CI mode)
npm run test:run

# Run tests with coverage report
npm run test:coverage
```

## Other Commands

```bash
# Type checking
npm run typecheck

# Linting
npm run lint

# Build for production
npm run build

# Start production build
npm start
```

## Environment Variables

The UI connects to the backend API at `http://localhost:8000` by default. You can override this:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
