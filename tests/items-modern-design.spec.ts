import { test, expect } from '@playwright/test';

test('Modern Items page screenshot', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);

  await page.click('[data-testid="nav-inventory"]');
  await page.waitForTimeout(1000);

  await page.click('[data-testid="submenu-items"]');
  await page.waitForTimeout(4000);

  await page.waitForSelector('table tbody tr', { timeout: 10000 });

  // Take List View screenshot
  await page.screenshot({
    path: 'test-results/items-modern-list-view.png',
    fullPage: true
  });

  console.log('✅ List view screenshot saved!');

  // Switch to Grid View
  await page.click('button:has-text("Grid")');
  await page.waitForTimeout(1000);

  // Take Grid View screenshot
  await page.screenshot({
    path: 'test-results/items-modern-grid-view.png',
    fullPage: true
  });

  console.log('✅ Grid view screenshot saved!');
});