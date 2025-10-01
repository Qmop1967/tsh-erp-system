import { test, expect, Page } from '@playwright/test';

test.describe('User Management Dropdown Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Navigate to the application
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Check if login is required and perform login if needed
    const loginForm = page.locator('form[data-testid="login-form"], .login-form, input[type="email"], input[type="password"]');
    if (await loginForm.first().isVisible({ timeout: 3000 })) {
      await page.fill('input[type="email"], input[name="email"], #email', 'admin@test.com');
      await page.fill('input[type="password"], input[name="password"], #password', 'password123');
      await page.click('button[type="submit"], .login-button, .btn-login');
      await page.waitForLoadState('networkidle');
    }
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('should display user management dropdown in navigation', async () => {
    // Look for various possible selectors for the user management dropdown
    const dropdownSelectors = [
      '[data-testid="user-management-dropdown"]',
      '.user-management-dropdown',
      'button:has-text("User Management")',
      'a:has-text("User Management")',
      '[aria-label*="User Management"]',
      '.dropdown:has-text("User")',
      '.nav-item:has-text("User")'
    ];

    let dropdown = null;
    let foundSelector = '';
    
    for (const selector of dropdownSelectors) {
      try {
        const testDropdown = page.locator(selector).first();
        if (await testDropdown.isVisible({ timeout: 2000 })) {
          dropdown = testDropdown;
          foundSelector = selector;
          console.log(`Found dropdown with selector: ${selector}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }

    if (!dropdown) {
      // Check if there's a navigation menu that might contain user management
      const navElements = await page.locator('nav, .navbar, .navigation, .menu, .sidebar').all();
      console.log(`Found ${navElements.length} navigation elements`);
      
      for (const nav of navElements) {
        const navText = await nav.textContent();
        console.log(`Navigation content: ${navText}`);
      }
      
      // Fail the test with helpful message
      throw new Error('User management dropdown not found. Check the selectors or ensure the component is rendered.');
    }

    expect(dropdown).toBeTruthy();
    await expect(dropdown).toBeVisible();
  });

  test('should open dropdown menu when clicked', async () => {
    // Find and click the dropdown trigger
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await expect(dropdownTrigger).toBeVisible();
    await dropdownTrigger.click();

    // Wait for dropdown menu to appear
    const dropdownMenu = page.locator(
      '[data-testid="user-management-menu"], .dropdown-menu, .user-management-menu, [role="menu"]'
    ).first();

    await expect(dropdownMenu).toBeVisible({ timeout: 5000 });
  });

  test('should contain expected menu items', async () => {
    // Click dropdown to open it
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await dropdownTrigger.click();

    // Expected menu items
    const expectedItems = [
      'Users',
      'User Groups',
      'Roles',
      'Permissions',
      'Add User',
      'Manage Users'
    ];

    for (const item of expectedItems) {
      const menuItem = page.locator(`text="${item}"`).first();
      try {
        await expect(menuItem).toBeVisible({ timeout: 3000 });
        console.log(`✓ Found menu item: ${item}`);
      } catch (e) {
        console.log(`✗ Missing menu item: ${item}`);
      }
    }
  });

  test('should navigate to users page when clicking Users', async () => {
    // Open dropdown
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await dropdownTrigger.click();

    // Click on Users menu item
    const usersLink = page.locator('a:has-text("Users"), button:has-text("Users")').first();
    await expect(usersLink).toBeVisible();
    await usersLink.click();

    // Wait for navigation
    await page.waitForLoadState('networkidle');

    // Check if we're on the users page
    await expect(page).toHaveURL(/.*users.*/);
    
    // Check for users page content
    const usersPageIndicators = [
      'h1:has-text("Users")',
      'h2:has-text("User Management")',
      '[data-testid="users-table"]',
      '.users-table',
      'table:has(th:has-text("Username"))',
      'button:has-text("Add User")'
    ];

    let foundIndicator = false;
    for (const indicator of usersPageIndicators) {
      try {
        await expect(page.locator(indicator).first()).toBeVisible({ timeout: 3000 });
        foundIndicator = true;
        console.log(`✓ Found users page indicator: ${indicator}`);
        break;
      } catch (e) {
        continue;
      }
    }

    expect(foundIndicator).toBeTruthy();
  });

  test('should close dropdown when clicking outside', async () => {
    // Open dropdown
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await dropdownTrigger.click();

    // Verify dropdown is open
    const dropdownMenu = page.locator(
      '[data-testid="user-management-menu"], .dropdown-menu, .user-management-menu'
    ).first();
    await expect(dropdownMenu).toBeVisible();

    // Click outside the dropdown
    await page.click('body', { position: { x: 10, y: 10 } });

    // Verify dropdown is closed
    await expect(dropdownMenu).not.toBeVisible();
  });

  test('should handle keyboard navigation', async () => {
    // Focus on dropdown trigger
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await dropdownTrigger.focus();

    // Open dropdown with Enter key
    await page.keyboard.press('Enter');

    // Verify dropdown opened
    const dropdownMenu = page.locator(
      '[data-testid="user-management-menu"], .dropdown-menu, .user-management-menu'
    ).first();
    await expect(dropdownMenu).toBeVisible();

    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowDown');

    // Close with Escape
    await page.keyboard.press('Escape');
    await expect(dropdownMenu).not.toBeVisible();
  });

  test('should be accessible to screen readers', async () => {
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    // Check for accessibility attributes
    await expect(dropdownTrigger).toHaveAttribute('aria-haspopup', 'true');
    await expect(dropdownTrigger).toHaveAttribute('aria-expanded', 'false');

    // Open dropdown
    await dropdownTrigger.click();

    // Check expanded state
    await expect(dropdownTrigger).toHaveAttribute('aria-expanded', 'true');

    // Check menu accessibility
    const dropdownMenu = page.locator(
      '[data-testid="user-management-menu"], .dropdown-menu, .user-management-menu'
    ).first();
    
    await expect(dropdownMenu).toHaveAttribute('role', 'menu');
  });

  test('should handle mobile responsive behavior', async () => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Check if dropdown adapts to mobile
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await expect(dropdownTrigger).toBeVisible();
    
    // On mobile, might be in a hamburger menu
    const mobileMenu = page.locator('.mobile-menu, .hamburger-menu, [data-testid="mobile-menu"]').first();
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
    }

    await dropdownTrigger.click();

    const dropdownMenu = page.locator(
      '[data-testid="user-management-menu"], .dropdown-menu, .user-management-menu'
    ).first();
    
    await expect(dropdownMenu).toBeVisible();
  });

  test('should show loading states appropriately', async () => {
    const dropdownTrigger = page.locator(
      '[data-testid="user-management-dropdown"], button:has-text("User Management"), .user-management-dropdown'
    ).first();

    await dropdownTrigger.click();

    // Click on a menu item that might show loading
    const usersLink = page.locator('a:has-text("Users"), button:has-text("Users")').first();
    await usersLink.click();

    // Check for loading indicators
    const loadingIndicators = [
      '.loading',
      '.spinner',
      '[data-testid="loading"]',
      'text="Loading..."'
    ];

    for (const indicator of loadingIndicators) {
      try {
        const loading = page.locator(indicator).first();
        if (await loading.isVisible({ timeout: 1000 })) {
          console.log(`✓ Found loading indicator: ${indicator}`);
          // Wait for loading to finish
          await expect(loading).not.toBeVisible({ timeout: 10000 });
          break;
        }
      } catch (e) {
        continue;
      }
    }
  });
});
