import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Use real test invoice from docs directory or root
const TEST_INVOICE_PATH = path.join(__dirname, '../../../test_invoice_001.pdf');
const BACKEND_TEST_INVOICE_PATH = path.join(__dirname, '../../../backend/integration_test_invoice.pdf');

// Base URL for backend API (defaults to localhost:7071)
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:7071';

// Find available test invoice file
function getTestInvoicePath(): string {
  if (existsSync(TEST_INVOICE_PATH)) {
    return TEST_INVOICE_PATH;
  }
  if (existsSync(BACKEND_TEST_INVOICE_PATH)) {
    return BACKEND_TEST_INVOICE_PATH;
  }
  throw new Error(`No test invoice file found. Checked:\n- ${TEST_INVOICE_PATH}\n- ${BACKEND_TEST_INVOICE_PATH}`);
}

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
    const invoicePath = getTestInvoicePath();
    console.log(`Using test invoice: ${invoicePath}`);
    
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeVisible({ timeout: 5000 });
    await fileInput.setInputFiles(invoicePath);
    console.log('File selected, waiting for upload...');
    
    // Wait for upload request to complete
    let uploadResponse;
    try {
      uploadResponse = await page.waitForResponse(
        response => {
          const url = response.url();
          const status = response.status();
          if (url.includes('/api/upload')) {
            console.log(`Upload response: ${status} from ${url}`);
          }
          return url.includes('/api/upload') && status === 200;
        },
        { timeout: 30000 }
      );
    } catch (error) {
      // Log all responses to help debug
      console.error('Upload timeout. Checking for error responses...');
      throw new Error(`Upload failed or timed out. Make sure backend is running and accessible. Error: ${error}`);
    }
    
    const uploadData = await uploadResponse.json();
    console.log('Upload response data:', JSON.stringify(uploadData, null, 2));
    
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
        const statusCode = statusResponse.status();
        
        if (statusCode === 404) {
          console.log(`Status not found yet (404), waiting...`);
          await page.waitForTimeout(2000);
          continue;
        }
        
        if (statusResponse.ok()) {
          statusData = await statusResponse.json();
          const overallStatus = statusData.overall_status;
          
          console.log(`Processing status: ${overallStatus} (stage: ${statusData.current_stage || 'N/A'})`);
          
          if (overallStatus === 'COMPLETED' || overallStatus === 'FAILED') {
            processingComplete = true;
            break;
          }
        } else {
          console.log(`Status check returned ${statusCode}`);
        }
      } catch (error: any) {
        console.log(`Status check error: ${error.message || error}`);
      }
      
      // Wait 2 seconds before next check
      await page.waitForTimeout(2000);
    }
    
    if (!processingComplete) {
      console.error(`Processing did not complete. Last status:`, statusData);
      throw new Error(`Processing did not complete within ${maxWaitTime / 1000} seconds. Last status: ${statusData?.overall_status || 'unknown'}`);
    }
    
    console.log(`Processing completed with status: ${statusData.overall_status}`);
    
    // Wait for task to appear in the tasks list
    // Poll the tasks endpoint until we see a new task
    let taskFound = false;
    let foundTask: any = null;
    const taskPollStartTime = Date.now();
    const taskPollMaxTime = 120000; // 2 minutes to find task (processing can take time)
    
    console.log(`Starting to poll for task. Initial task count: ${initialTaskCount}`);
    
    while (!taskFound && (Date.now() - taskPollStartTime) < taskPollMaxTime) {
      try {
        // Use direct API call instead of page reload for faster polling
        const tasksResponse = await request.get(`${BACKEND_URL}/api/tasks`);
        
        if (tasksResponse.ok()) {
          const tasks = await tasksResponse.json();
          const currentTaskCount = Array.isArray(tasks) ? tasks.length : 0;
          
          console.log(`Current task count: ${currentTaskCount} (was ${initialTaskCount})`);
          
          // Check if we have a new task
          if (currentTaskCount > initialTaskCount) {
            // Find the task that matches our file ID (check various patterns)
            const newTask = tasks.find((task: any) => {
              if (!task.id) return false;
              // Try multiple matching strategies
              const taskIdLower = task.id.toLowerCase();
              const fileIdLower = fileId.toLowerCase();
              return taskIdLower.includes(fileIdLower) || 
                     fileIdLower.includes(taskIdLower) ||
                     taskIdLower.replace(/[_-]/g, '').includes(fileIdLower.replace(/[_-]/g, ''));
            });
            
            if (newTask) {
              taskFound = true;
              foundTask = newTask;
              console.log(`Found task: ${newTask.id}, Status: ${newTask.status}`);
              console.log(`Task extracted data:`, JSON.stringify(newTask.extracted, null, 2));
              break;
            } else {
              console.log(`New task count detected but no matching task found. File ID: ${fileId}`);
              console.log(`Available task IDs:`, tasks.map((t: any) => t.id));
            }
          }
        } else {
          console.log(`Tasks API returned ${tasksResponse.status()}`);
        }
      } catch (error: any) {
        console.log(`Error polling tasks: ${error.message || error}`);
      }
      
      // Wait before next poll
      await page.waitForTimeout(3000);
    }
    
    if (!taskFound) {
      // Try one more time with page reload to see current state
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);
      
      const finalTasksResponse = await request.get(`${BACKEND_URL}/api/tasks`);
      if (finalTasksResponse.ok()) {
        const finalTasks = await finalTasksResponse.json();
        console.error(`Final task list:`, JSON.stringify(finalTasks, null, 2));
      }
      
      throw new Error(`Task did not appear in the list within ${taskPollMaxTime / 1000} seconds. File ID: ${fileId}`);
    }
    
    // Reload page to show the task in UI
    await page.reload({ waitUntil: 'networkidle' });
    await expect(page.getByText('Mai Statisztika')).toBeVisible({ timeout: 10000 });
    
    // Verify task has extracted data
    expect(foundTask.extracted).toBeDefined();
    
    // Wait for the task to appear in the UI
    // Check for vendor name if available
    if (foundTask.extracted?.vendor) {
      await expect(page.getByText(foundTask.extracted.vendor, { exact: false })).toBeVisible({ timeout: 15000 });
    } else {
      console.warn('No vendor name in extracted data');
    }
    
    // Check for amount if available
    if (foundTask.extracted?.amount) {
      const amountText = new Intl.NumberFormat('hu-HU', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(foundTask.extracted.amount);
      const currency = foundTask.extracted.currency || 'HUF';
      await expect(page.getByText(`${amountText} ${currency}`, { exact: false })).toBeVisible({ timeout: 15000 });
    } else {
      console.warn('No amount in extracted data');
    }
    
    // Verify the task appears in the UI table
    await expect(page.locator('table, [role="table"], .task-list, .task-item')).toBeVisible({ timeout: 5000 });
  });

});
