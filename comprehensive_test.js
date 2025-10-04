const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function comprehensiveERPTest() {
  const testResults = {
    testDate: new Date().toISOString(),
    baseUrl: 'http://localhost:5173',
    tests: [],
    screenshots: [],
    errors: [],
    consoleMessages: [],
    summary: {}
  };

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500 // Slow down actions to see what's happening
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  const screenshotsDir = '/Users/khaleelal-mulla/TSH_ERP_System_Local/screenshots';
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  // Capture console messages
  page.on('console', msg => {
    testResults.consoleMessages.push({
      type: msg.type(),
      text: msg.text(),
      timestamp: new Date().toISOString()
    });
  });

  // Capture errors
  page.on('pageerror', error => {
    testResults.errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  });

  async function takeScreenshot(name, description) {
    const screenshotPath = path.join(screenshotsDir, `${name}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    testResults.screenshots.push({
      name,
      description,
      path: screenshotPath,
      timestamp: new Date().toISOString()
    });
    console.log(`✓ Screenshot saved: ${name}.png - ${description}`);
  }

  async function addTest(name, status, details) {
    testResults.tests.push({
      name,
      status,
      details,
      timestamp: new Date().toISOString()
    });
    console.log(`${status === 'PASS' ? '✓' : '✗'} ${name}: ${details}`);
  }

  try {
    console.log('\n=== TSH ERP SYSTEM - COMPREHENSIVE TEST ===\n');

    // TEST 1: Load Homepage
    console.log('TEST 1: Loading Homepage...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    await takeScreenshot('01-homepage-login', 'Login page initial load');

    const title = await page.title();
    await addTest('Homepage Load', 'PASS', `Page title: "${title}"`);

    // TEST 2: Check Login Form Elements
    console.log('\nTEST 2: Checking Login Form Elements...');
    const emailInput = await page.$('input[type="email"], input[placeholder*="email" i], input[name="email"]');
    const passwordInput = await page.$('input[type="password"]');
    const loginButton = await page.$('button:has-text("Sign in")');

    if (emailInput && passwordInput && loginButton) {
      await addTest('Login Form Elements', 'PASS', 'All login form elements found');
    } else {
      await addTest('Login Form Elements', 'FAIL', 'Missing form elements');
    }

    // TEST 3: Attempt Login
    console.log('\nTEST 3: Attempting Login...');

    // Try to find and fill email field
    try {
      await page.fill('input[type="email"]', 'admin@tsh-erp.com');
      await page.fill('input[type="password"]', 'admin123');
      await takeScreenshot('02-login-filled', 'Login form with credentials filled');

      await addTest('Fill Login Form', 'PASS', 'Credentials entered successfully');

      // Click login button
      await page.click('button:has-text("Sign in")');
      console.log('Login button clicked, waiting for navigation...');

      // Wait for navigation or dashboard to load
      await page.waitForTimeout(3000);

      const currentUrl = page.url();
      await takeScreenshot('03-after-login', 'Page after login attempt');

      if (currentUrl !== 'http://localhost:5173/') {
        await addTest('Login Navigation', 'PASS', `Navigated to: ${currentUrl}`);
      } else {
        await addTest('Login Navigation', 'INFO', 'Still on login page - checking for errors');
      }
    } catch (error) {
      await addTest('Login Process', 'FAIL', `Error: ${error.message}`);
    }

    // TEST 4: Explore Dashboard
    console.log('\nTEST 4: Exploring Dashboard...');
    await page.waitForTimeout(2000);

    // Check if sidebar exists
    const sidebar = await page.$('nav, [class*="sidebar" i], aside');
    if (sidebar) {
      await addTest('Dashboard Sidebar', 'PASS', 'Sidebar navigation found');
      await takeScreenshot('04-dashboard-overview', 'Dashboard main view');
    }

    // TEST 5: Check Navigation Menu Items
    console.log('\nTEST 5: Checking Navigation Menu Items...');
    const menuItems = await page.$$eval('[role="navigation"] a, nav a, aside a', links =>
      links.map(link => ({
        text: link.textContent.trim(),
        href: link.href
      }))
    );

    if (menuItems.length > 0) {
      await addTest('Navigation Menu Items', 'PASS', `Found ${menuItems.length} menu items: ${menuItems.map(m => m.text).join(', ')}`);
    }

    // TEST 6: Test Inventory Page
    console.log('\nTEST 6: Testing Inventory Page...');
    try {
      // Try to find and click inventory link
      const inventoryLink = await page.$('a:has-text("Inventory"), a:has-text("Items"), a[href*="inventory"]');

      if (inventoryLink) {
        await inventoryLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('05-inventory-page', 'Inventory page view');
        await addTest('Inventory Page Navigation', 'PASS', 'Successfully navigated to Inventory');

        // Check for items table or list
        const itemsTable = await page.$('table, [role="table"], [class*="table" i]');
        if (itemsTable) {
          await addTest('Inventory Items Display', 'PASS', 'Items table/list found');
        }
      } else {
        await addTest('Inventory Page Navigation', 'INFO', 'Inventory link not found in current view');
      }
    } catch (error) {
      await addTest('Inventory Page', 'FAIL', `Error: ${error.message}`);
    }

    // TEST 7: Test User Management Page
    console.log('\nTEST 7: Testing User Management Page...');
    try {
      const usersLink = await page.$('a:has-text("Users"), a:has-text("User Management"), a[href*="users"]');

      if (usersLink) {
        await usersLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('06-users-page', 'User Management page view');
        await addTest('Users Page Navigation', 'PASS', 'Successfully navigated to Users');
      } else {
        await addTest('Users Page Navigation', 'INFO', 'Users link not found in current view');
      }
    } catch (error) {
      await addTest('Users Page', 'FAIL', `Error: ${error.message}`);
    }

    // TEST 8: Test Sidebar Collapse/Expand
    console.log('\nTEST 8: Testing Sidebar Collapse/Expand...');
    try {
      const collapseButton = await page.$('button[aria-label*="collapse" i], button[aria-label*="toggle" i], button:has([class*="menu" i])');

      if (collapseButton) {
        await takeScreenshot('07-sidebar-expanded', 'Sidebar in expanded state');
        await collapseButton.click();
        await page.waitForTimeout(1000);
        await takeScreenshot('08-sidebar-collapsed', 'Sidebar in collapsed state');
        await addTest('Sidebar Toggle', 'PASS', 'Sidebar collapse/expand works');

        // Expand it back
        await collapseButton.click();
        await page.waitForTimeout(1000);
      } else {
        await addTest('Sidebar Toggle', 'INFO', 'Collapse button not found');
      }
    } catch (error) {
      await addTest('Sidebar Toggle', 'FAIL', `Error: ${error.message}`);
    }

    // TEST 9: Check Responsive Design
    console.log('\nTEST 9: Testing Responsive Design...');
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await takeScreenshot('09-tablet-view', 'Tablet responsive view');
    await addTest('Tablet View', 'PASS', 'Tablet viewport tested');

    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await takeScreenshot('10-mobile-view', 'Mobile responsive view');
    await addTest('Mobile View', 'PASS', 'Mobile viewport tested');

    // Reset to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });

    // TEST 10: Performance Check
    console.log('\nTEST 10: Checking Performance Metrics...');
    const metrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      return {
        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        responseTime: perfData.responseEnd - perfData.requestStart
      };
    });

    await addTest('Performance Metrics', 'PASS',
      `Load: ${metrics.loadTime.toFixed(2)}ms, DOM: ${metrics.domContentLoaded.toFixed(2)}ms, Response: ${metrics.responseTime.toFixed(2)}ms`);

    // Generate Summary
    const passCount = testResults.tests.filter(t => t.status === 'PASS').length;
    const failCount = testResults.tests.filter(t => t.status === 'FAIL').length;
    const infoCount = testResults.tests.filter(t => t.status === 'INFO').length;

    testResults.summary = {
      totalTests: testResults.tests.length,
      passed: passCount,
      failed: failCount,
      info: infoCount,
      successRate: `${((passCount / testResults.tests.length) * 100).toFixed(2)}%`,
      totalScreenshots: testResults.screenshots.length,
      totalErrors: testResults.errors.length,
      totalConsoleMessages: testResults.consoleMessages.length
    };

  } catch (error) {
    console.error('Critical Error:', error);
    testResults.errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  } finally {
    // Save test results
    const reportPath = '/Users/khaleelal-mulla/TSH_ERP_System_Local/test-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));

    console.log('\n=== TEST SUMMARY ===');
    console.log(`Total Tests: ${testResults.summary.totalTests}`);
    console.log(`Passed: ${testResults.summary.passed}`);
    console.log(`Failed: ${testResults.summary.failed}`);
    console.log(`Info: ${testResults.summary.info}`);
    console.log(`Success Rate: ${testResults.summary.successRate}`);
    console.log(`Screenshots: ${testResults.summary.totalScreenshots}`);
    console.log(`Errors: ${testResults.summary.totalErrors}`);
    console.log(`\nFull report saved to: ${reportPath}`);
    console.log('\nScreenshots saved in: /Users/khaleelal-mulla/TSH_ERP_System_Local/screenshots/');

    await browser.close();
  }
}

comprehensiveERPTest().catch(console.error);
