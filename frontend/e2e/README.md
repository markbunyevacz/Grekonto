# E2E Testing Guide

## Prerequisites

- Node.js installed
- Frontend dependencies installed (`npm install`)

## Running Tests

All E2E commands must be run from the `frontend` directory:

```bash
cd frontend
```

### Available Commands

1. **Run all E2E tests:**
   ```bash
   npm run e2e
   ```
   Runs tests in Chromium, Firefox, and WebKit browsers.

2. **Run tests in interactive UI mode:**
   ```bash
   npm run e2e:ui
   ```
   Opens Playwright's interactive UI where you can:
   - Run tests individually
   - Watch tests execute in real-time
   - Debug and re-run tests
   - See detailed logs and screenshots

3. **View HTML test report:**
   ```bash
   npm run e2e:report
   ```
   Opens the last test run's HTML report in your browser.

   **Note:** If you get a port conflict error (EADDRINUSE), you can:
   - Wait a few seconds for the previous report server to stop
   - Or open the report directly: `start playwright-report\index.html`

## Test Structure

```
frontend/e2e/
├── fixtures/          # Test data files (PDFs, images, etc.)
├── specs/             # Test files (*.spec.ts)
└── utils/             # Helper functions (optional)
```

## Writing Tests

Tests are written in TypeScript using Playwright's API. See `e2e/specs/workflow.spec.ts` for an example.

## Troubleshooting

### Port Already in Use

If `npm run e2e:report` fails with "address already in use":
```powershell
# Find the process using port 9323
netstat -ano | findstr :9323

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Tests Fail to Start

- Ensure the frontend dev server can start: `npm run dev`
- Check that all dependencies are installed: `npm install`
- Verify Playwright browsers are installed: `npx playwright install`

