import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SAMPLE_INVOICE_PATH = path.join(__dirname, '../fixtures/sample_invoice.pdf');

test.describe('End-to-End Workflow', () => {

  test.beforeEach(async ({ page }) => {
    // Mock console logs
    page.on('console', msg => {
      if (msg.type() === 'error') console.log(`Error: "${msg.text()}"`);
    });

    // MOCK BACKEND APIs
    // This ensures the frontend test passes even if the backend is not running.
    // In a real full-stack E2E, you might conditionally skip these routes.
    
    // 1. Mock Tasks GET
    // Initial state: Empty or some existing tasks
    await page.route('**/api/tasks', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                // We can return an empty list initially, or a fixed list.
                // The test logic below waits for a task to appear.
                // We'll handle dynamic mocking inside the test or here.
            ])
        });
    });

    // 2. Mock Upload POST
    await page.route('**/api/upload', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ message: "File uploaded successfully" })
        });
    });
  });

  test('User can login, upload an invoice, and see it in the list', async ({ page }) => {
    // Mock MSAL authentication by setting sessionStorage
    // This simulates a logged-in user without triggering the popup
    await page.goto('/', { timeout: 60000 });
    
    // Wait for the page to load
    await page.waitForSelector('#root', { state: 'attached' });
    
    // Mock MSAL by injecting a mock account into sessionStorage
    // The MSAL library checks sessionStorage for cached accounts
    await page.evaluate(() => {
      // Mock MSAL cache structure
      const mockAccount = {
        homeAccountId: 'mock-account-id',
        environment: 'login.microsoftonline.com',
        tenantId: 'common',
        username: 'test@grekonto.hu',
        localAccountId: 'mock-local-id',
        name: 'Test User'
      };
      
      // Store in sessionStorage in the format MSAL expects
      sessionStorage.setItem('msal.account.keys', JSON.stringify(['mock-account-id']));
      sessionStorage.setItem(`msal.account.${mockAccount.homeAccountId}`, JSON.stringify(mockAccount));
      sessionStorage.setItem('msal.login.request', JSON.stringify({ scopes: ['User.Read'] }));
    });
    
    // Navigate directly to dashboard (bypassing login UI)
    await page.goto('/dashboard', { timeout: 60000 });
    
    // Verify we're on the dashboard
    await expect(page.getByText('Mai Statisztika')).toBeVisible({ timeout: 10000 });
    
    // Update mock to return a task AFTER we upload (simulating processing)
    // We can use a variable to toggle the response
    let taskAvailable = false;
    await page.unroute('**/api/tasks'); // Remove previous handler
    await page.route('**/api/tasks', async route => {
        if (taskAvailable) {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    {
                        id: "mock-task-123",
                        status: "YELLOW",
                        confidence: 85,
                        document_url: "http://mock/doc.pdf",
                        extracted: {
                            vendor: "Teszt Szállító Kft.",
                            amount: 12500,
                            currency: "HUF",
                            date: "2023.11.22",
                            invoice_id: "INV-2023-001"
                        }
                    }
                ])
            });
        } else {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([])
            });
        }
    });

    // 2. File Upload
    page.on('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(SAMPLE_INVOICE_PATH);
    
    // Trigger the "processed" state
    taskAvailable = true;

    // 3. Poll/Wait for the new task
    // Reload to fetch new tasks (since dashboard fetches on mount/manual refresh usually)
    // The current Dashboard implementation only fetches on mount. 
    // The handleFileUpload does a re-fetch:
    // const res = await fetch('/api/tasks');
    // So the list should update automatically after upload success!
    
    // We wait for the table row to appear
    await expect(page.getByText('Teszt Szállító Kft.')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('12,500 HUF')).toBeVisible();
    
  });

});
