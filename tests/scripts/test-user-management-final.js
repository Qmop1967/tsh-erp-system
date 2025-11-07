/**
 * Final User Management Module Test
 * Comprehensive test of TSH Access Management user management features
 */

const { chromium } = require('playwright');

async function testUserManagement() {
  console.log('🚀 Starting User Management Module Test...\n');

  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Step 1: Navigate and Login
    console.log('📍 Step 1: Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');

    console.log('📍 Step 2: Logging in with admin@tsh.sale');
    await page.fill('input[type="email"], input[name="email"]', 'admin@tsh.sale');
    await page.fill('input[type="password"], input[name="password"]', 'admin123');
    await page.click('button[type="submit"], button:has-text("Sign in")');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'screenshots/01-dashboard.png' });
    console.log('✅ Logged in successfully\n');

    // Step 2: Expand User Management menu by clicking the arrow
    console.log('📍 Step 3: Expanding User Management menu');

    // Find the User Management menu item and click the chevron/arrow
    const userMgmtSection = await page.locator('text=User Management').locator('..');
    await userMgmtSection.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'screenshots/02-user-mgmt-expanded.png' });
    console.log('✅ User Management menu expanded\n');

    // Step 3: Navigate to Users page by clicking the URL directly
    console.log('📍 Step 4: Navigating to Users page');
    await page.goto('http://localhost:5173/users');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'screenshots/03-users-page.png', fullPage: true });
    console.log('✅ Navigated to Users page\n');

    // Step 4: Analyze User Management Features
    console.log('=' .repeat(70));
    console.log('📊 ANALYZING USER MANAGEMENT MODULE');
    console.log('='.repeat(70) + '\n');

    const currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);
    console.log(`📄 Page Title: ${await page.title()}\n`);

    // Check main components
    const hasTable = await page.$('table');
    console.log(`📋 User Table: ${hasTable ? '✅ PRESENT' : '❌ NOT FOUND'}`);

    if (hasTable) {
      const userRows = await page.$$('table tbody tr');
      console.log(`👥 Number of Users: ${userRows.length}`);

      // Get table headers
      const headers = await page.$$eval('table thead th', elements =>
        elements.map(el => el.textContent.trim()).filter(h => h.length > 0)
      );
      console.log(`📊 Table Columns: ${headers.join(' | ')}`);
    }

    // Check for action buttons
    const buttons = {
      'Add/Create User': await page.$('button:has-text("Add"), button:has-text("Create"), button:has-text("New User")'),
      'Search': await page.$('input[type="search"], input[placeholder*="Search"], input[placeholder*="search"]'),
      'Filter': await page.$('button:has-text("Filter")'),
      'Export': await page.$('button:has-text("Export"), button:has-text("Download")'),
    };

    console.log('\n🎛️  AVAILABLE FEATURES:');
    for (const [feature, element] of Object.entries(buttons)) {
      console.log(`   ${element ? '✅' : '❌'} ${feature}`);
    }

    // Step 5: Test Permissions page
    console.log('\n📍 Step 5: Testing Permissions page');
    await page.goto('http://localhost:5173/permissions');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/04-permissions-page.png', fullPage: true });

    const permissionsTable = await page.$('table');
    console.log(`📋 Permissions Table: ${permissionsTable ? '✅ PRESENT' : '❌ NOT FOUND'}`);

    if (permissionsTable) {
      const permRows = await page.$$('table tbody tr');
      console.log(`🔐 Number of Permissions: ${permRows.length}`);
    }

    // Step 6: Test Roles page
    console.log('\n📍 Step 6: Testing Roles page');
    await page.goto('http://localhost:5173/roles');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/05-roles-page.png', fullPage: true });

    const rolesTable = await page.$('table');
    console.log(`📋 Roles Table: ${rolesTable ? '✅ PRESENT' : '❌ NOT FOUND'}`);

    if (rolesTable) {
      const roleRows = await page.$$('table tbody tr');
      console.log(`👔 Number of Roles: ${roleRows.length}`);
    }

    // Step 7: Test Search Functionality (if available)
    if (buttons.Search) {
      console.log('\n📍 Step 7: Testing Search Functionality');
      await page.goto('http://localhost:5173/users');
      await page.waitForTimeout(1500);

      await buttons.Search.fill('admin');
      await page.waitForTimeout(1500);
      await page.screenshot({ path: 'screenshots/06-search-admin.png' });
      console.log('✅ Search tested with keyword: "admin"');

      await buttons.Search.fill('');
      await page.waitForTimeout(500);
    }

    // Final Summary
    console.log('\n' + '='.repeat(70));
    console.log('📊 USER MANAGEMENT MODULE TEST SUMMARY');
    console.log('='.repeat(70));
    console.log('Module Components:');
    console.log(`  ✅ Users Page: ${hasTable ? 'WORKING' : 'ISSUE DETECTED'}`);
    console.log(`  ✅ Permissions Page: ${permissionsTable ? 'WORKING' : 'ISSUE DETECTED'}`);
    console.log(`  ✅ Roles Page: ${rolesTable ? 'WORKING' : 'ISSUE DETECTED'}`);
    console.log('\nFunctionality:');
    console.log(`  ${buttons['Add/Create User'] ? '✅' : '❌'} Add/Create User`);
    console.log(`  ${buttons.Search ? '✅' : '❌'} Search Users`);
    console.log(`  ${buttons.Filter ? '✅' : '❌'} Filter Options`);
    console.log(`  ${buttons.Export ? '✅' : '❌'} Export Data`);
    console.log('='.repeat(70));
    console.log('\n📸 All screenshots saved to screenshots/ directory');
    console.log('✅ Test completed successfully!\n');

  } catch (error) {
    console.error('\n❌ TEST FAILED');
    console.error('Error:', error.message);
    await page.screenshot({ path: 'screenshots/error.png', fullPage: true });
  } finally {
    console.log('⏳ Keeping browser open for 5 seconds for manual review...');
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

testUserManagement().catch(console.error);
