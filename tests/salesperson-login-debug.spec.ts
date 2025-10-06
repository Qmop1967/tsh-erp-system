import { test, expect } from '@playwright/test';

/**
 * Salesperson Login Debug Test
 * Tests the Flutter salesperson app login functionality
 * URL: http://localhost:8080
 * User: frati@tsh.sale (from screenshot)
 */

test.describe('Salesperson App Login Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the salesperson app
    await page.goto('http://localhost:8080', { waitUntil: 'networkidle' });
    
    // Wait for Flutter to initialize
    await page.waitForTimeout(2000);
  });

  test('should load the salesperson login page', async ({ page }) => {
    console.log('🧪 Test 1: Checking if login page loads...');
    
    // Check if the page loaded
    await expect(page).toHaveTitle(/TSH/);
    
    // Take a screenshot
    await page.screenshot({ path: 'test-results/salesperson-login-page.png', fullPage: true });
    
    console.log('✅ Login page loaded successfully');
  });

  test('should display login form elements', async ({ page }) => {
    console.log('🧪 Test 2: Checking form elements...');
    
    // Wait for the page to be fully rendered
    await page.waitForLoadState('networkidle');
    
    // Get the page content to debug
    const content = await page.content();
    console.log('Page has Flutter view:', content.includes('flutter-view'));
    console.log('Page has flt-glass-pane:', content.includes('flt-glass-pane'));
    
    // Since it's a Flutter app, we need to find elements differently
    // Look for any input fields or interactive elements
    const inputs = await page.locator('input').count();
    console.log(`Found ${inputs} input elements`);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/salesperson-form-elements.png', fullPage: true });
  });

  test('should attempt login with salesperson credentials', async ({ page }) => {
    console.log('🧪 Test 3: Attempting login...');
    
    // Wait for Flutter app to be ready
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Try to find and click on email field
    try {
      // Flutter web apps render to canvas, so we need to use different selectors
      // Look for semantics or input elements
      const emailField = page.locator('input[type="email"], input[type="text"]').first();
      const passwordField = page.locator('input[type="password"]').first();
      const loginButton = page.locator('button:has-text("تسجيل"), button:has-text("Login")').first();
      
      // Check if fields are visible
      const emailVisible = await emailField.isVisible().catch(() => false);
      const passwordVisible = await passwordField.isVisible().catch(() => false);
      const buttonVisible = await loginButton.isVisible().catch(() => false);
      
      console.log('Email field visible:', emailVisible);
      console.log('Password field visible:', passwordVisible);
      console.log('Login button visible:', buttonVisible);
      
      if (emailVisible && passwordVisible && buttonVisible) {
        // Fill in the form
        await emailField.fill('frati@tsh.sale');
        await passwordField.fill('test123'); // Use actual password
        
        // Take screenshot before clicking
        await page.screenshot({ path: 'test-results/salesperson-before-login.png', fullPage: true });
        
        // Click login button
        await loginButton.click();
        
        // Wait for navigation or error
        await page.waitForTimeout(3000);
        
        // Take screenshot after clicking
        await page.screenshot({ path: 'test-results/salesperson-after-login.png', fullPage: true });
        
        // Check for error messages
        const pageText = await page.locator('body').textContent();
        console.log('Page text includes error:', pageText?.includes('error') || pageText?.includes('خطأ'));
        
      } else {
        console.log('❌ Form fields not visible - Flutter canvas rendering');
        await page.screenshot({ path: 'test-results/salesperson-form-not-visible.png', fullPage: true });
      }
      
    } catch (error) {
      console.error('Error during login attempt:', error);
      await page.screenshot({ path: 'test-results/salesperson-login-error.png', fullPage: true });
    }
  });

  test('should check API connection', async ({ page }) => {
    console.log('🧪 Test 4: Checking API connection...');
    
    // Listen for network requests
    const apiRequests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('localhost:8000')) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          headers: request.headers(),
        });
      }
    });
    
    // Listen for responses
    const apiResponses: any[] = [];
    page.on('response', async response => {
      if (response.url().includes('localhost:8000')) {
        const status = response.status();
        let body: string | null = null;
        try {
          body = await response.text();
        } catch (e) {
          body = 'Could not read response body';
        }
        apiResponses.push({
          url: response.url(),
          status,
          body,
        });
      }
    });
    
    // Listen for console logs from the app
    page.on('console', msg => {
      console.log('Browser console:', msg.type(), msg.text());
    });
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);
    
    console.log('API Requests made:', apiRequests.length);
    console.log('API Responses received:', apiResponses.length);
    
    if (apiRequests.length > 0) {
      console.log('First API request:', JSON.stringify(apiRequests[0], null, 2));
    }
    
    if (apiResponses.length > 0) {
      console.log('First API response:', JSON.stringify(apiResponses[0], null, 2));
    }
  });

  test('should debug Flutter semantics', async ({ page }) => {
    console.log('🧪 Test 5: Debugging Flutter semantics...');
    
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Try to find Flutter semantics elements
    const flutterView = page.locator('flutter-view');
    const semanticsHost = page.locator('flt-semantics-host');
    const glassPane = page.locator('flt-glass-pane');
    
    console.log('Flutter view exists:', await flutterView.count() > 0);
    console.log('Semantics host exists:', await semanticsHost.count() > 0);
    console.log('Glass pane exists:', await glassPane.count() > 0);
    
    // Get all inputs
    const allInputs = await page.locator('input').all();
    console.log('Total input elements:', allInputs.length);
    
    for (let i = 0; i < allInputs.length; i++) {
      const input = allInputs[i];
      const type = await input.getAttribute('type');
      const placeholder = await input.getAttribute('placeholder');
      const name = await input.getAttribute('name');
      const visible = await input.isVisible();
      
      console.log(`Input ${i + 1}:`, { type, placeholder, name, visible });
    }
    
    // Get all buttons
    const allButtons = await page.locator('button').all();
    console.log('Total button elements:', allButtons.length);
    
    for (let i = 0; i < allButtons.length; i++) {
      const button = allButtons[i];
      const text = await button.textContent();
      const visible = await button.isVisible();
      
      console.log(`Button ${i + 1}:`, { text, visible });
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/salesperson-semantics-debug.png', fullPage: true });
  });

  test('should test backend API directly', async ({ request }) => {
    console.log('🧪 Test 6: Testing backend API directly...');
    
    // Test if backend is accessible
    try {
      const healthResponse = await request.get('http://localhost:8000/health');
      console.log('Backend health status:', healthResponse.status());
      console.log('Backend health body:', await healthResponse.json());
    } catch (error) {
      console.error('❌ Backend health check failed:', error);
    }
    
    // Test login endpoint with CORRECT URL (with /api prefix)
    try {
      const loginResponse = await request.post('http://localhost:8000/api/auth/login/mobile', {
        data: {
          email: 'frati@tsh.sale',
          password: 'test123'
        },
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ Login API status (FIXED URL):', loginResponse.status());
      console.log('Login API response:', await loginResponse.text());
      
      if (loginResponse.status() === 200) {
        console.log('🎉 API login successful with correct endpoint!');
      } else if (loginResponse.status() === 401) {
        console.log('✅ Endpoint works! (401 = wrong password, endpoint is accessible)');
      } else {
        console.log('❌ API login failed with status:', loginResponse.status());
      }
    } catch (error) {
      console.error('❌ Login API call failed:', error);
    }
  });

  test('should check user credentials in database', async ({ request }) => {
    console.log('🧪 Test 7: Checking if user exists...');
    
    // First, try to get all users or check if the salesperson user exists
    try {
      // You might need admin credentials for this
      const usersResponse = await request.get('http://localhost:8000/api/users', {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Users API status:', usersResponse.status());
      
      if (usersResponse.status() === 200) {
        const users = await usersResponse.json();
        console.log('Users found:', Array.isArray(users) ? users.length : 'Not an array');
        
        // Look for the salesperson user
        const salespersonUser = Array.isArray(users) 
          ? users.find((u: any) => u.email === 'frati@tsh.sale')
          : null;
        
        if (salespersonUser) {
          console.log('✅ Salesperson user found:', salespersonUser);
        } else {
          console.log('❌ Salesperson user NOT found in database');
        }
      }
    } catch (error) {
      console.error('❌ Could not fetch users:', error);
    }
  });

  test('should capture network errors', async ({ page }) => {
    console.log('🧪 Test 8: Capturing network errors...');
    
    const networkErrors: any[] = [];
    const failedRequests: any[] = [];
    
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        method: request.method(),
        failure: request.failure()?.errorText,
      });
    });
    
    page.on('pageerror', error => {
      networkErrors.push({
        message: error.message,
        stack: error.stack,
      });
    });
    
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);
    
    console.log('Failed requests:', failedRequests.length);
    if (failedRequests.length > 0) {
      console.log('Failed requests details:', JSON.stringify(failedRequests, null, 2));
    }
    
    console.log('Page errors:', networkErrors.length);
    if (networkErrors.length > 0) {
      console.log('Page errors details:', JSON.stringify(networkErrors, null, 2));
    }
    
    if (failedRequests.length === 0 && networkErrors.length === 0) {
      console.log('✅ No network errors detected');
    }
  });
});
