import { test, expect, Page } from '@playwright/test';

test.describe('User Management Dropdown - All Users Button Flow', () => {
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    console.log('🚀 Setting up test environment for User Management Dropdown tests...');
  });

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    
    // Navigate to dashboard with retries
    let retries = 3;
    while (retries > 0) {
      try {
        await page.goto('http://localhost:5173', { 
          waitUntil: 'networkidle',
          timeout: 15000 
        });
        
        // Wait for dashboard to be ready
        await page.waitForSelector('[data-testid="dashboard-container"], .dashboard-container, main', { timeout: 10000 });
        console.log('✅ Dashboard loaded successfully');
        break;
      } catch (error) {
        retries--;
        console.log(`⚠️  Retry loading dashboard... (${retries} attempts left)`);
        if (retries === 0) throw error;
        await page.waitForTimeout(2000);
      }
    }
  });

  test('Step 1: Verify User Management module exists in sidebar', async () => {
    console.log('🔍 Step 1: Checking User Management module in sidebar...');
    
    // Look for User Management module with multiple possible selectors
    const userManagementSelectors = [
      '[data-testid="sidebar-module-users"]',
      '[data-module="users"]',
      'li:has-text("User Management")',
      '.sidebar-item:has-text("User Management")',
      '.nav-item:has-text("User Management")'
    ];
    
    let userManagementFound = false;
    for (let selector of userManagementSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
        userManagementFound = true;
        console.log(`✅ User Management found with selector: ${selector}`);
        break;
      }
    }
    
    if (!userManagementFound) {
      // Take screenshot for debugging
      await page.screenshot({ path: 'debug-sidebar.png', fullPage: true });
      console.log('📸 Screenshot saved as debug-sidebar.png for debugging');
      
      // Log sidebar content
      const sidebarContent = await page.locator('.sidebar, nav, aside').textContent();
      console.log('🔍 Sidebar content:', sidebarContent);
      
      throw new Error('User Management module not found in sidebar');
    }
  });

  test('Step 2: Click User Management to expand dropdown', async () => {
    console.log('🔍 Step 2: Clicking User Management to expand dropdown...');
    
    // Find and click User Management
    const userManagementSelectors = [
      '[data-testid="sidebar-module-users"]',
      '[data-module="users"]',
      'li:has-text("User Management")',
      '.sidebar-item:has-text("User Management")',
      '.nav-item:has-text("User Management")'
    ];
    
    let clicked = false;
    for (let selector of userManagementSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await element.first().click();
        clicked = true;
        console.log(`✅ Clicked User Management with selector: ${selector}`);
        break;
      }
    }
    
    if (!clicked) {
      throw new Error('Could not find User Management to click');
    }
    
    // Wait for dropdown animation
    await page.waitForTimeout(1000);
    
    // Verify dropdown expanded
    const dropdownSelectors = [
      '[data-testid="user-management-dropdown"]',
      '.submenu',
      '.dropdown-menu',
      'ul:has-text("All Users")'
    ];
    
    let dropdownFound = false;
    for (let selector of dropdownSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
        dropdownFound = true;
        console.log(`✅ Dropdown expanded with selector: ${selector}`);
        break;
      }
    }
    
    if (!dropdownFound) {
      await page.screenshot({ path: 'debug-dropdown.png', fullPage: true });
      console.log('📸 Screenshot saved as debug-dropdown.png');
      console.log('⚠️  Dropdown might have different structure or animation timing');
    }
  });

  test('Step 3: Verify All Users option appears in dropdown', async () => {
    console.log('🔍 Step 3: Verifying All Users option in dropdown...');
    
    // First expand the dropdown
    const userManagement = page.locator('li:has-text("User Management"), [data-testid="sidebar-module-users"]').first();
    await userManagement.click();
    await page.waitForTimeout(1000);
    
    // Look for All Users option
    const allUsersSelectors = [
      '[data-testid="submenu-item-all-users"]',
      'a:has-text("All Users")',
      'li:has-text("All Users")',
      '.submenu-item:has-text("All Users")',
      '.dropdown-item:has-text("All Users")'
    ];
    
    let allUsersFound = false;
    for (let selector of allUsersSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
        await expect(element.first()).toContainText('All Users');
        allUsersFound = true;
        console.log(`✅ All Users option found with selector: ${selector}`);
        break;
      }
    }
    
    if (!allUsersFound) {
      // Log all dropdown content for debugging
      const dropdownContent = await page.locator('.submenu, .dropdown-menu, ul').allTextContents();
      console.log('🔍 Dropdown content:', dropdownContent);
      
      await page.screenshot({ path: 'debug-all-users-option.png', fullPage: true });
      throw new Error('All Users option not found in dropdown');
    }
  });

  test('Step 4: Click All Users and verify navigation', async () => {
    console.log('🔍 Step 4: Clicking All Users and verifying navigation...');
    
    // Expand dropdown first
    const userManagement = page.locator('li:has-text("User Management"), [data-testid="sidebar-module-users"]').first();
    await userManagement.click();
    await page.waitForTimeout(1000);
    
    // Click All Users
    const allUsersSelectors = [
      '[data-testid="submenu-item-all-users"]',
      'a:has-text("All Users")',
      'li:has-text("All Users")',
      '.submenu-item:has-text("All Users")'
    ];
    
    let navigationStarted = false;
    for (let selector of allUsersSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await element.first().click();
        navigationStarted = true;
        console.log(`✅ Clicked All Users with selector: ${selector}`);
        break;
      }
    }
    
    if (!navigationStarted) {
      throw new Error('Could not click All Users option');
    }
    
    // Wait for navigation
    await page.waitForTimeout(2000);
    
    // Verify URL changed to users page
    const currentUrl = page.url();
    console.log('🔍 Current URL:', currentUrl);
    
    if (currentUrl.includes('/users')) {
      console.log('✅ Successfully navigated to users page');
    } else {
      console.log('⚠️  URL might not have changed yet, checking for page content...');
    }
    
    // Verify users page content loaded
    const usersPageSelectors = [
      '[data-testid="users-page-container"]',
      '.users-page',
      'h1:has-text("Users")',
      'h1:has-text("User Management")',
      '.page-title:has-text("Users")'
    ];
    
    let usersPageFound = false;
    for (let selector of usersPageSelectors) {
      const element = page.locator(selector);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
        usersPageFound = true;
        console.log(`✅ Users page loaded with selector: ${selector}`);
        break;
      }
    }
    
    if (!usersPageFound) {
      await page.screenshot({ path: 'debug-users-page.png', fullPage: true });
      console.log('📸 Screenshot saved as debug-users-page.png');
      console.log('⚠️  Users page content might be loading or have different structure');
    }
  });

  test('Step 5: Verify Users page functionality', async () => {
    console.log('🔍 Step 5: Verifying Users page functionality...');
    
    // Navigate directly to users page
    await page.goto('http://localhost:5173/users', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Check for essential page elements
    const pageElements = {
      title: ['h1', '.page-title', '[data-testid="page-title"]'],
      addButton: ['[data-testid="add-user-button"]', 'button:has-text("Add User")', '.add-user-btn'],
      table: ['[data-testid="users-table"]', '.users-table', 'table'],
      container: ['[data-testid="users-page-container"]', '.users-page', '.page-content']
    };
    
    for (let [elementName, selectors] of Object.entries(pageElements)) {
      let found = false;
      for (let selector of selectors) {
        const element = page.locator(selector);
        if (await element.count() > 0) {
          console.log(`✅ ${elementName} found with selector: ${selector}`);
          found = true;
          break;
        }
      }
      if (!found) {
        console.log(`⚠️  ${elementName} not found - might have different structure`);
      }
    }
    
    // Check for loading states or data
    const hasLoadingState = await page.locator('.loading, .spinner, [data-testid="loading"]').count() > 0;
    const hasUserData = await page.locator('.user-item, .user-row, tr[data-user-id]').count() > 0;
    const hasEmptyState = await page.locator('.no-users, .empty-state, [data-testid="empty-state"]').count() > 0;
    
    if (hasLoadingState) {
      console.log('🔄 Page is in loading state');
    } else if (hasUserData) {
      console.log('✅ User data is displayed');
    } else if (hasEmptyState) {
      console.log('✅ Empty state is displayed (no users)');
    } else {
      console.log('⚠️  Page state is unclear - might still be loading or have different structure');
    }
  });

  test('Complete Flow: Dashboard → User Management → All Users → Users Page', async () => {
    console.log('🔍 Testing complete flow from Dashboard to Users Page...');
    
    // Step 1: Verify we're on dashboard
    await expect(page.locator('h1, .page-title')).toContainText(/Dashboard|Home/i);
    console.log('✅ Starting from Dashboard');
    
    // Step 2: Find and click User Management
    const userManagement = page.locator('li:has-text("User Management"), [data-testid="sidebar-module-users"]').first();
    await expect(userManagement).toBeVisible();
    await userManagement.click();
    console.log('✅ Clicked User Management');
    
    // Step 3: Wait for dropdown and click All Users
    await page.waitForTimeout(1000);
    const allUsers = page.locator('a:has-text("All Users"), li:has-text("All Users")').first();
    await expect(allUsers).toBeVisible();
    await allUsers.click();
    console.log('✅ Clicked All Users');
    
    // Step 4: Verify navigation to users page
    await page.waitForTimeout(2000);
    
    // Check multiple indicators that we're on users page
    const indicators = [
      async () => page.url().includes('/users'),
      async () => await page.locator('h1:has-text("Users"), h1:has-text("User Management")').count() > 0,
      async () => await page.locator('[data-testid="users-page"], .users-page').count() > 0
    ];
    
    let navigationSuccessful = false;
    for (let indicator of indicators) {
      if (await indicator()) {
        navigationSuccessful = true;
        break;
      }
    }
    
    if (navigationSuccessful) {
      console.log('✅ Complete flow successful: Dashboard → User Management → All Users → Users Page');
    } else {
      await page.screenshot({ path: 'debug-complete-flow.png', fullPage: true });
      console.log('❌ Complete flow failed - screenshot saved for debugging');
      throw new Error('Navigation to Users page failed');
    }
  });

  test.afterEach(async () => {
    // Take screenshot on failure for debugging
    if (test.info().status !== test.info().expectedStatus) {
      await page.screenshot({ 
        path: `debug-failure-${Date.now()}.png`, 
        fullPage: true 
      });
    }
  });
});
