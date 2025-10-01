import { test, expect } from '@playwright/test';

test('Items page with authentication', async ({ page, context }) => {
  // Set up demo authentication in localStorage before navigation
  await context.addInitScript(() => {
    localStorage.setItem('tsh-erp-auth', JSON.stringify({
      state: {
        token: 'demo-token-123',
        user: {
          id: 1,
          name: 'Demo User',
          email: 'demo@tsh.sale',
          role: 'Admin'
        }
      }
    }));
  });

  // Navigate to the application
  await page.goto('http://localhost:5173');

  // Wait for the dashboard to load
  await page.waitForTimeout(2000);

  // Click on Inventory module
  await page.click('[data-testid="nav-inventory"]');

  // Wait for submenu
  await page.waitForTimeout(1000);

  // Click on Items
  await page.click('[data-testid="submenu-items"]');

  // Wait for the items page to fully load
  await page.waitForTimeout(3000);

  // Wait for items to load
  await page.waitForSelector('h1:has-text("Inventory Items")', { timeout: 10000 });

  // Take a full page screenshot
  await page.screenshot({
    path: 'test-results/items-page-authenticated.png',
    fullPage: true
  });

  console.log('✅ Screenshot saved to test-results/items-page-authenticated.png');

  // Log what we see
  const tableContent = await page.textContent('table');
  console.log('Table content preview:', tableContent?.substring(0, 200));
});