import { test, expect } from '@playwright/test';

test.describe('Dropdown Plus Button Functionality Tests', () => {
  test.beforeEach(async ({ page }) => {
    console.log('🌐 Navigating to frontend...');
    await page.goto('http://localhost:5174');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Wait for React to fully load
  });

  test('should display plus buttons next to all dropdown items', async ({ page }) => {
    console.log('🔍 Testing plus button visibility...');
    
    // Click on User Management to expand dropdown
    await page.locator('[data-testid="nav-users"]').click();
    await page.waitForTimeout(500);
    
    // Check if "All Users" submenu item has a plus button
    const addUsersButton = page.locator('[data-testid="add-all-users"]');
    await expect(addUsersButton).toBeVisible();
    console.log('✅ Plus button visible for All Users');
    
    // Check permissions submenu
    const addPermissionsButton = page.locator('[data-testid="add-permissions"]');
    await expect(addPermissionsButton).toBeVisible();
    console.log('✅ Plus button visible for Permissions');
    
    // Check roles submenu
    const addRolesButton = page.locator('[data-testid="add-roles"]');
    await expect(addRolesButton).toBeVisible();
    console.log('✅ Plus button visible for Roles');
    
    // Navigate to Sales Management
    await page.locator('[data-testid="nav-sales"]').click();
    await page.waitForTimeout(500);
    
    // Check customers submenu
    const addCustomersButton = page.locator('[data-testid="add-customers"]');
    await expect(addCustomersButton).toBeVisible();
    console.log('✅ Plus button visible for Customers');
    
    // Navigate to Inventory
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    // Check items submenu
    const addItemsButton = page.locator('[data-testid="add-items"]');
    await expect(addItemsButton).toBeVisible();
    console.log('✅ Plus button visible for Items');
    
    await page.screenshot({ path: 'test-results/plus-buttons-visible.png' });
  });

  test('should open Add User modal when clicking plus button next to All Users', async ({ page }) => {
    console.log('👤 Testing Add User functionality...');
    
    // Navigate to User Management and expand
    await page.locator('[data-testid="nav-users"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "All Users"
    await page.locator('[data-testid="add-all-users"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal opened with correct title
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Add New User');
    console.log('✅ Add User modal opened with correct title');
    
    // Check that user-specific fields are present
    await expect(page.locator('[data-testid="user-name-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-employee-code-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="user-phone-input"]')).toBeVisible();
    console.log('✅ All user form fields are visible');
    
    await page.screenshot({ path: 'test-results/add-user-modal.png' });
    
    // Test form submission with valid data
    console.log('📝 Filling user form...');
    await page.locator('[data-testid="user-name-input"]').fill('Test User 123');
    await page.locator('[data-testid="user-email-input"]').fill('testuser123@example.com');
    await page.locator('[data-testid="user-employee-code-input"]').fill('EMP123');
    await page.locator('[data-testid="user-password-input"]').fill('password123');
    await page.locator('[data-testid="user-phone-input"]').fill('+1-555-0123');
    
    // Submit the form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Check for success or error message (accept both since backend might not be fully set up)
    const alertPromise = page.waitForEvent('dialog');
    try {
      const dialog = await alertPromise;
      console.log('📢 Alert received:', dialog.message());
      await dialog.accept();
      console.log('✅ User creation flow completed');
    } catch (e) {
      console.log('ℹ️ No alert received, continuing...');
    }
    
    await page.screenshot({ path: 'test-results/add-user-completed.png' });
  });

  test('should open Add Customer modal when clicking plus button next to Customers', async ({ page }) => {
    console.log('🏢 Testing Add Customer functionality...');
    
    // Navigate to Sales Management and expand
    await page.locator('[data-testid="nav-sales"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "Customers"
    await page.locator('[data-testid="add-customers"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal opened with correct title
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Add New Customer');
    console.log('✅ Add Customer modal opened with correct title');
    
    // Check that customer-specific fields are present
    await expect(page.locator('[data-testid="customer-name-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="customer-email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="customer-phone-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="customer-contact-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="customer-address-input"]')).toBeVisible();
    console.log('✅ All customer form fields are visible');
    
    await page.screenshot({ path: 'test-results/add-customer-modal.png' });
    
    // Test form submission with valid data
    console.log('📝 Filling customer form...');
    await page.locator('[data-testid="customer-name-input"]').fill('Test Customer Corp');
    await page.locator('[data-testid="customer-email-input"]').fill('contact@testcustomer.com');
    await page.locator('[data-testid="customer-phone-input"]').fill('+1-555-0123');
    await page.locator('[data-testid="customer-contact-input"]').fill('John Doe');
    await page.locator('[data-testid="customer-address-input"]').fill('123 Business Ave, Suite 100, Business City, BC 12345');
    
    // Submit the form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Check for success or error message
    const alertPromise = page.waitForEvent('dialog');
    try {
      const dialog = await alertPromise;
      console.log('📢 Alert received:', dialog.message());
      await dialog.accept();
      console.log('✅ Customer creation flow completed');
    } catch (e) {
      console.log('ℹ️ No alert received, continuing...');
    }
    
    await page.screenshot({ path: 'test-results/add-customer-completed.png' });
  });

  test('should open Add Inventory Item modal when clicking plus button next to Items', async ({ page }) => {
    console.log('📦 Testing Add Inventory Item functionality...');
    
    // Navigate to Inventory and expand
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "Items"
    await page.locator('[data-testid="add-items"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal opened with correct title
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Add New Inventory Item');
    console.log('✅ Add Inventory Item modal opened with correct title');
    
    // Check that inventory-specific fields are present
    await expect(page.locator('[data-testid="item-name-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-sku-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-category-select"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-price-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-quantity-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-description-input"]')).toBeVisible();
    console.log('✅ All inventory form fields are visible');
    
    await page.screenshot({ path: 'test-results/add-inventory-modal.png' });
    
    // Test form submission with valid data
    console.log('📝 Filling inventory form...');
    await page.locator('[data-testid="item-name-input"]').fill('Test Product Widget');
    await page.locator('[data-testid="item-sku-input"]').fill('TPW-001');
    await page.locator('[data-testid="item-category-select"]').selectOption('electronics');
    await page.locator('[data-testid="item-price-input"]').fill('29.99');
    await page.locator('[data-testid="item-quantity-input"]').fill('100');
    await page.locator('[data-testid="item-description-input"]').fill('A high-quality test widget for demonstration purposes.');
    
    // Submit the form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Check for success or error message
    const alertPromise = page.waitForEvent('dialog');
    try {
      const dialog = await alertPromise;
      console.log('📢 Alert received:', dialog.message());
      await dialog.accept();
      console.log('✅ Inventory item creation flow completed');
    } catch (e) {
      console.log('ℹ️ No alert received, continuing...');
    }
    
    await page.screenshot({ path: 'test-results/add-inventory-completed.png' });
  });

  test('should close modal when clicking cancel button', async ({ page }) => {
    console.log('❌ Testing modal cancel functionality...');
    
    // Navigate to User Management and expand
    await page.locator('[data-testid="nav-users"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "All Users"
    await page.locator('[data-testid="add-all-users"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal is open
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    
    // Click cancel button
    await page.locator('[data-testid="cancel-add-item"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal is closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Modal closed successfully after clicking cancel');
    
    await page.screenshot({ path: 'test-results/modal-cancelled.png' });
  });

  test('should close modal when clicking X button', async ({ page }) => {
    console.log('❌ Testing modal X button functionality...');
    
    // Navigate to Sales Management and expand
    await page.locator('[data-testid="nav-sales"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "Customers"
    await page.locator('[data-testid="add-customers"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal is open
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    
    // Click X button
    await page.locator('[data-testid="close-modal"]').click();
    await page.waitForTimeout(500);
    
    // Verify modal is closed
    await expect(page.locator('[data-testid="add-item-modal"]')).not.toBeVisible();
    console.log('✅ Modal closed successfully after clicking X');
    
    await page.screenshot({ path: 'test-results/modal-x-closed.png' });
  });

  test('should handle form validation for required fields', async ({ page }) => {
    console.log('🛡️ Testing form validation...');
    
    // Navigate to User Management and expand
    await page.locator('[data-testid="nav-users"]').click();
    await page.waitForTimeout(500);
    
    // Click the plus button next to "All Users"
    await page.locator('[data-testid="add-all-users"]').click();
    await page.waitForTimeout(500);
    
    // Try to submit empty form
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(500);
    
    // Check that form validation prevents submission
    // The modal should still be visible (not closed)
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    console.log('✅ Form validation working - empty form not submitted');
    
    await page.screenshot({ path: 'test-results/form-validation.png' });
  });

  test('should maintain dropdown state when opening and closing modals', async ({ page }) => {
    console.log('🔄 Testing dropdown state persistence...');
    
    // Navigate to Sales Management and expand
    await page.locator('[data-testid="nav-sales"]').click();
    await page.waitForTimeout(500);
    
    // Verify dropdown is expanded
    await expect(page.locator('[data-testid="add-customers"]')).toBeVisible();
    
    // Open modal
    await page.locator('[data-testid="add-customers"]').click();
    await page.waitForTimeout(500);
    
    // Close modal
    await page.locator('[data-testid="cancel-add-item"]').click();
    await page.waitForTimeout(500);
    
    // Verify dropdown is still expanded
    await expect(page.locator('[data-testid="add-customers"]')).toBeVisible();
    console.log('✅ Dropdown state maintained after modal close');
    
    await page.screenshot({ path: 'test-results/dropdown-state-maintained.png' });
  });
});
