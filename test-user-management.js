/**
 * Test User Management Module
 * Tests the TSH Access Management user management features
 */

const { chromium } = require('playwright');

async function testUserManagement() {
  console.log('🚀 Starting User Management Module Test...\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Step 1: Navigate to the application
    console.log('📍 Step 1: Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');

    // Take screenshot of login page
    await page.screenshot({ path: 'screenshots/01-login-page.png' });
    console.log('✅ Reached login page\n');

    // Step 2: Login
    console.log('📍 Step 2: Logging in with admin credentials');
    await page.fill('input[type="email"], input[name="email"]', 'admin@tsh.sale');
    await page.fill('input[type="password"], input[name="password"]', 'admin123');
    await page.screenshot({ path: 'screenshots/02-credentials-entered.png' });

    // Click login button
    await page.click('button[type="submit"], button:has-text("Sign in")');
    console.log('🔐 Login button clicked, waiting for navigation...');

    // Wait for navigation (with timeout handling)
    try {
      await page.waitForURL('**/dashboard**', { timeout: 10000 });
      console.log('✅ Successfully logged in\n');
    } catch (e) {
      console.log('⏳ Waiting for page to load...');
      await page.waitForTimeout(5000);
    }

    await page.screenshot({ path: 'screenshots/03-after-login.png' });

    // Step 3: Navigate to User Management
    console.log('📍 Step 3: Navigating to User Management');

    // Try different selectors for user management menu
    const userMenuSelectors = [
      'a:has-text("Users")',
      'a:has-text("User Management")',
      'a:has-text("المستخدمين")',
      '[href*="/users"]',
      'nav a:has-text("Users")'
    ];

    let clicked = false;
    for (const selector of userMenuSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          await element.click();
          clicked = true;
          console.log(`✅ Clicked user management menu: ${selector}`);
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }

    if (!clicked) {
      console.log('⚠️  Could not find user management menu, checking current page...');
    }

    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshots/04-user-management-page.png' });

    // Step 4: Analyze the User Management page
    console.log('\n📍 Step 4: Analyzing User Management Module\n');

    // Get page title
    const title = await page.title();
    console.log(`📄 Page Title: ${title}`);

    // Check for user table
    const hasTable = await page.$('table');
    console.log(`📊 User Table: ${hasTable ? '✅ Found' : '❌ Not found'}`);

    // Check for add user button
    const addButton = await page.$('button:has-text("Add"), button:has-text("Create"), button:has-text("New")');
    console.log(`➕ Add User Button: ${addButton ? '✅ Found' : '❌ Not found'}`);

    // Check for search functionality
    const searchInput = await page.$('input[type="search"], input[placeholder*="Search"], input[placeholder*="search"]');
    console.log(`🔍 Search Input: ${searchInput ? '✅ Found' : '❌ Not found'}`);

    // Get current URL
    const currentUrl = page.url();
    console.log(`🌐 Current URL: ${currentUrl}`);

    // Count visible users in the table
    const userRows = await page.$$('table tbody tr');
    console.log(`👥 Visible Users: ${userRows.length}`);

    // Get all visible text content
    const bodyText = await page.textContent('body');
    const hasUserContent = bodyText.includes('user') || bodyText.includes('User') || bodyText.includes('مستخدم');
    console.log(`📝 Page contains user-related content: ${hasUserContent ? '✅ Yes' : '❌ No'}`);

    // Final screenshot
    await page.screenshot({ path: 'screenshots/05-final-state.png', fullPage: true });

    console.log('\n✅ Test completed successfully!');
    console.log('📸 Screenshots saved to screenshots/ directory');

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
    await page.screenshot({ path: 'screenshots/error.png' });
  } finally {
    await browser.close();
  }
}

testUserManagement().catch(console.error);
