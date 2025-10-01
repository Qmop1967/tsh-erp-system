import { test, expect } from '@playwright/test';

test('Take screenshot of Items page', async ({ page }) => {
  // Navigate to the application
  await page.goto('http://localhost:5173');

  // Wait for the dashboard to load
  await page.waitForTimeout(2000);

  // Click on Inventory module to expand submenu
  await page.click('[data-testid="nav-inventory"]');

  // Wait for submenu to appear
  await page.waitForTimeout(1000);

  // Click on Items submenu
  await page.click('[data-testid="submenu-items"]');

  // Wait for the items page to fully load
  await page.waitForTimeout(3000);

  // Wait for the table or content to be visible
  await page.waitForSelector('h1:has-text("Inventory Items")', { timeout: 10000 });

  // Take a full page screenshot
  await page.screenshot({
    path: 'test-results/items-page-full.png',
    fullPage: true
  });

  console.log('✅ Screenshot saved to test-results/items-page-full.png');
});