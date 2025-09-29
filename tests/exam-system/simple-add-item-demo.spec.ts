import { test, expect } from '@playwright/test';

test.describe('Simple Add Item Demo', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('should demonstrate complete add new item functionality', async ({ page }) => {
    console.log('🚀 Starting Add New Item Demo...');
    
    // Step 1: Navigate to inventory module
    console.log('📋 Step 1: Navigate to Inventory');
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    // Verify we're on the inventory page
    await expect(page.locator('[data-testid="page-title"]')).toContainText('Inventory');
    console.log('✅ Successfully navigated to Inventory module');
    
    // Step 2: Click Add New Item button
    console.log('🆕 Step 2: Click Add New Item button');
    const addButton = page.getByText('Add New Item');
    await expect(addButton).toBeVisible();
    await addButton.click();
    await page.waitForTimeout(500);
    
    // Verify modal opened
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Add Item modal opened successfully');
    
    // Step 3: Fill out the form with unique data
    console.log('📝 Step 3: Fill out the item form');
    const uniqueId = Date.now();
    const testItem = {
      name: `Demo Item ${uniqueId}`,
      sku: `DEMO-${uniqueId}`,
      category: 'electronics',
      price: '49.99',
      quantity: '10',
      description: `This is a demo item created on ${new Date().toLocaleString()}`
    };
    
    await page.locator('[data-testid="item-name-input"]').fill(testItem.name);
    await page.locator('[data-testid="item-sku-input"]').fill(testItem.sku);
    await page.locator('[data-testid="item-category-select"]').selectOption(testItem.category);
    await page.locator('[data-testid="item-price-input"]').fill(testItem.price);
    await page.locator('[data-testid="item-quantity-input"]').fill(testItem.quantity);
    await page.locator('[data-testid="item-description-input"]').fill(testItem.description);
    
    console.log(`✅ Form filled with: ${testItem.name} (${testItem.sku})`);
    
    // Step 4: Handle the success alert
    console.log('💾 Step 4: Submit the form');
    page.on('dialog', async (dialog) => {
      const message = dialog.message();
      console.log(`📨 Alert received: ${message}`);
      expect(message).toContain(testItem.name);
      expect(message).toContain('added successfully');
      await dialog.accept();
    });
    
    // Submit the form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Step 5: Verify modal closed
    console.log('🔒 Step 5: Verify modal closed after success');
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Modal closed successfully');
    
    // Step 6: Take a final screenshot
    console.log('📸 Step 6: Taking final screenshot');
    await page.screenshot({ 
      path: `test-results/add-item-demo-success-${uniqueId}.png`,
      fullPage: true 
    });
    
    console.log('🎉 Add New Item Demo completed successfully!');
    console.log(`📊 Created item: ${testItem.name} with SKU: ${testItem.sku}`);
  });
  
  test('should test modal cancel functionality', async ({ page }) => {
    console.log('❌ Testing modal cancel functionality');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill some test data
    await page.locator('[data-testid="item-name-input"]').fill('Test Cancel Item');
    await page.locator('[data-testid="item-sku-input"]').fill(`CANCEL-${Date.now()}`);
    
    // Click cancel
    await page.locator('[data-testid="cancel-add-item"]').click();
    await page.waitForTimeout(200);
    
    // Verify modal closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Cancel functionality working correctly');
  });
  
  test('should test all form fields', async ({ page }) => {
    console.log('📋 Testing all form fields');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Test all form fields
    const formFields = [
      { testId: 'item-name-input', value: 'Field Test Item', type: 'text' },
      { testId: 'item-sku-input', value: `FIELD-${Date.now()}`, type: 'text' },
      { testId: 'item-price-input', value: '99.99', type: 'number' },
      { testId: 'item-quantity-input', value: '5', type: 'number' },
      { testId: 'item-description-input', value: 'Testing all form fields', type: 'text' }
    ];
    
    for (const field of formFields) {
      console.log(`Testing field: ${field.testId}`);
      const input = page.locator(`[data-testid="${field.testId}"]`);
      
      // Test input and validation
      await input.fill(field.value);
      await expect(input).toHaveValue(field.value);
      
      console.log(`✅ ${field.testId} working correctly`);
    }
    
    // Test category dropdown
    const categorySelect = page.locator('[data-testid="item-category-select"]');
    await categorySelect.selectOption('furniture');
    await expect(categorySelect).toHaveValue('furniture');
    console.log('✅ Category dropdown working correctly');
    
    // Close modal
    await page.locator('[data-testid="cancel-add-item"]').click();
    console.log('✅ All form fields test completed');
  });
});
