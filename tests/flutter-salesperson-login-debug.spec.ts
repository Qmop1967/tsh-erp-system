import { test, expect } from '@playwright/test';

/**
 * Playwright Test: Flutter Salesperson App Login Debug
 * Enhanced test to diagnose why login form is not appearing
 */

test.describe('Flutter Salesperson App - Login Debug', () => {
  const FLUTTER_APP_URL = 'http://localhost:8080';
  const BACKEND_URL = 'http://localhost:8000';
  
  test.beforeEach(async ({ page }) => {
    // Listen to console messages
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`❌ Console Error: ${msg.text()}`);
      } else if (msg.type() === 'warning') {
        console.log(`⚠️  Console Warning: ${msg.text()}`);
      } else {
        console.log(`📝 Console: ${msg.text()}`);
      }
    });

    // Listen to network requests
    page.on('request', request => {
      if (request.url().includes('login')) {
        console.log(`📤 Request: ${request.method()} ${request.url()}`);
        console.log(`   Headers:`, request.headers());
        if (request.postData()) {
          console.log(`   Body:`, request.postData());
        }
      }
    });

    // Listen to network responses
    page.on('response', async response => {
      if (response.url().includes('login')) {
        console.log(`📥 Response: ${response.status()} ${response.url()}`);
        try {
          const body = await response.text();
          console.log(`   Body:`, body);
        } catch (e) {
          console.log(`   Body: (Unable to read)`);
        }
      }
    });

    // Listen to page errors
    page.on('pageerror', error => {
      console.log(`💥 Page Error: ${error.message}`);
    });
  });

  test('should diagnose Flutter app rendering', async ({ page }) => {
    console.log('\n🔍 DIAGNOSTIC TEST: Flutter App Rendering\n');
    console.log('='.repeat(60));
    
    // Step 1: Check if Flutter app is accessible
    console.log('\n📍 Step 1: Checking Flutter app accessibility...');
    try {
      const response = await page.goto(FLUTTER_APP_URL);
      console.log(`   ✅ Status: ${response?.status()}`);
      console.log(`   ✅ URL: ${page.url()}`);
    } catch (e) {
      console.log(`   ❌ Error navigating to Flutter app: ${e}`);
      return;
    }
    
    // Step 2: Wait for page load and check Flutter initialization
    console.log('\n📍 Step 2: Waiting for page load...');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000); // Give Flutter time to initialize
    
    // Step 3: Check for Flutter loading indicator
    console.log('\n📍 Step 3: Checking Flutter loading state...');
    const flutterView = await page.locator('flt-glass-pane, flutter-view, [flt-renderer]');
    const flutterViewCount = await flutterView.count();
    console.log(`   Flutter views found: ${flutterViewCount}`);
    
    // Step 4: Capture full HTML structure
    console.log('\n📍 Step 4: Analyzing HTML structure...');
    const bodyContent = await page.evaluate(() => {
      return {
        bodyHTML: document.body.innerHTML.substring(0, 1000),
        bodyText: document.body.innerText.substring(0, 500),
        scriptTags: Array.from(document.scripts).map(s => ({
          src: s.src,
          loaded: (s as any).readyState || 'unknown'
        })),
        allElements: document.querySelectorAll('*').length,
        flutterElements: document.querySelectorAll('[flt-renderer], flt-glass-pane, flutter-view').length
      };
    });
    
    console.log(`   Total HTML elements: ${bodyContent.allElements}`);
    console.log(`   Flutter-specific elements: ${bodyContent.flutterElements}`);
    console.log(`   Script tags: ${bodyContent.scriptTags.length}`);
    console.log(`   Body text preview: ${bodyContent.bodyText.replace(/\n/g, ' ').substring(0, 100)}`);
    
    // Step 5: Check for Flutter bootstrap
    console.log('\n📍 Step 5: Checking Flutter bootstrap...');
    const hasFlutterBootstrap = await page.evaluate(() => {
      return window.hasOwnProperty('_flutter') || 
             window.hasOwnProperty('flutterConfiguration') ||
             document.querySelector('script[src*="flutter"]') !== null;
    });
    console.log(`   Flutter bootstrap detected: ${hasFlutterBootstrap}`);
    
    // Step 6: Check for input elements (any type)
    console.log('\n📍 Step 6: Looking for input elements...');
    const inputs = await page.evaluate(() => {
      const allInputs = document.querySelectorAll('input');
      return {
        count: allInputs.length,
        types: Array.from(allInputs).map(i => ({
          type: i.type,
          name: i.name,
          placeholder: i.placeholder,
          visible: i.offsetWidth > 0 && i.offsetHeight > 0
        }))
      };
    });
    console.log(`   Input elements found: ${inputs.count}`);
    if (inputs.count > 0) {
      inputs.types.forEach((inp, idx) => {
        console.log(`     Input ${idx + 1}: type=${inp.type}, name=${inp.name}, placeholder=${inp.placeholder}, visible=${inp.visible}`);
      });
    }
    
    // Step 7: Check for buttons
    console.log('\n📍 Step 7: Looking for buttons...');
    const buttons = await page.evaluate(() => {
      const allButtons = document.querySelectorAll('button');
      return {
        count: allButtons.length,
        texts: Array.from(allButtons).map(b => ({
          text: b.textContent?.trim().substring(0, 50),
          visible: b.offsetWidth > 0 && b.offsetHeight > 0,
          className: b.className
        }))
      };
    });
    console.log(`   Button elements found: ${buttons.count}`);
    if (buttons.count > 0) {
      buttons.texts.forEach((btn, idx) => {
        console.log(`     Button ${idx + 1}: text="${btn.text}", visible=${btn.visible}`);
      });
    }
    
    // Step 8: Check for any Arabic text (login page should have Arabic)
    console.log('\n📍 Step 8: Checking for Arabic text...');
    const hasArabic = await page.evaluate(() => {
      const text = document.body.textContent || '';
      const arabicRegex = /[\u0600-\u06FF]/;
      return {
        hasArabic: arabicRegex.test(text),
        textSample: text.substring(0, 200)
      };
    });
    console.log(`   Arabic text detected: ${hasArabic.hasArabic}`);
    if (hasArabic.hasArabic) {
      console.log(`   Text sample: ${hasArabic.textSample}`);
    }
    
    // Step 9: Check for canvas elements (Flutter uses canvas for rendering)
    console.log('\n📍 Step 9: Checking for canvas elements...');
    const canvasInfo = await page.evaluate(() => {
      const canvases = document.querySelectorAll('canvas');
      return {
        count: canvases.length,
        details: Array.from(canvases).map(c => ({
          width: c.width,
          height: c.height,
          visible: c.offsetWidth > 0 && c.offsetHeight > 0
        }))
      };
    });
    console.log(`   Canvas elements found: ${canvasInfo.count}`);
    if (canvasInfo.count > 0) {
      canvasInfo.details.forEach((canvas, idx) => {
        console.log(`     Canvas ${idx + 1}: ${canvas.width}x${canvas.height}, visible=${canvas.visible}`);
      });
    }
    
    // Step 10: Take diagnostic screenshot
    console.log('\n📍 Step 10: Taking diagnostic screenshots...');
    await page.screenshot({ 
      path: 'test-results/diagnostic-full-page.png', 
      fullPage: true 
    });
    console.log('   ✅ Full page screenshot saved');
    
    await page.screenshot({ 
      path: 'test-results/diagnostic-viewport.png', 
      fullPage: false 
    });
    console.log('   ✅ Viewport screenshot saved');
    
    // Step 11: Save HTML to file for inspection
    console.log('\n📍 Step 11: Saving HTML content...');
    const fullHTML = await page.content();
    const fs = require('fs');
    fs.writeFileSync('test-results/diagnostic-page.html', fullHTML);
    console.log(`   ✅ HTML saved (${fullHTML.length} characters)`);
    
    console.log('\n' + '='.repeat(60));
    console.log('🏁 Diagnostic Test Complete!');
    console.log('='.repeat(60));
  });

  test('should debug login process', async ({ page }) => {
    console.log('\n🚀 Starting Flutter App Login Test...\n');
    
    // Step 1: Navigate to Flutter app
    console.log('📍 Step 1: Navigating to Flutter app...');
    await page.goto(FLUTTER_APP_URL);
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'test-results/flutter-1-initial.png', fullPage: true });
    console.log('✅ Screenshot saved: flutter-1-initial.png');
    
    // Step 2: Wait for login form
    console.log('\n📍 Step 2: Waiting for login form...');
    await page.waitForTimeout(2000); // Wait for Flutter to fully load
    
    // Check for email input (try multiple selectors)
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"], input[placeholder*="البريد"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"], input[placeholder*="كلمة"]').first();
    const loginButton = await page.locator('button:has-text("تسجيل الدخول"), button:has-text("Login")').first();
    
    // Check if elements exist
    const emailExists = await emailInput.count() > 0;
    const passwordExists = await passwordInput.count() > 0;
    const buttonExists = await loginButton.count() > 0;
    
    console.log(`   Email input found: ${emailExists}`);
    console.log(`   Password input found: ${passwordExists}`);
    console.log(`   Login button found: ${buttonExists}`);
    
    if (!emailExists || !passwordExists || !buttonExists) {
      console.log('\n❌ Login form elements not found!');
      console.log('   Page HTML:', await page.content());
      return;
    }
    
    // Take screenshot of login form
    await page.screenshot({ path: 'test-results/flutter-2-login-form.png', fullPage: true });
    console.log('✅ Screenshot saved: flutter-2-login-form.png');
    
    // Step 3: Fill in credentials
    console.log('\n📍 Step 3: Filling in credentials...');
    await emailInput.fill('frati@tsh.sale');
    console.log('   Filled email: frati@tsh.sale');
    
    await passwordInput.fill('frati123');
    console.log('   Filled password: frati123');
    
    // Take screenshot after filling
    await page.screenshot({ path: 'test-results/flutter-3-filled.png', fullPage: true });
    console.log('✅ Screenshot saved: flutter-3-filled.png');
    
    // Step 4: Click login button
    console.log('\n📍 Step 4: Clicking login button...');
    
    // Wait for network response
    const responsePromise = page.waitForResponse(
      response => response.url().includes('login'),
      { timeout: 10000 }
    );
    
    await loginButton.click();
    console.log('   Clicked login button');
    
    // Wait for response
    try {
      const response = await responsePromise;
      console.log(`\n📥 Login Response Received:`);
      console.log(`   Status: ${response.status()}`);
      console.log(`   Status Text: ${response.statusText()}`);
      
      const responseBody = await response.text();
      console.log(`   Body: ${responseBody}`);
      
      // Try to parse as JSON
      try {
        const jsonBody = JSON.parse(responseBody);
        console.log('\n📊 Parsed Response:');
        console.log(JSON.stringify(jsonBody, null, 2));
      } catch (e) {
        console.log('   (Response is not JSON)');
      }
      
    } catch (e) {
      console.log(`\n❌ No login response received: ${e}`);
    }
    
    // Wait a bit for UI to update
    await page.waitForTimeout(2000);
    
    // Take screenshot after login attempt
    await page.screenshot({ path: 'test-results/flutter-4-after-login.png', fullPage: true });
    console.log('✅ Screenshot saved: flutter-4-after-login.png');
    
    // Step 5: Check for error messages
    console.log('\n📍 Step 5: Checking for error messages...');
    const errorMessage = await page.locator('text=/فشل|error|failed/i').first();
    const errorExists = await errorMessage.count() > 0;
    
    if (errorExists) {
      const errorText = await errorMessage.textContent();
      console.log(`   ❌ Error message found: "${errorText}"`);
    } else {
      console.log('   ✅ No error message found');
    }
    
    // Step 6: Check if redirected or logged in
    console.log('\n📍 Step 6: Checking login success...');
    const currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);
    
    // Check for success indicators
    const dashboardVisible = await page.locator('text=/dashboard|لوحة|home/i').count() > 0;
    const logoutVisible = await page.locator('text=/logout|تسجيل الخروج/i').count() > 0;
    
    console.log(`   Dashboard visible: ${dashboardVisible}`);
    console.log(`   Logout button visible: ${logoutVisible}`);
    
    // Step 7: Check local storage
    console.log('\n📍 Step 7: Checking local storage...');
    const localStorage = await page.evaluate(() => {
      return {
        token: localStorage.getItem('auth_token'),
        user: localStorage.getItem('user_data'),
        allKeys: Object.keys(localStorage)
      };
    });
    
    console.log(`   Token stored: ${localStorage.token ? 'YES' : 'NO'}`);
    console.log(`   User data stored: ${localStorage.user ? 'YES' : 'NO'}`);
    console.log(`   All keys: ${localStorage.allKeys.join(', ')}`);
    
    if (localStorage.token) {
      console.log(`   Token preview: ${localStorage.token.substring(0, 50)}...`);
    }
    
    if (localStorage.user) {
      try {
        const userData = JSON.parse(localStorage.user);
        console.log(`   User: ${JSON.stringify(userData, null, 2)}`);
      } catch (e) {
        console.log(`   User data (raw): ${localStorage.user}`);
      }
    }
    
    // Final screenshot
    await page.screenshot({ path: 'test-results/flutter-5-final.png', fullPage: true });
    console.log('\n✅ Screenshot saved: flutter-5-final.png');
    
    console.log('\n' + '='.repeat(60));
    console.log('🏁 Test Complete!');
    console.log('='.repeat(60));
  });

  test('should test backend API directly', async ({ request }) => {
    console.log('\n🔍 Testing Backend API Directly...\n');
    
    const response = await request.post(`${BACKEND_URL}/api/auth/login/mobile`, {
      headers: {
        'Content-Type': 'application/json',
      },
      data: {
        email: 'frati@tsh.sale',
        password: 'frati123',
      },
    });

    console.log(`📥 Direct API Test:`);
    console.log(`   Status: ${response.status()}`);
    console.log(`   Status Text: ${response.statusText()}`);
    
    const body = await response.text();
    console.log(`   Body: ${body}`);
    
    try {
      const jsonBody = JSON.parse(body);
      console.log('\n📊 Parsed Response:');
      console.log(JSON.stringify(jsonBody, null, 2));
      
      // Verify expected format
      console.log('\n✅ Response Validation:');
      console.log(`   Has access_token: ${!!jsonBody.access_token}`);
      console.log(`   Has user: ${!!jsonBody.user}`);
      console.log(`   Has user.id: ${!!jsonBody.user?.id}`);
      console.log(`   Has user.email: ${!!jsonBody.user?.email}`);
      console.log(`   Has user.role: ${!!jsonBody.user?.role}`);
      
    } catch (e) {
      console.log('   ❌ Response is not JSON');
    }
    
    console.log('\n' + '='.repeat(60));
  });
});
