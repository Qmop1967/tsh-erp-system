import { test, expect } from '@playwright/test';

test.describe('Items Page Debugging', () => {
  test('should load items and display them correctly', async ({ page }) => {
    console.log('🧪 Starting Items Page Debug Test...');

    // Listen to console messages from the browser
    page.on('console', msg => {
      console.log(`🖥️  Browser Console [${msg.type()}]:`, msg.text());
    });

    // Listen to page errors
    page.on('pageerror', error => {
      console.log('❌ Page Error:', error.message);
    });

    // Listen to network requests
    page.on('request', request => {
      if (request.url().includes('/api/migration/items')) {
        console.log('🌐 API Request:', request.url());
      }
    });

    page.on('response', async response => {
      if (response.url().includes('/api/migration/items')) {
        console.log('📡 API Response Status:', response.status());
        try {
          const data = await response.json();
          console.log('📦 API Response Data:', Array.isArray(data) ? `Array with ${data.length} items` : typeof data);
          if (Array.isArray(data) && data.length > 0) {
            console.log('📄 First item:', JSON.stringify(data[0]).substring(0, 200));
          }
        } catch (e) {
          console.log('⚠️  Could not parse response as JSON');
        }
      }
    });

    // Navigate to items page
    console.log('📍 Navigating to items page...');
    await page.goto('http://localhost:5173/inventory/items');
    
    // Wait a bit for the page to load
    await page.waitForTimeout(2000);

    // Take screenshot of initial state
    await page.screenshot({ path: 'test-results/items-page-initial.png', fullPage: true });
    console.log('📸 Screenshot saved: items-page-initial.png');

    // Check page title
    const title = await page.textContent('h1');
    console.log('📝 Page Title:', title);

    // Check if loading state appears
    const loadingVisible = await page.locator('text=Loading inventory items').isVisible().catch(() => false);
    console.log('⏳ Loading indicator visible:', loadingVisible);

    // Wait for items to potentially load
    await page.waitForTimeout(3000);

    // Check debug info
    const debugInfo = await page.locator('text=Debug: Total items').textContent().catch(() => 'Not found');
    console.log('🔍 Debug Info:', debugInfo);

    // Check statistics cards
    const totalItems = await page.locator('text=Total Items').locator('..').locator('div.text-2xl').textContent().catch(() => '?');
    console.log('📊 Total Items shown:', totalItems);

    // Check if "No items found" message appears
    const noItemsMessage = await page.locator('text=No items found').isVisible().catch(() => false);
    console.log('🚫 No items message visible:', noItemsMessage);

    // Check if any item cards are visible
    const itemCards = await page.locator('[class*="grid"]').locator('[class*="bg-white"]').count();
    console.log('🗂️  Item cards found:', itemCards);

    // Get all text content from the page
    const pageText = await page.textContent('body');
    console.log('📄 Page contains "Total Items":', pageText?.includes('Total Items'));
    console.log('📄 Page contains "Active Items":', pageText?.includes('Active Items'));

    // Check local storage
    const localStorage = await page.evaluate(() => {
      return {
        token: window.localStorage.getItem('token') ? 'exists' : 'missing',
        keys: Object.keys(window.localStorage)
      };
    });
    console.log('💾 LocalStorage:', localStorage);

    // Try to directly call the API from the browser
    const apiTestResult = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/migration/items/?limit=5&active_only=false');
        const data = await response.json();
        return {
          success: true,
          status: response.status,
          itemCount: Array.isArray(data) ? data.length : 0,
          dataType: Array.isArray(data) ? 'array' : typeof data
        };
      } catch (error: any) {
        return {
          success: false,
          error: error.message
        };
      }
    });
    console.log('🧪 Direct API Test Result:', apiTestResult);

    // Take final screenshot
    await page.screenshot({ path: 'test-results/items-page-final.png', fullPage: true });
    console.log('📸 Screenshot saved: items-page-final.png');

    // Print summary
    console.log('\n📋 Test Summary:');
    console.log('  - Page loaded:', title?.includes('Inventory') ? '✅' : '❌');
    console.log('  - API accessible:', apiTestResult.success ? '✅' : '❌');
    console.log('  - Items loaded:', totalItems !== '0' ? '✅' : '❌');
    console.log('  - Item cards visible:', itemCards > 0 ? '✅' : '❌');
  });

  test('should test API endpoint directly', async ({ request }) => {
    console.log('\n🧪 Testing API Endpoint Directly...');
    
    const response = await request.get('http://localhost:8000/api/migration/items/?limit=5&active_only=false');
    const data = await response.json();
    
    console.log('📡 API Status:', response.status());
    console.log('📦 API Data Type:', Array.isArray(data) ? 'Array' : typeof data);
    console.log('📊 Items Count:', Array.isArray(data) ? data.length : 0);
    
    if (Array.isArray(data) && data.length > 0) {
      console.log('📄 First Item Keys:', Object.keys(data[0]));
      console.log('📄 First Item Sample:', {
        code: data[0].code,
        name_en: data[0].name_en,
        selling_price_usd: data[0].selling_price_usd
      });
    }
    
    expect(response.status()).toBe(200);
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThan(0);
  });
});
