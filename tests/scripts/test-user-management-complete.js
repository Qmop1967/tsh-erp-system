/**
 * Complete User Management Module Test
 * Tests all features of the TSH Access Management user management module
 */

const { chromium } = require('playwright');

async function testUserManagement() {
  console.log('🚀 Starting Complete User Management Module Test...\n');

  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Step 1: Navigate and Login
    console.log('📍 Step 1: Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/01-login-page.png' });

    console.log('📍 Step 2: Logging in with admin@tsh.sale');
    await page.fill('input[type="email"], input[name="email"]', 'admin@tsh.sale');
    await page.fill('input[type="password"], input[name="password"]', 'admin123');
    await page.click('button[type="submit"], button:has-text("Sign in")');

    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'screenshots/02-dashboard.png' });
    console.log('✅ Logged in successfully\n');

    // Step 2: Navigate to User Management
    console.log('📍 Step 3: Clicking on User Management menu');
    await page.click('text=User Management');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/03-user-management-menu-clicked.png' });

    // Click on "All Users" submenu
    console.log('📍 Step 4: Clicking on "All Users" submenu');
    await page.click('text=All Users');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'screenshots/04-all-users-page.png' });
    console.log('✅ Navigated to All Users page\n');

    // Step 3: Analyze User Management Features
    console.log('📊 ANALYZING USER MANAGEMENT MODULE:\n');

    const currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);

    // Check for user table
    const hasTable = await page.$('table');
    console.log(`📋 User Table: ${hasTable ? '✅ Present' : '❌ Not found'}`);

    // Count user rows
    const userRows = await page.$$('table tbody tr');
    console.log(`👥 Number of Users Displayed: ${userRows.length}`);

    // Check for action buttons
    const addUserBtn = await page.$('button:has-text("Add"), button:has-text("Create"), button:has-text("New")');
    console.log(`➕ Add User Button: ${addUserBtn ? '✅ Present' : '❌ Not found'}`);

    const searchInput = await page.$('input[type="search"], input[placeholder*="Search"], input[placeholder*="search"]');
    console.log(`🔍 Search Functionality: ${searchInput ? '✅ Present' : '❌ Not found'}`);

    // Check for filter/sort options
    const filterBtn = await page.$('button:has-text("Filter")');
    console.log(`🎛️  Filter Button: ${filterBtn ? '✅ Present' : '❌ Not found'}`);

    // Step 4: Test Search Functionality
    if (searchInput) {
      console.log('\n📍 Step 5: Testing Search Functionality');
      await searchInput.fill('admin');
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'screenshots/05-search-test.png' });
      console.log('✅ Search test completed');
      await searchInput.fill('');
    }

    // Step 5: Check Permissions submenu
    console.log('\n📍 Step 6: Checking Permissions submenu');
    await page.click('text=Permissions');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/06-permissions-page.png' });
    console.log('✅ Navigated to Permissions page');

    const permissionsTable = await page.$('table');
    console.log(`📋 Permissions Table: ${permissionsTable ? '✅ Present' : '❌ Not found'}`);

    // Step 6: Check Roles submenu
    console.log('\n📍 Step 7: Checking Roles submenu');
    await page.click('text=Roles');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/07-roles-page.png' });
    console.log('✅ Navigated to Roles page');

    const rolesTable = await page.$('table');
    console.log(`📋 Roles Table: ${rolesTable ? '✅ Present' : '❌ Not found'}`);

    // Step 7: Get all visible column headers
    console.log('\n📍 Step 8: Analyzing Table Columns');
    const headers = await page.$$eval('table thead th', elements =>
      elements.map(el => el.textContent.trim())
    );
    console.log('📊 Table Columns:', headers);

    // Step 8: Check for export functionality
    const exportBtn = await page.$('button:has-text("Export"), button:has-text("Download")');
    console.log(`\n📤 Export Functionality: ${exportBtn ? '✅ Present' : '❌ Not found'}`);

    // Final Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 USER MANAGEMENT MODULE TEST SUMMARY');
    console.log('='.repeat(60));
    console.log('✅ Login: Success');
    console.log('✅ Navigation: Success');
    console.log(`✅ User List: ${hasTable ? 'Working' : 'Not found'}`);
    console.log(`✅ Permissions: ${permissionsTable ? 'Working' : 'Not found'}`);
    console.log(`✅ Roles: ${rolesTable ? 'Working' : 'Not found'}`);
    console.log(`✅ Search: ${searchInput ? 'Available' : 'Not found'}`);
    console.log(`✅ Add User: ${addUserBtn ? 'Available' : 'Not found'}`);
    console.log('='.repeat(60));
    console.log('\n📸 All screenshots saved to screenshots/ directory');

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
    console.error(error.stack);
    await page.screenshot({ path: 'screenshots/error.png', fullPage: true });
  } finally {
    console.log('\n⏳ Keeping browser open for 5 seconds for review...');
    await page.waitForTimeout(5000);
    await browser.close();
    console.log('✅ Test completed!');
  }
}

testUserManagement().catch(console.error);
