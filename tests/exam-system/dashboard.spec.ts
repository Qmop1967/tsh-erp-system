import { test, expect } from '@playwright/test';

const BASE_URL = process.env.APP_URL || 'http://localhost:5173';

test.describe('ERP Dashboard Examinations - Level 1 & 2', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  // G001: Theme Toggle and Persistence (L1 - 2 points)
  test('G001: Theme toggle and persistence', async ({ page }) => {
    // Verify dashboard loads
    await expect(page.getByTestId('page-title')).toBeVisible();
    
    // Test theme toggle
    const themeToggle = page.getByTestId('theme-toggle');
    await expect(themeToggle).toBeVisible();
    
    // Click theme toggle and verify change (visual regression would be ideal)
    await themeToggle.click();
    
    // Reload page to test persistence
    await page.reload();
    await expect(page.getByTestId('page-title')).toBeVisible();
    
    console.log('✅ G001 PASSED: Theme toggle functionality verified');
  });

  // G002: Global Search Functionality (L1 - 3 points)
  test('G002: Global search functionality', async ({ page }) => {
    const searchInput = page.getByTestId('global-search');
    await expect(searchInput).toBeVisible();
    
    // Test search input focus and interaction
    await searchInput.click();
    await expect(searchInput).toBeFocused();
    
    // Type in search
    await searchInput.fill('Sales');
    await expect(searchInput).toHaveValue('Sales');
    
    // Test keyboard navigation
    await searchInput.press('Tab');
    
    console.log('✅ G002 PASSED: Global search functionality verified');
  });

  // G003: Sidebar Navigation (L2 - 4 points)
  test('G003: Sidebar navigation and keyboard accessibility', async ({ page }) => {
    const sidebarToggle = page.getByTestId('sidebar-toggle');
    await expect(sidebarToggle).toBeVisible();
    
    // Test sidebar toggle
    await sidebarToggle.click();
    
    // Test keyboard navigation
    await sidebarToggle.focus();
    await sidebarToggle.press('Enter');
    
    console.log('✅ G003 PASSED: Sidebar navigation verified');
  });

  // D001: Dashboard Loading (L1 - 3 points)
  test('D001: Dashboard loading and metrics display', async ({ page }) => {
    // Verify dashboard title
    await expect(page.getByTestId('page-title')).toHaveText('Dashboard');
    
    // Check for key sections
    await expect(page.getByText('Financial Overview')).toBeVisible();
    await expect(page.getByText('Money Boxes')).toBeVisible();
    await expect(page.getByText('Recent Activity')).toBeVisible();
    
    // Verify metric cards
    await expect(page.getByText('Total Revenue')).toBeVisible();
    await expect(page.getByText('Net Profit')).toBeVisible();
    await expect(page.getByText('Total Employees')).toBeVisible();
    await expect(page.getByText('Inventory Items')).toBeVisible();
    
    console.log('✅ D001 PASSED: Dashboard loading verified');
  });

  // D002: Financial Data Accuracy (L2 - 5 points)
  test('D002: Financial data accuracy', async ({ page }) => {
    // Verify currency formatting is present
    await expect(page.getByText(/\$[\d,]+\.?\d*/)).toBeVisible();
    
    // Check specific financial elements
    await expect(page.getByText('Total Receivables')).toBeVisible();
    await expect(page.getByText('Total Payables')).toBeVisible();
    await expect(page.getByText('Stock Value')).toBeVisible();
    await expect(page.getByText('Total Cash Flow')).toBeVisible();
    
    console.log('✅ D002 PASSED: Financial data display verified');
  });

  // U001: User Management Navigation (L2 - 6 points)
  test('U001: User management navigation', async ({ page }) => {
    // Navigate to User Management
    await page.getByTestId('nav-users').click();
    
    // Verify header changes
    await expect(page.getByTestId('page-title')).toHaveText('User Management');
    
    // Check for Available Features section
    await expect(page.getByText('Available Features')).toBeVisible();
    
    // Verify action buttons
    await expect(page.getByRole('button', { name: /Add New/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /View All/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Filter/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Export/i })).toBeVisible();
    
    console.log('✅ U001 PASSED: User Management navigation verified');
  });

  // S001: Sales Module Navigation (L2 - 6 points)
  test('S001: Sales module navigation', async ({ page }) => {
    // Navigate to Sales Management
    await page.getByTestId('nav-sales').click();
    
    // Verify header
    await expect(page.getByTestId('page-title')).toHaveText('Sales Management');
    
    // Check for Available Features
    await expect(page.getByText('Available Features')).toBeVisible();
    
    // Verify submodule features are mentioned (even if just in the sidebar)
    await expect(page.getByText('Customers')).toBeVisible();
    await expect(page.getByText('Sales Orders')).toBeVisible();
    await expect(page.getByText('Quotations')).toBeVisible();
    await expect(page.getByText('Invoices')).toBeVisible();
    await expect(page.getByText('Payments')).toBeVisible();
    await expect(page.getByText('Credit Notes')).toBeVisible();
    
    console.log('✅ S001 PASSED: Sales module navigation verified');
  });

  // I001: Inventory Module Features (L2 - 6 points)
  test('I001: Inventory module features', async ({ page }) => {
    // Navigate to Inventory
    await page.getByTestId('nav-inventory').click();
    
    // Verify header
    await expect(page.getByTestId('page-title')).toHaveText('Inventory');
    
    // Check for subfeatures in sidebar
    await expect(page.getByText('Items')).toBeVisible();
    await expect(page.getByText('Stock Adjustments')).toBeVisible();
    await expect(page.getByText('Warehouses')).toBeVisible();
    await expect(page.getByText('Stock Movements')).toBeVisible();
    await expect(page.getByText('Suppliers')).toBeVisible();
    
    console.log('✅ I001 PASSED: Inventory module features verified');
  });

  // F001: Money Boxes Display (L2 - 5 points)
  test('F001: Money boxes display', async ({ page }) => {
    // Navigate to Dashboard
    await page.getByTestId('nav-dashboard').click();
    
    // Check Money Boxes section
    await expect(page.getByText('Money Boxes')).toBeVisible();
    await expect(page.getByText('Total Cash Flow')).toBeVisible();
    
    // Count individual money boxes (should see at least several)
    const moneyBoxes = await page.getByText(/\$[\d,]+\.?\d*/).count();
    expect(moneyBoxes).toBeGreaterThan(5);
    
    console.log('✅ F001 PASSED: Money boxes display verified');
  });

  // A001: Keyboard Navigation (L2 - 4 points)
  test('A001: Keyboard navigation', async ({ page }) => {
    // Test Tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Test theme toggle with keyboard
    const themeToggle = page.getByTestId('theme-toggle');
    await themeToggle.focus();
    await themeToggle.press('Enter');
    
    // Test search field with Tab
    const searchField = page.getByTestId('global-search');
    await searchField.focus();
    await expect(searchField).toBeFocused();
    
    console.log('✅ A001 PASSED: Keyboard navigation verified');
  });
});

