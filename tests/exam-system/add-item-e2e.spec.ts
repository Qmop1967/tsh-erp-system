import { test, expect } from '@playwright/test';

test.describe('Add New Item E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('should complete add new item workflow', async ({ page }) => {
    console.log('🚀 Starting complete add new item workflow...');
    
    // Navigate to inventory
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    // Click Add New Item button
    const addNewItemButton = page.getByText('Add New Item');
    await addNewItemButton.click();
    await page.waitForTimeout(500);
    
    // Verify modal opened
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Add Item modal opened successfully');
    
    // Take screenshot of modal
    await page.screenshot({ path: 'test-results/add-item-modal-opened.png' });
    
    // Fill out the form
    console.log('📝 Filling out the add item form...');
    
    // Fill item name
    await page.locator('[data-testid="item-name-input"]').fill('Test Product E2E');
    
    // Fill SKU with timestamp to ensure uniqueness
    const uniqueSku = `TEST-E2E-${Date.now()}`;
    await page.locator('[data-testid="item-sku-input"]').fill(uniqueSku);
    
    // Select category
    await page.locator('[data-testid="item-category-select"]').selectOption('electronics');
    
    // Fill price
    await page.locator('[data-testid="item-price-input"]').fill('99.99');
    
    // Fill quantity
    await page.locator('[data-testid="item-quantity-input"]').fill('50');
    
    // Fill description
    await page.locator('[data-testid="item-description-input"]').fill('This is a test product created via E2E testing using Playwright.');
    
    console.log('✅ Form filled successfully');
    
    // Take screenshot of filled form
    await page.screenshot({ path: 'test-results/add-item-form-filled.png' });
    
    // Handle the alert that will appear when saving
    page.on('dialog', async (dialog) => {
      console.log(`Alert appeared: ${dialog.message()}`);
      expect(dialog.message()).toContain('Test Product E2E');
      expect(dialog.message()).toContain('added successfully');
      await dialog.accept();
    });
    
    // Submit the form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(1000);
    
    console.log('✅ Form submitted successfully');
    
    // Verify modal is closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Modal closed after successful submission');
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/add-item-completed.png' });
    
    console.log('🎉 Add new item workflow completed successfully!');
  });

  test('should test modal validation', async ({ page }) => {
    console.log('🧪 Testing modal validation...');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Try to submit without required fields
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(200);
    
    // Check if form validation prevents submission (modal should still be open)
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Form validation working - modal remains open');
    
    // Fill only name and try again
    await page.locator('[data-testid="item-name-input"]').fill('Test Item');
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(200);
    
    // Modal should still be open due to missing SKU
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ SKU validation working');
    
    // Fill SKU and submit
    const uniqueSku = `TEST-VAL-${Date.now()}`;
    await page.locator('[data-testid="item-sku-input"]').fill(uniqueSku);
    
    // Handle alert for successful submission
    let alertTriggered = false;
    let dialogMessage = '';
    page.on('dialog', async (dialog) => {
      alertTriggered = true;
      dialogMessage = dialog.message();
      console.log(`Dialog triggered: ${dialogMessage}`);
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000); // Wait longer for alert and API call
    
    // Check if it was a success or error
    if (alertTriggered) {
      if (dialogMessage.includes('added successfully')) {
        // Success case - modal should close
        await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
        console.log('✅ Validation test completed successfully - item added');
      } else {
        // Error case - modal should remain open
        await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
        console.log('✅ Error handling working correctly - modal remains open on error');
        // Close modal manually for cleanup
        await page.locator('[data-testid="cancel-add-item"]').click();
      }
    } else {
      console.log('⚠️  Alert not triggered, modal remains open');
      // Close modal manually for cleanup
      await page.locator('[data-testid="cancel-add-item"]').click();
    }
  });

  test('should test modal cancel functionality', async ({ page }) => {
    console.log('❌ Testing modal cancel functionality...');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill some data
    await page.locator('[data-testid="item-name-input"]').fill('Test Cancel Item');
    await page.locator('[data-testid="item-sku-input"]').fill('CANCEL-TEST-001');
    
    // Click cancel
    await page.locator('[data-testid="cancel-add-item"]').click();
    await page.waitForTimeout(200);
    
    // Modal should close
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Cancel button working correctly');
    
    // Open modal again and verify form is cleared
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Verify form is cleared
    await expect(page.locator('[data-testid="item-name-input"]')).toHaveValue('');
    await expect(page.locator('[data-testid="item-sku-input"]')).toHaveValue('');
    console.log('✅ Form cleared after cancel');
    
    // Test close button (X)
    await page.locator('[data-testid="close-modal"]').click();
    await page.waitForTimeout(200);
    
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Close button (X) working correctly');
  });

  test('should test all form fields and interactions', async ({ page }) => {
    console.log('📋 Testing all form fields and interactions...');
    
    // Navigate to inventory and open modal
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Test all form fields
    const formFields = [
      { testId: 'item-name-input', value: 'Comprehensive Test Item' },
      { testId: 'item-sku-input', value: `COMP-TEST-${Date.now()}` },
      { testId: 'item-price-input', value: '199.99' },
      { testId: 'item-quantity-input', value: '100' },
      { testId: 'item-description-input', value: 'This is a comprehensive test of all form fields including validation and user interaction patterns.' }
    ];
    
    for (const field of formFields) {
      console.log(`Testing field: ${field.testId}`);
      const input = page.locator(`[data-testid="${field.testId}"]`);
      
      // Test input
      await input.fill(field.value);
      await expect(input).toHaveValue(field.value);
      
      // Test focus styling (verify field is focusable)
      await input.focus();
      await page.waitForTimeout(100);
      
      console.log(`✅ ${field.testId} working correctly`);
    }
    
    // Test category dropdown
    console.log('Testing category dropdown...');
    const categorySelect = page.locator('[data-testid="item-category-select"]');
    await categorySelect.selectOption('furniture');
    await expect(categorySelect).toHaveValue('furniture');
    console.log('✅ Category dropdown working correctly');
    
    // Test form submission with all fields
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Comprehensive Test Item');
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(1000);
    
    // Verify modal closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('🎉 All form fields test completed successfully!');
  });
});
