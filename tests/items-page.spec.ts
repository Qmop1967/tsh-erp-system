import { test, expect } from '@playwright/test';

test.describe('Items Page', () => {
  test('should navigate to items page and display items', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:5173');

    // Wait for the dashboard to load
    await page.waitForTimeout(1000);

    // Click on Inventory module to expand submenu
    await page.click('[data-testid="nav-inventory"]');

    // Wait for submenu to appear
    await page.waitForTimeout(500);

    // Click on Items submenu
    await page.click('[data-testid="submenu-items"]');

    // Wait for navigation
    await page.waitForTimeout(1000);

    // Verify we're on the items page
    await expect(page).toHaveURL(/.*inventory\/items/);

    // Check if the page title is present
    await expect(page.locator('h1:has-text("Inventory Items")')).toBeVisible();

    // Check if statistics cards are present
    await expect(page.locator('text=Total Items')).toBeVisible();
    await expect(page.locator('text=Active Items')).toBeVisible();
    await expect(page.locator('text=Total Value')).toBeVisible();

    // Check if search box is present
    await expect(page.locator('input[placeholder*="Search items"]')).toBeVisible();

    // Check if table headers are present
    await expect(page.locator('th:has-text("Code")')).toBeVisible();
    await expect(page.locator('th:has-text("Name (EN)")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();

    // Take a screenshot for verification
    await page.screenshot({ path: 'test-results/items-page.png', fullPage: true });
  });

  test('should handle items button click from inventory module', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:5173');

    // Wait for the dashboard to load
    await page.waitForTimeout(1000);

    // Click on Inventory module
    await page.click('[data-testid="nav-inventory"]');

    // Wait for submenu
    await page.waitForTimeout(500);

    // Verify Items link is visible
    await expect(page.locator('[data-testid="submenu-items"]')).toBeVisible();

    // Click Items
    await page.click('[data-testid="submenu-items"]');

    // Verify navigation worked
    await expect(page).toHaveURL(/.*inventory\/items/);

    // Verify items page loaded
    await expect(page.locator('h1:has-text("Inventory Items")')).toBeVisible();
  });
});