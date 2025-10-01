import { test, expect } from '@playwright/test';

test('Final screenshot of Items page with data', async ({ page }) => {
  // Navigate to the application
  await page.goto('http://localhost:5173');

  // Wait for the dashboard
  await page.waitForTimeout(2000);

  // Click Inventory
  await page.click('[data-testid="nav-inventory"]');
  await page.waitForTimeout(1000);

  // Click Items
  await page.click('[data-testid="submenu-items"]');

  // Wait for items to load
  await page.waitForTimeout(4000);

  // Wait for table to be visible
  await page.waitForSelector('table tbody tr', { timeout: 10000 });

  // Take screenshot
  await page.screenshot({
    path: 'test-results/items-page-with-data.png',
    fullPage: true
  });

  console.log('✅ Screenshot saved!');
});