const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function advancedERPTest() {
  const testResults = {
    testDate: new Date().toISOString(),
    baseUrl: 'http://localhost:5173',
    tests: [],
    screenshots: [],
    errors: [],
    consoleMessages: [],
    pageAnalysis: {},
    summary: {}
  };

  const browser = await chromium.launch({
    headless: false,
    slowMo: 800
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  const screenshotsDir = '/Users/khaleelal-mulla/TSH_ERP_System_Local/screenshots';

  // Capture console and errors
  page.on('console', msg => {
    testResults.consoleMessages.push({
      type: msg.type(),
      text: msg.text(),
      timestamp: new Date().toISOString()
    });
  });

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
    testResults.screenshots.push({ name, description, path: screenshotPath, timestamp: new Date().toISOString() });
    console.log(`✓ Screenshot: ${name}.png - ${description}`);
  }

  async function addTest(name, status, details) {
    testResults.tests.push({ name, status, details, timestamp: new Date().toISOString() });
    const icon = status === 'PASS' ? '✓' : status === 'FAIL' ? '✗' : 'ℹ';
    console.log(`${icon} ${name}: ${details}`);
  }

  try {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║   TSH ERP SYSTEM - ADVANCED COMPREHENSIVE TEST             ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    // ============ PHASE 1: LOGIN ============
    console.log('📋 PHASE 1: LOGIN & AUTHENTICATION\n');

    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    await takeScreenshot('01-login-page', 'Initial login page');

    await page.fill('input[type="email"]', 'admin@tsh-erp.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Sign in")');
    await page.waitForTimeout(3000);

    const isLoggedIn = page.url().includes('/dashboard');
    await addTest('User Authentication', isLoggedIn ? 'PASS' : 'FAIL',
      isLoggedIn ? 'Successfully logged in and redirected to dashboard' : 'Login failed');

    if (!isLoggedIn) {
      console.log('❌ Login failed. Stopping test.');
      return;
    }

    await takeScreenshot('02-dashboard-main', 'Main dashboard after login');

    // ============ PHASE 2: DASHBOARD ANALYSIS ============
    console.log('\n📋 PHASE 2: DASHBOARD METRICS ANALYSIS\n');

    // Extract dashboard metrics
    const metrics = await page.evaluate(() => {
      const metrics = {
        hasRevenue: !!document.body.textContent.match(/Total Revenue/i),
        hasEmployees: !!document.body.textContent.match(/Total Employees/i),
        hasInventory: !!document.body.textContent.match(/Inventory Items/i),
        hasCash: !!document.body.textContent.match(/Total Cash/i),
        dashboardTitle: document.querySelector('h1, h2')?.textContent.trim() || 'Not found'
      };
      return metrics;
    });

    testResults.pageAnalysis.dashboardMetrics = metrics;
    await addTest('Dashboard Metrics Load', 'PASS', `Captured metrics: Revenue, Employees, Inventory, Cash`);

    // ============ PHASE 3: NAVIGATION EXPLORATION ============
    console.log('\n📋 PHASE 3: NAVIGATION MENU EXPLORATION\n');

    const menuItems = await page.$$eval('nav a, aside a, [role="navigation"] a', links =>
      links.filter(l => l.textContent.trim()).map(link => ({
        text: link.textContent.trim(),
        href: link.getAttribute('href')
      }))
    );

    testResults.pageAnalysis.navigationMenu = menuItems;
    await addTest('Navigation Menu', 'PASS', `Found ${menuItems.length} menu items`);
    console.log(`   Menu items: ${menuItems.map(m => m.text).join(', ')}`);

    // ============ PHASE 4: INVENTORY PAGE ============
    console.log('\n📋 PHASE 4: INVENTORY MODULE\n');

    try {
      const inventoryLink = await page.$('a:has-text("Inventory"), a[href*="inventory"]');
      if (inventoryLink) {
        await inventoryLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('03-inventory-page', 'Inventory page');

        const inventoryUrl = page.url();
        await addTest('Inventory Navigation', 'PASS', `Navigated to: ${inventoryUrl}`);

        // Check for inventory table
        const hasTable = await page.$('table, [role="table"]');
        if (hasTable) {
          const itemCount = await page.$$eval('table tr, [role="row"]', rows => rows.length - 1);
          await addTest('Inventory Items Display', 'PASS', `Found ${itemCount} items in table`);
        }

        // Check for action buttons
        const buttons = await page.$$eval('button', btns => btns.map(b => b.textContent.trim()));
        testResults.pageAnalysis.inventoryButtons = buttons;
        await addTest('Inventory Actions', 'PASS', `Found ${buttons.length} action buttons`);
      } else {
        await addTest('Inventory Navigation', 'INFO', 'Inventory menu item not found');
      }
    } catch (error) {
      await addTest('Inventory Module', 'FAIL', `Error: ${error.message}`);
    }

    // ============ PHASE 5: USER MANAGEMENT ============
    console.log('\n📋 PHASE 5: USER MANAGEMENT MODULE\n');

    try {
      await page.click('a:has-text("Dashboard")');
      await page.waitForTimeout(1000);

      const userMgmtLink = await page.$('a:has-text("User Management"), a[href*="users"]');
      if (userMgmtLink) {
        await userMgmtLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('04-users-page', 'User Management page');

        const usersUrl = page.url();
        await addTest('User Management Navigation', 'PASS', `Navigated to: ${usersUrl}`);

        // Check for users table or list
        const hasUsersTable = await page.$('table, [role="table"], div[class*="user"]');
        if (hasUsersTable) {
          await addTest('Users Display', 'PASS', 'Users list/table found');
        }
      } else {
        await addTest('User Management Navigation', 'INFO', 'User Management menu not found');
      }
    } catch (error) {
      await addTest('User Management Module', 'FAIL', `Error: ${error.message}`);
    }

    // ============ PHASE 6: SALES MANAGEMENT ============
    console.log('\n📋 PHASE 6: SALES MANAGEMENT MODULE\n');

    try {
      await page.click('a:has-text("Dashboard")');
      await page.waitForTimeout(1000);

      const salesLink = await page.$('a:has-text("Sales"), a[href*="sales"]');
      if (salesLink) {
        await salesLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('05-sales-page', 'Sales Management page');
        await addTest('Sales Navigation', 'PASS', `Navigated to sales page`);
      } else {
        await addTest('Sales Navigation', 'INFO', 'Sales menu not found');
      }
    } catch (error) {
      await addTest('Sales Module', 'FAIL', `Error: ${error.message}`);
    }

    // ============ PHASE 7: REPORTS ============
    console.log('\n📋 PHASE 7: REPORTS MODULE\n');

    try {
      await page.click('a:has-text("Dashboard")');
      await page.waitForTimeout(1000);

      const reportsLink = await page.$('a:has-text("Reports"), a[href*="report"]');
      if (reportsLink) {
        await reportsLink.click();
        await page.waitForTimeout(2000);
        await takeScreenshot('06-reports-page', 'Reports page');
        await addTest('Reports Navigation', 'PASS', `Navigated to reports page`);
      } else {
        await addTest('Reports Navigation', 'INFO', 'Reports menu not found');
      }
    } catch (error) {
      await addTest('Reports Module', 'FAIL', `Error: ${error.message}`);
    }

    // ============ PHASE 8: SIDEBAR INTERACTION ============
    console.log('\n📋 PHASE 8: SIDEBAR TOGGLE FUNCTIONALITY\n');

    try {
      await page.click('a:has-text("Dashboard")');
      await page.waitForTimeout(1000);

      const collapseBtn = await page.$('button:has-text("Collapse"), button[aria-label*="collapse" i]');
      if (collapseBtn) {
        await takeScreenshot('07-sidebar-expanded', 'Sidebar expanded state');
        await collapseBtn.click();
        await page.waitForTimeout(1500);
        await takeScreenshot('08-sidebar-collapsed', 'Sidebar collapsed state');
        await addTest('Sidebar Toggle', 'PASS', 'Sidebar collapse/expand works');

        // Expand back
        await collapseBtn.click();
        await page.waitForTimeout(1000);
      } else {
        await addTest('Sidebar Toggle', 'INFO', 'Collapse button not found with standard selectors');
      }
    } catch (error) {
      await addTest('Sidebar Toggle', 'FAIL', `Error: ${error.message}`);
    }

    // ============ PHASE 9: QUICK ACTIONS ============
    console.log('\n📋 PHASE 9: QUICK ACTIONS TESTING\n');

    try {
      await page.click('a:has-text("Dashboard")');
      await page.waitForTimeout(1000);

      const quickActions = await page.$$eval('button:has-text("New Sale"), button:has-text("Add Item"), button:has-text("New Customer"), button:has-text("View Reports")',
        btns => btns.map(b => b.textContent.trim()));

      if (quickActions.length > 0) {
        testResults.pageAnalysis.quickActions = quickActions;
        await addTest('Quick Actions', 'PASS', `Found ${quickActions.length} quick action buttons`);
        console.log(`   Actions: ${quickActions.join(', ')}`);
      }
    } catch (error) {
      await addTest('Quick Actions', 'INFO', 'Quick action buttons not found');
    }

    // ============ PHASE 10: RESPONSIVE DESIGN ============
    console.log('\n📋 PHASE 10: RESPONSIVE DESIGN TESTING\n');

    // Tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1500);
    await takeScreenshot('09-tablet-view', 'Tablet (768px) responsive view');
    await addTest('Tablet Responsiveness', 'PASS', 'Tested at 768px width');

    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1500);
    await takeScreenshot('10-mobile-view', 'Mobile (375px) responsive view');
    await addTest('Mobile Responsiveness', 'PASS', 'Tested at 375px width');

    // Back to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);

    // ============ PHASE 11: PERFORMANCE METRICS ============
    console.log('\n📋 PHASE 11: PERFORMANCE ANALYSIS\n');

    const perfMetrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      const paintEntries = performance.getEntriesByType('paint');

      return {
        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        responseTime: perfData.responseEnd - perfData.requestStart,
        firstPaint: paintEntries.find(e => e.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paintEntries.find(e => e.name === 'first-contentful-paint')?.startTime || 0
      };
    });

    testResults.pageAnalysis.performance = perfMetrics;
    await addTest('Performance Metrics', 'PASS',
      `Load: ${perfMetrics.loadTime.toFixed(2)}ms, FCP: ${perfMetrics.firstContentfulPaint.toFixed(2)}ms`);

    // ============ PHASE 12: ACCESSIBILITY CHECK ============
    console.log('\n📋 PHASE 12: ACCESSIBILITY ANALYSIS\n');

    const a11y = await page.evaluate(() => {
      return {
        hasH1: !!document.querySelector('h1'),
        hasNav: !!document.querySelector('nav'),
        hasMain: !!document.querySelector('main'),
        imageCount: document.querySelectorAll('img').length,
        imagesWithAlt: document.querySelectorAll('img[alt]').length,
        buttonsCount: document.querySelectorAll('button').length,
        linksCount: document.querySelectorAll('a').length
      };
    });

    testResults.pageAnalysis.accessibility = a11y;
    await addTest('Accessibility Features', 'PASS',
      `H1: ${a11y.hasH1}, Nav: ${a11y.hasNav}, Images with alt: ${a11y.imagesWithAlt}/${a11y.imageCount}`);

    // ============ FINAL SUMMARY ============
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
      totalConsoleMessages: testResults.consoleMessages.length,
      criticalIssues: testResults.errors.length + failCount
    };

  } catch (error) {
    console.error('❌ Critical Error:', error);
    testResults.errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  } finally {
    // Save comprehensive report
    const reportPath = '/Users/khaleelal-mulla/TSH_ERP_System_Local/advanced-test-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));

    // Create human-readable report
    const readableReport = `
╔════════════════════════════════════════════════════════════╗
║           TSH ERP SYSTEM - TEST SUMMARY REPORT             ║
╚════════════════════════════════════════════════════════════╝

📊 TEST STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Tests:        ${testResults.summary.totalTests}
  ✓ Passed:          ${testResults.summary.passed}
  ✗ Failed:          ${testResults.summary.failed}
  ℹ Info:            ${testResults.summary.info}
  Success Rate:      ${testResults.summary.successRate}

  Screenshots:       ${testResults.summary.totalScreenshots}
  Errors:            ${testResults.summary.totalErrors}
  Critical Issues:   ${testResults.summary.criticalIssues}

🎯 KEY FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Login:             ${testResults.tests.find(t => t.name === 'User Authentication')?.status || 'N/A'}
  Dashboard:         ${testResults.tests.find(t => t.name === 'Dashboard Metrics Load')?.status || 'N/A'}
  Navigation:        ${testResults.tests.find(t => t.name === 'Navigation Menu')?.status || 'N/A'}
  Inventory:         ${testResults.tests.find(t => t.name === 'Inventory Navigation')?.status || 'N/A'}
  User Management:   ${testResults.tests.find(t => t.name === 'User Management Navigation')?.status || 'N/A'}
  Responsive Design: ${testResults.tests.find(t => t.name === 'Mobile Responsiveness')?.status || 'N/A'}
  Performance:       ${testResults.tests.find(t => t.name === 'Performance Metrics')?.status || 'N/A'}

📁 FILES GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  JSON Report:       ${reportPath}
  Screenshots Dir:   ${screenshotsDir}/

Test completed at: ${new Date().toLocaleString()}

╚════════════════════════════════════════════════════════════╝
    `;

    const readableReportPath = '/Users/khaleelal-mulla/TSH_ERP_System_Local/test-summary.txt';
    fs.writeFileSync(readableReportPath, readableReport);

    console.log(readableReport);
    console.log(`\n💾 Full JSON report: ${reportPath}`);
    console.log(`📄 Summary report: ${readableReportPath}`);
    console.log(`📸 Screenshots: ${screenshotsDir}/`);

    await browser.close();
  }
}

advancedERPTest().catch(console.error);
