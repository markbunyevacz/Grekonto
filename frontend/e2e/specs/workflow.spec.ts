import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Use real test invoice from docs directory or root
const TEST_INVOICE_PATH = path.join(__dirname, '../../../test_invoice_001.pdf');
const BACKEND_TEST_INVOICE_PATH = path.join(__dirname, '../../../backend/integration_test_invoice.pdf');

// Base URL for backend API (defaults to localhost:7071)
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:7071';

test.describe('End-to-End Workflow', () => {

  test.beforeEach(async ({ page }) => {
    // Log console errors for debugging
    page.on('console', msg => {
      if (msg.type() === 'error') console.log(`Browser Error: "${msg.text()}"`);
    });

    // Log network failures
    page.on('response', response => {
      if (response.status() >= 400) {
        console.log(`HTTP ${response.status()}: ${response.url()}`);
      }
    });
  });

  test('User can login, upload an invoice, and see it in the list', async ({ page, request }) => {
    // Check if backend is available
    try {
      const healthCheck = await request.get(`${BACKEND_URL}/api/tasks`);
      if (healthCheck.status() >= 500) {
        test.skip(true, 'Backend is not available. Make sure Azure Functions is running on port 7071.');
      }
    } catch (error) {
      test.skip(true, 'Backend is not available. Make sure Azure Functions is running on port 7071.');
    }

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
    
    // Get initial task count
    const initialTasksResponse = await page.waitForResponse(response => 
      response.url().includes('/api/tasks') && response.status() === 200
    );
    const initialTasks = await initialTasksResponse.json();
    const initialTaskCount = Array.isArray(initialTasks) ? initialTasks.length : 0;
    
    // Handle dialogs (if any appear)
    page.on('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    // Upload test invoice file
    // Try root test_invoice_001.pdf first, fallback to backend integration_test_invoice.pdf
    let invoicePath = TEST_INVOICE_PATH;
    try {
      await page.locator('input[type="file"]').setInputFiles(invoicePath);
    } catch (error) {
      // Try fallback path
      invoicePath = BACKEND_TEST_INVOICE_PATH;
      await page.locator('input[type="file"]').setInputFiles(invoicePath);
    }
    
    // Wait for upload request to complete
    const uploadResponse = await page.waitForResponse(
      response => response.url().includes('/api/upload') && response.status() === 200,
      { timeout: 30000 }
    );
    
    const uploadData = await uploadResponse.json();
    const fileId = uploadData.file_id;
    
    expect(fileId).toBeTruthy();
    console.log(`Upload successful. File ID: ${fileId}`);
    
    // Wait for processing to complete by polling status endpoint
    let processingComplete = false;
    let statusData: any = null;
    const maxWaitTime = 120000; // 2 minutes max wait
    const startTime = Date.now();
    
    while (!processingComplete && (Date.now() - startTime) < maxWaitTime) {
      try {
        const statusResponse = await request.get(`${BACKEND_URL}/api/status/${fileId}`);
        if (statusResponse.ok()) {
          statusData = await statusResponse.json();
          const overallStatus = statusData.overall_status;
          
          console.log(`Processing status: ${overallStatus} (stage: ${statusData.current_stage})`);
          
          if (overallStatus === 'COMPLETED' || overallStatus === 'FAILED') {
            processingComplete = true;
            break;
          }
        }
      } catch (error) {
        console.log(`Status check error: ${error}`);
      }
      
      // Wait 2 seconds before next check
      await page.waitForTimeout(2000);
    }
    
    if (!processingComplete) {
      throw new Error(`Processing did not complete within ${maxWaitTime / 1000} seconds`);
    }
    
    // Wait for task to appear in the tasks list
    // Poll the tasks endpoint until we see a new task
    let taskFound = false;
    const taskPollStartTime = Date.now();
    const taskPollMaxTime = 60000; // 1 minute to find task
    
    while (!taskFound && (Date.now() - taskPollStartTime) < taskPollMaxTime) {
      // Reload page to trigger tasks fetch
      await page.reload({ waitUntil: 'networkidle' });
      
      // Wait for tasks API call
      const tasksResponse = await page.waitForResponse(
        response => response.url().includes('/api/tasks') && response.status() === 200,
        { timeout: 5000 }
      );
      
      const tasks = await tasksResponse.json();
      const currentTaskCount = Array.isArray(tasks) ? tasks.length : 0;
      
      // Check if we have a new task
      if (currentTaskCount > initialTaskCount) {
        // Find the task that matches our file ID
        const newTask = tasks.find((task: any) => 
          task.id && (task.id.includes(fileId) || fileId.includes(task.id))
        );
        
        if (newTask) {
          taskFound = true;
          console.log(`Found task: ${newTask.id}, Status: ${newTask.status}`);
          
          // Verify task has extracted data
          expect(newTask.extracted).toBeDefined();
          
          // Wait for the task to appear in the UI
          // Check for vendor name if available
          if (newTask.extracted?.vendor) {
            await expect(page.getByText(newTask.extracted.vendor, { exact: false })).toBeVisible({ timeout: 10000 });
          }
          
          // Check for amount if available
          if (newTask.extracted?.amount) {
            const amountText = new Intl.NumberFormat('hu-HU', {
              style: 'decimal',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0
            }).format(newTask.extracted.amount);
            const currency = newTask.extracted.currency || 'HUF';
            await expect(page.getByText(`${amountText} ${currency}`, { exact: false })).toBeVisible({ timeout: 10000 });
          }
          
          break;
        }
      }
      
      // Wait before next poll
      await page.waitForTimeout(3000);
    }
    
    if (!taskFound) {
      throw new Error(`Task did not appear in the list within ${taskPollMaxTime / 1000} seconds`);
    }
    
    // Verify the task appears in the UI table
    await expect(page.locator('table, [role="table"], .task-list, .task-item')).toBeVisible({ timeout: 5000 });
  });

});
