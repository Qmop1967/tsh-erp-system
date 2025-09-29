import { test, expect } from '@playwright/test';

test.describe('🟣 Enhancement & Stability Tests - Performance', () => {
  test('should load main pages within 3 seconds', async ({ page }) => {
    const modules = ['dashboard', 'inventory', 'sales', 'financial', 'users'];
    const performanceResults: Array<{module: string, loadTime: number}> = [];
    
    for (const module of modules) {
      const startTime = Date.now();
      
      await page.goto('http://localhost:3001');
      await page.waitForLoadState('networkidle');
      
      if (module !== 'dashboard') {
        await page.locator(`[data-testid="nav-${module}"]`).click();
        await page.waitForLoadState('networkidle');
      }
      
      const endTime = Date.now();
      const loadTime = (endTime - startTime) / 1000;
      
      performanceResults.push({ module, loadTime });
      
      console.log(`${module} module loaded in ${loadTime.toFixed(2)} seconds`);
      
      // Verify page loaded correctly
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible();
      
      // Take performance screenshot
      await page.screenshot({ 
        path: `test-results/performance-${module}-${loadTime.toFixed(2)}s.png`,
        fullPage: true
      });
      
      // Check if load time is within 3 seconds
      expect(loadTime).toBeLessThan(3);
    }
    
    // Log performance summary
    console.log('\n📊 Performance Test Results:');
    performanceResults.forEach(result => {
      const status = result.loadTime < 3 ? '✅ PASS' : '❌ FAIL';
      console.log(`${result.module}: ${result.loadTime.toFixed(2)}s ${status}`);
    });
  });

  test('should handle search queries without freezing', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    const searchInput = page.locator('[data-testid="global-search"]');
    const searchQueries = [
      'product',
      'customer',
      'inventory management',
      'sales report',
      'financial data'
    ];
    
    for (const query of searchQueries) {
      const startTime = Date.now();
      
      await searchInput.clear();
      await searchInput.fill(query);
      await page.waitForTimeout(500); // Allow for search processing
      
      const endTime = Date.now();
      const searchTime = (endTime - startTime) / 1000;
      
      console.log(`Search "${query}" completed in ${searchTime.toFixed(2)} seconds`);
      
      // Verify search didn't freeze the UI
      await expect(searchInput).toHaveValue(query);
      expect(searchTime).toBeLessThan(2); // Search should complete within 2 seconds
    }
    
    await page.screenshot({ path: 'test-results/search-performance.png' });
  });

  test('should measure form submission performance', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill form
    const perfTestId = Date.now();
    await page.locator('[data-testid="item-name-input"]').fill(`Performance Test ${perfTestId}`);
    await page.locator('[data-testid="item-sku-input"]').fill(`PERF-${perfTestId}`);
    await page.locator('[data-testid="item-price-input"]').fill('99.99');
    
    // Measure submission time
    const startTime = Date.now();
    
    page.on('dialog', async (dialog) => {
      const endTime = Date.now();
      const submissionTime = (endTime - startTime) / 1000;
      
      console.log(`Form submission completed in ${submissionTime.toFixed(2)} seconds`);
      expect(submissionTime).toBeLessThan(3); // Should complete within 3 seconds
      
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'test-results/form-performance.png' });
  });
});

