import { test, expect } from '@playwright/test';

test('Test direct URL navigation', async ({ page }) => {
  console.log('🔍 Testing direct URL: http://localhost:5173/inventory/items');

  // Navigate directly to the items URL
  await page.goto('http://localhost:5173/inventory/items');

  // Wait for page to load
  await page.waitForTimeout(3000);

  // Check if we're on the items page
  const title = await page.locator('h1').textContent();
  console.log('📄 Page title:', title);

  // Check URL
  const currentUrl = page.url();
  console.log('🌐 Current URL:', currentUrl);

  // Take screenshot
  await page.screenshot({
    path: 'test-results/direct-url-test.png',
    fullPage: true
  });
  console.log('📸 Screenshot saved');

  // Verify items page loaded
  await expect(page.locator('h1:has-text("Inventory Items")')).toBeVisible({ timeout: 5000 });

  console.log('✅ Direct URL navigation works!');
});