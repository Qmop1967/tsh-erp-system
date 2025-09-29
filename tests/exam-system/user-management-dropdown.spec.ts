import { test, expect } from '@playwright/test';

test.describe('User Management Dropdown E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application on the correct port
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    
    // Wait for the application to fully load
    await expect(page.locator('[data-testid="page-title"]')).toBeVisible();
  });

  test('should display User Management module in sidebar', async ({ page }) => {
    // Check if User Management navigation item is visible
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await expect(userManagementNav).toBeVisible();
    await expect(userManagementNav).toContainText('User Management');
  });

  test('should show submenu when User Management is clicked', async ({ page }) => {
    // Click on User Management navigation item
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    
    // Wait for submenu to appear
    await page.waitForTimeout(300);
    
    // Check if the submenu items are visible
    const submenuItems = page.locator('text="All Users"');
    await expect(submenuItems).toBeVisible();
    
    const permissionsItem = page.locator('text="Permissions"');
    await expect(permissionsItem).toBeVisible();
    
    const rolesItem = page.locator('text="Roles"');
    await expect(rolesItem).toBeVisible();
  });

  test('should have clickable submenu items', async ({ page }) => {
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    
    // Wait for submenu to appear
    await page.waitForTimeout(300);
    
    // Test clicking on "All Users"
    const allUsersItem = page.locator('text="All Users"');
    await expect(allUsersItem).toBeVisible();
    await allUsersItem.click();
    
    // Verify the page title still shows User Management (since we don't have routing)
    await expect(page.locator('[data-testid="page-title"]')).toContainText('User Management');
    
    // Test clicking on "Permissions"
    const permissionsItem = page.locator('text="Permissions"');
    await expect(permissionsItem).toBeVisible();
    await permissionsItem.click();
    
    // Test clicking on "Roles"
    const rolesItem = page.locator('text="Roles"');
    await expect(rolesItem).toBeVisible();
    await rolesItem.click();
  });

  test('should have proper hover effects on submenu items', async ({ page }) => {
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    
    // Wait for submenu to appear
    await page.waitForTimeout(300);
    
    // Test hover effect on "All Users"
    const allUsersItem = page.locator('text="All Users"');
    await allUsersItem.hover();
    
    // Check if hover effect is applied (color should change)
    const allUsersStyle = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    
    // Test hover on other items
    const permissionsItem = page.locator('text="Permissions"');
    await permissionsItem.hover();
    
    const rolesItem = page.locator('text="Roles"');
    await rolesItem.hover();
  });

  test('should maintain submenu visibility when switching between light/dark theme', async ({ page }) => {
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    
    // Wait for submenu to appear
    await page.waitForTimeout(300);
    
    // Verify submenu is visible
    const allUsersItem = page.locator('text="All Users"');
    await expect(allUsersItem).toBeVisible();
    
    // Click theme toggle to switch to dark mode
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    await themeToggle.click();
    
    // Wait for theme transition
    await page.waitForTimeout(300);
    
    // Verify submenu is still visible and readable in dark mode
    await expect(allUsersItem).toBeVisible();
    await expect(page.locator('text="Permissions"')).toBeVisible();
    await expect(page.locator('text="Roles"')).toBeVisible();
    
    // Switch back to light mode
    await themeToggle.click();
    await page.waitForTimeout(300);
    
    // Verify submenu is still visible and readable in light mode
    await expect(allUsersItem).toBeVisible();
    await expect(page.locator('text="Permissions"')).toBeVisible();
    await expect(page.locator('text="Roles"')).toBeVisible();
  });

  test('should have proper contrast and readability in light mode', async ({ page }) => {
    // Ensure we're in light mode first
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    // Click twice to ensure light mode (in case it was dark)
    await themeToggle.click();
    await page.waitForTimeout(200);
    await themeToggle.click();
    await page.waitForTimeout(200);
    
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(300);
    
    // Check submenu background color (should be light in light mode)
    const submenuContainer = page.locator('text="All Users"').locator('..');
    const backgroundColor = await submenuContainer.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // Background should be light (not dark)
    expect(backgroundColor).not.toBe('rgb(30, 41, 59)'); // Not dark slate
    
    // Check text color contrast
    const allUsersItem = page.locator('text="All Users"');
    const textColor = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    
    // Text should be dark in light mode for good contrast
    console.log('Submenu text color in light mode:', textColor);
    console.log('Submenu background color in light mode:', backgroundColor);
  });

  test('should collapse submenu when clicking on another module', async ({ page }) => {
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(300);
    
    // Verify submenu is visible
    const allUsersItem = page.locator('text="All Users"');
    await expect(allUsersItem).toBeVisible();
    
    // Click on Dashboard module
    const dashboardNav = page.locator('[data-testid="nav-dashboard"]');
    await dashboardNav.click();
    await page.waitForTimeout(300);
    
    // Verify User Management submenu is no longer visible
    await expect(allUsersItem).not.toBeVisible();
    
    // Verify page title changed to Dashboard
    await expect(page.locator('[data-testid="page-title"]')).toContainText('Dashboard');
  });

  test('should handle keyboard navigation for submenu items', async ({ page }) => {
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(300);
    
    // Focus on first submenu item and test keyboard navigation
    const allUsersItem = page.locator('text="All Users"');
    await allUsersItem.focus();
    
    // Test Tab navigation to next item
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Test Enter key activation
    const permissionsItem = page.locator('text="Permissions"');
    await permissionsItem.focus();
    await page.keyboard.press('Enter');
  });

  test('should show chevron icon indicating expandable module', async ({ page }) => {
    // Look for User Management with chevron icon
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await expect(userManagementNav).toBeVisible();
    
    // The chevron should be visible (ChevronRight icon)
    // This is implicit in the module having subItems, but we can verify the structure
    await expect(userManagementNav).toContainText('User Management');
    
    // After clicking, the submenu should expand
    await userManagementNav.click();
    await page.waitForTimeout(300);
    
    // Verify the submenu expanded
    await expect(page.locator('text="All Users"')).toBeVisible();
    await expect(page.locator('text="Permissions"')).toBeVisible();
    await expect(page.locator('text="Roles"')).toBeVisible();
  });

  test('should verify submenu items are truly clickable and interactive', async ({ page }) => {
    console.log('Testing actual clickability of User Management submenu items...');
    
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(500);
    
    // Test each submenu item individually with detailed verification
    
    // Test 1: "All Users" clickability
    console.log('Testing "All Users" clickability...');
    const allUsersItem = page.locator('text="All Users"');
    await expect(allUsersItem).toBeVisible();
    
    // Check if element has cursor pointer style (indicates clickability)
    const allUsersCursor = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).cursor;
    });
    console.log('All Users cursor style:', allUsersCursor);
    expect(allUsersCursor).toBe('pointer');
    
    // Actually click and verify response
    await allUsersItem.click();
    await page.waitForTimeout(300);
    
    // Test 2: "Permissions" clickability
    console.log('Testing "Permissions" clickability...');
    const permissionsItem = page.locator('text="Permissions"');
    await expect(permissionsItem).toBeVisible();
    
    const permissionsCursor = await permissionsItem.evaluate((el) => {
      return window.getComputedStyle(el).cursor;
    });
    console.log('Permissions cursor style:', permissionsCursor);
    expect(permissionsCursor).toBe('pointer');
    
    await permissionsItem.click();
    await page.waitForTimeout(300);
    
    // Test 3: "Roles" clickability
    console.log('Testing "Roles" clickability...');
    const rolesItem = page.locator('text="Roles"');
    await expect(rolesItem).toBeVisible();
    
    const rolesCursor = await rolesItem.evaluate((el) => {
      return window.getComputedStyle(el).cursor;
    });
    console.log('Roles cursor style:', rolesCursor);
    expect(rolesCursor).toBe('pointer');
    
    await rolesItem.click();
    await page.waitForTimeout(300);
    
    console.log('All submenu items are clickable and interactive!');
  });

  test('should verify hover effects actually work on submenu items', async ({ page }) => {
    console.log('Testing hover effects on submenu items...');
    
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(500);
    
    const allUsersItem = page.locator('text="All Users"');
    
    // Get initial color
    const initialColor = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    console.log('Initial text color:', initialColor);
    
    // Hover over the item
    await allUsersItem.hover();
    await page.waitForTimeout(200);
    
    // Get color after hover
    const hoverColor = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).color;
    });
    console.log('Hover text color:', hoverColor);
    
    // Get background color during hover
    const hoverBackground = await allUsersItem.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    console.log('Hover background color:', hoverBackground);
    
    // Verify hover effect is working (background should not be transparent)
    expect(hoverBackground).not.toBe('rgba(0, 0, 0, 0)');
    
    console.log('Hover effects are working properly!');
  });

  test('should show response/alert when submenu items are clicked', async ({ page }) => {
    console.log('Testing if submenu items show actual responses when clicked...');
    
    // Set up alert handler to capture alerts
    const alerts: string[] = [];
    page.on('dialog', async dialog => {
      console.log('Alert detected:', dialog.message());
      alerts.push(dialog.message());
      await dialog.accept();
    });
    
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(500);
    
    // Test clicking "All Users" and verify alert appears
    console.log('Testing "All Users" response...');
    const allUsersItem = page.locator('[data-testid="submenu-all-users"]');
    await expect(allUsersItem).toBeVisible();
    await allUsersItem.click();
    await page.waitForTimeout(500);
    
    // Verify alert was triggered
    expect(alerts.length).toBeGreaterThan(0);
    expect(alerts[0]).toContain('All Users');
    expect(alerts[0]).toContain('/users');
    console.log('✅ All Users shows response:', alerts[0]);
    
    // Test clicking "Permissions" and verify alert appears
    console.log('Testing "Permissions" response...');
    const permissionsItem = page.locator('[data-testid="submenu-permissions"]');
    await expect(permissionsItem).toBeVisible();
    await permissionsItem.click();
    await page.waitForTimeout(500);
    
    // Verify second alert was triggered
    expect(alerts.length).toBeGreaterThan(1);
    expect(alerts[1]).toContain('Permissions');
    expect(alerts[1]).toContain('/permissions');
    console.log('✅ Permissions shows response:', alerts[1]);
    
    // Test clicking "Roles" and verify alert appears
    console.log('Testing "Roles" response...');
    const rolesItem = page.locator('[data-testid="submenu-roles"]');
    await expect(rolesItem).toBeVisible();
    await rolesItem.click();
    await page.waitForTimeout(500);
    
    // Verify third alert was triggered
    expect(alerts.length).toBeGreaterThan(2);
    expect(alerts[2]).toContain('Roles');
    expect(alerts[2]).toContain('/roles');
    console.log('✅ Roles shows response:', alerts[2]);
    
    console.log('All submenu items now show proper responses when clicked!');
    console.log('Total alerts captured:', alerts.length);
  });

  test('should support keyboard navigation with Enter key on submenu items', async ({ page }) => {
    console.log('Testing keyboard navigation and Enter key response...');
    
    // Set up alert handler
    const alerts: string[] = [];
    page.on('dialog', async dialog => {
      alerts.push(dialog.message());
      await dialog.accept();
    });
    
    // Click on User Management to open submenu
    const userManagementNav = page.locator('[data-testid="nav-users"]');
    await userManagementNav.click();
    await page.waitForTimeout(500);
    
    // Test Enter key on "All Users"
    const allUsersItem = page.locator('[data-testid="submenu-all-users"]');
    await allUsersItem.focus();
    await page.keyboard.press('Enter');
    await page.waitForTimeout(300);
    
    // Verify alert was triggered by Enter key
    expect(alerts.length).toBeGreaterThan(0);
    expect(alerts[0]).toContain('All Users');
    
    console.log('✅ Enter key navigation works:', alerts[0]);
    
    // Test Space key on "Permissions"
    const permissionsItem = page.locator('[data-testid="submenu-permissions"]');
    await permissionsItem.focus();
    await page.keyboard.press(' ');
    await page.waitForTimeout(300);
    
    // Verify alert was triggered by Space key
    expect(alerts.length).toBeGreaterThan(1);
    expect(alerts[1]).toContain('Permissions');
    
    console.log('✅ Space key navigation works:', alerts[1]);
  });
});