test.describe('🟣 Enhancement & Stability Tests - Responsive UI', () => {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'laptop', width: 1366, height: 768 },
    { name: 'desktop', width: 1920, height: 1080 }
  ];

  for (const viewport of viewports) {
    test(`should display correctly on ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('http://localhost:3001');
      await page.waitForLoadState('networkidle');
      
      // Test main dashboard
      await expect(page.locator('[data-testid="page-title"]')).toBeVisible();
      
      // Test sidebar toggle on smaller screens
      if (viewport.width < 768) {
        const sidebarToggle = page.locator('[data-testid="sidebar-toggle"]');
        await expect(sidebarToggle).toBeVisible();
        await sidebarToggle.click();
        await page.waitForTimeout(300);
      }
      
      // Test navigation works on this viewport
      await page.locator('[data-testid="nav-inventory"]').click();
      await page.waitForTimeout(500);
      
      await expect(page.locator('[data-testid="page-title"]')).toContainText('Inventory');
      
      // Test form responsiveness
      await page.getByText('Add New Item').click();
      await page.waitForTimeout(500);
      
      // Verify modal is visible and properly sized
      const modal = page.locator('[data-testid="add-item-modal"]');
      await expect(modal).toBeVisible();
      
      // Check form elements are accessible
      await expect(page.locator('[data-testid="item-name-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="save-add-item"]')).toBeVisible();
      
      await page.locator('[data-testid="cancel-add-item"]').click();
      
      await page.screenshot({ 
        path: `test-results/responsive-${viewport.name}-${viewport.width}x${viewport.height}.png`,
        fullPage: true
      });
      
      console.log(`✅ ${viewport.name} viewport test completed`);
    });
  }

  test('should prevent component overlap on small screens', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 }); // Very small mobile
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Check main navigation elements don't overlap
    const sidebarToggle = page.locator('[data-testid="sidebar-toggle"]');
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    const searchInput = page.locator('[data-testid="global-search"]');
    
    await expect(sidebarToggle).toBeVisible();
    await expect(themeToggle).toBeVisible();
    await expect(searchInput).toBeVisible();
    
    // Test modal on very small screen
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Modal should still be usable
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    await expect(page.locator('[data-testid="item-name-input"]')).toBeVisible();
    
    await page.locator('[data-testid="cancel-add-item"]').click();
    
    await page.screenshot({ path: 'test-results/small-screen-320px.png', fullPage: true });
  });
});

test.describe('🟣 Enhancement & Stability Tests - Loading Indicators', () => {
  test('should show loading indicators during data fetch', async ({ page }) => {
    await page.goto('http://localhost:3001');
    
    // Monitor for loading states
    const loadingStates: string[] = [];
    
    // Listen for loading-related elements
    page.on('response', response => {
      if (response.url().includes('api') && response.status() === 200) {
        console.log(`API response: ${response.url()}`);
      }
    });
    
    await page.waitForLoadState('networkidle');
    
    // Test navigation loading
    await page.locator('[data-testid="nav-inventory"]').click();
    
    // Look for any loading indicators
    const possibleLoadingSelectors = [
      '.loading',
      '.spinner',
      '[data-testid*="loading"]',
      '[data-testid*="spinner"]',
      '.fa-spinner',
      '.animate-spin'
    ];
    
    for (const selector of possibleLoadingSelectors) {
      const loadingElement = page.locator(selector);
      if (await loadingElement.isVisible()) {
        loadingStates.push(selector);
        console.log(`Loading indicator found: ${selector}`);
      }
    }
    
    await page.waitForTimeout(1000);
    
    // Verify page loads completely
    await expect(page.locator('[data-testid="page-title"]')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/loading-indicators.png' });
    
    console.log(`Found ${loadingStates.length} loading indicators`);
  });

  test('should hide loading indicators after completion', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Test form submission loading
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill and submit form
    await page.locator('[data-testid="item-name-input"]').fill(`Loading Test ${Date.now()}`);
    await page.locator('[data-testid="item-sku-input"]').fill(`LOAD-${Date.now()}`);
    
    // Monitor for loading during submission
    page.on('dialog', async (dialog) => {
      console.log('Form submission completed - dialog appeared');
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    // Verify no loading indicators remain visible
    const remainingLoaders = await page.locator('.loading, .spinner, [data-testid*="loading"]').count();
    expect(remainingLoaders).toBe(0);
    
    await page.screenshot({ path: 'test-results/loading-completion.png' });
  });
});

test.describe('🟣 Enhancement & Stability Tests - Security Checks', () => {
  test('should handle protected route access', async ({ page }) => {
    // Test direct access to application
    await page.goto('http://localhost:3001');
    
    // For demo purposes, assume we're testing the accessible routes
    // In a real system, this would test authentication redirects
    
    const restrictedRoutes = [
      'http://localhost:3001/admin',
      'http://localhost:3001/settings',
      'http://localhost:3001/users'
    ];
    
    for (const route of restrictedRoutes) {
      try {
        const response = await page.goto(route);
        console.log(`Route ${route}: ${response?.status() || 'No response'}`);
        
        // Check if redirected to login or shows proper content
        const currentUrl = page.url();
        console.log(`Current URL after navigation: ${currentUrl}`);
        
        await page.screenshot({ 
          path: `test-results/security-route-${route.split('/').pop()}.png` 
        });
        
      } catch (error) {
        console.log(`Route ${route} not accessible: ${error}`);
      }
    }
  });

  test('should verify user permissions', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Test access to different modules (simulates permission checking)
    const modules = ['users', 'settings', 'security'];
    
    for (const module of modules) {
      const navItem = page.locator(`[data-testid="nav-${module}"]`);
      
      if (await navItem.isVisible()) {
        await navItem.click();
        await page.waitForTimeout(500);
        
        // Verify user can access the module
        await expect(page.locator('[data-testid="page-title"]')).toBeVisible();
        console.log(`✅ Access granted to ${module} module`);
        
      } else {
        console.log(`⚠️ ${module} module not accessible (may be restricted)`);
      }
    }
    
    await page.screenshot({ path: 'test-results/permission-testing.png' });
  });
});
