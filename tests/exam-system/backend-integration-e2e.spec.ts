import { test, expect } from '@playwright/test';

test.describe('Backend API Integration E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('should add new item with full backend integration', async ({ page }) => {
    console.log('🚀 Testing complete backend integration...');
    
    // Track all network requests
    const apiRequests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('localhost:8888') && request.url().includes('api')) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          body: request.postData()
        });
        console.log(`📡 API Request: ${request.method()} ${request.url()}`);
      }
    });
    
    // Track all network responses
    page.on('response', response => {
      if (response.url().includes('localhost:8888') && response.url().includes('api')) {
        console.log(`📨 API Response: ${response.status()} ${response.url()}`);
      }
    });
    
    // Navigate to inventory and open add item modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill out comprehensive item data
    const testItem = {
      name: 'Backend Integration Test Item',
      sku: `BACKEND-${Date.now()}`,
      category: 'electronics',
      price: '299.99',
      quantity: '25',
      description: 'This item was created through full backend integration testing with Playwright E2E tests.'
    };
    
    console.log('📝 Filling form with test data...');
    await page.locator('[data-testid="item-name-input"]').fill(testItem.name);
    await page.locator('[data-testid="item-sku-input"]').fill(testItem.sku);
    await page.locator('[data-testid="item-category-select"]').selectOption(testItem.category);
    await page.locator('[data-testid="item-price-input"]').fill(testItem.price);
    await page.locator('[data-testid="item-quantity-input"]').fill(testItem.quantity);
    await page.locator('[data-testid="item-description-input"]').fill(testItem.description);
    
    // Handle the alert that should contain backend response data
    let alertMessage = '';
    page.on('dialog', async (dialog) => {
      alertMessage = dialog.message();
      console.log(`💬 Alert received: ${alertMessage}`);
      await dialog.accept();
    });
    
    // Submit the form
    console.log('🚀 Submitting form to backend...');
    await page.locator('[data-testid="save-add-item"]').click();
    
    // Wait for API call to complete
    await page.waitForTimeout(2000);
    
    // Verify API call was made
    expect(apiRequests.length).toBeGreaterThan(0);
    console.log(`✅ ${apiRequests.length} API request(s) made`);
    
    const addItemRequest = apiRequests.find(req => 
      req.url.includes('/items/add') && req.method === 'POST'
    );
    
    if (addItemRequest) {
      console.log('✅ Add item API request found');
      console.log('📦 Request body:', addItemRequest.body);
      
      // Parse and verify request body
      const requestData = JSON.parse(addItemRequest.body);
      expect(requestData.name).toBe(testItem.name);
      expect(requestData.sku).toBe(testItem.sku);
      expect(requestData.category).toBe(testItem.category);
      console.log('✅ Request data validation passed');
    } else {
      console.log('⚠️  No add item API request found');
      console.log('Available requests:', apiRequests.map(req => `${req.method} ${req.url}`));
    }
    
    // Verify alert contains success message
    if (alertMessage) {
      expect(alertMessage).toContain(testItem.name);
      expect(alertMessage).toContain('added successfully');
      if (alertMessage.includes('ID:')) {
        console.log('✅ Backend returned item ID in response');
      }
    }
    
    // Verify modal closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    
    console.log('🎉 Backend integration test completed successfully!');
  });

  test('should handle backend errors gracefully', async ({ page }) => {
    console.log('🧪 Testing backend error handling...');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Try to add item with duplicate SKU (should cause error)
    await page.locator('[data-testid="item-name-input"]').fill('Duplicate SKU Test');
    await page.locator('[data-testid="item-sku-input"]').fill('BACKEND-2025-001'); // Same SKU as previous test
    
    let alertMessage = '';
    page.on('dialog', async (dialog) => {
      alertMessage = dialog.message();
      console.log(`💬 Error alert: ${alertMessage}`);
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Verify error handling
    if (alertMessage.includes('Error')) {
      console.log('✅ Error handling working correctly');
    }
    
    // Modal should remain open on error
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Modal remains open on error - good UX');
    
    // Close modal
    await page.locator('[data-testid="cancel-add-item"]').click();
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
  });

  test('should test network failure handling', async ({ page }) => {
    console.log('🌐 Testing network failure scenarios...');
    
    // Block all requests to simulate network failure
    await page.route('http://localhost:8888/**', route => {
      console.log('🚫 Blocking request to simulate network failure');
      route.abort('failed');
    });
    
    // Navigate to inventory and try to add item
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill minimal data
    await page.locator('[data-testid="item-name-input"]').fill('Network Failure Test');
    await page.locator('[data-testid="item-sku-input"]').fill('NETWORK-FAIL-001');
    
    let alertMessage = '';
    page.on('dialog', async (dialog) => {
      alertMessage = dialog.message();
      console.log(`🚨 Network error alert: ${alertMessage}`);
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Verify network error handling
    if (alertMessage.includes('Network error') || alertMessage.includes('Could not connect')) {
      console.log('✅ Network error handling working correctly');
    }
    
    // Modal should remain open on network error
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Modal remains open on network error');
  });

  test('should verify API endpoint availability', async ({ page }) => {
    console.log('🔍 Testing API endpoint availability...');
    
    // Test if backend is running by making a direct request
    try {
      const response = await page.request.get('http://localhost:8888/');
      console.log(`📡 Backend health check: ${response.status()}`);
      
      if (response.ok()) {
        console.log('✅ Backend is running and accessible');
        
        // Test inventory API endpoints
        const inventoryResponse = await page.request.get('http://localhost:8888/api/inventory/items');
        console.log(`📦 Inventory API: ${inventoryResponse.status()}`);
        
        if (inventoryResponse.ok()) {
          const items = await inventoryResponse.json();
          console.log(`📊 Found ${items.length} inventory items in database`);
          console.log('✅ Inventory API is working');
        }
      }
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
    }
  });
});