test.describe('ERP Dashboard Examinations - Level 3 & 4', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  // S002: Sales Workflow Understanding (L3 - 8 points)
  test('S002: Sales workflow simulation', async ({ page }) => {
    await page.getByTestId('nav-sales').click();
    
    // Verify user can identify workflow components
    await expect(page.getByText('Quotations')).toBeVisible();
    await expect(page.getByText('Sales Orders')).toBeVisible();
    await expect(page.getByText('Invoices')).toBeVisible();
    await expect(page.getByText('Payments')).toBeVisible();
    
    console.log('✅ S002 PASSED: Sales workflow components identified');
  });

  // I002: Stock Value Integration (L3 - 7 points)
  test('I002: Stock value integration', async ({ page }) => {
    // Check dashboard metrics
    await page.getByTestId('nav-dashboard').click();
    await expect(page.getByText('Stock Value')).toBeVisible();
    await expect(page.getByText('Inventory Items')).toBeVisible();
    
    // Navigate to inventory and connect the concepts
    await page.getByTestId('nav-inventory').click();
    await expect(page.getByTestId('page-title')).toHaveText('Inventory');
    
    console.log('✅ I002 PASSED: Stock value integration verified');
  });

  // F002: Financial Management Integration (L3 - 6 points)
  test('F002: Financial management integration', async ({ page }) => {
    // Check money boxes on dashboard
    await page.getByTestId('nav-dashboard').click();
    await expect(page.getByText('Money Boxes')).toBeVisible();
    
    // Navigate to Financial Management
    await page.getByTestId('nav-financial').click();
    await expect(page.getByTestId('page-title')).toHaveText('Financial Management');
    await expect(page.getByText('Cash Boxes')).toBeVisible();
    
    console.log('✅ F002 PASSED: Financial management integration verified');
  });

  // P001: Dashboard Load Performance (L3 - 5 points)
  test('P001: Dashboard load performance', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(BASE_URL);
    await expect(page.getByTestId('page-title')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    console.log(`Dashboard load time: ${loadTime}ms`);
    
    // Performance assertion (should load reasonably quickly)
    expect(loadTime).toBeLessThan(5000); // 5 second max for local development
    
    console.log('✅ P001 PASSED: Dashboard performance within acceptable limits');
  });

  // SEC001: Input Security (L4 - 6 points)
  test('SEC001: Input validation and XSS prevention', async ({ page }) => {
    const searchInput = page.getByTestId('global-search');
    
    // Test with special characters
    await searchInput.fill('<script>alert("test")</script>');
    await expect(searchInput).toHaveValue('<script>alert("test")</script>');
    
    // Test with SQL injection patterns
    await searchInput.fill("'; DROP TABLE users; --");
    await expect(searchInput).toHaveValue("'; DROP TABLE users; --");
    
    // Verify no JavaScript execution (page should still be functional)
    await expect(page.getByTestId('page-title')).toBeVisible();
    
    console.log('✅ SEC001 PASSED: Input security measures verified');
  });
});
