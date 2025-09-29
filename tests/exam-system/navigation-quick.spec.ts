import { test, expect } from '@playwright/test';

test.describe('Navigation Quick Test', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('should verify all enhanced modules work', async ({ page }) => {
    const enhancedModules = [
      { id: 'users', expectedText: '👥 User Management' },
      { id: 'hr', expectedText: '👔 Human Resources' },
      { id: 'sales', expectedText: '🛒 Sales Management' },
      { id: 'financial', expectedText: '💰 Financial Management' },
      { id: 'inventory', expectedText: '📦 Inventory Categories' }
    ];

    for (const module of enhancedModules) {
      console.log(`Testing ${module.id} module...`);
      
      // Navigate to module
      const navItem = page.locator(`[data-testid="nav-${module.id}"]`);
      await navItem.click();
      await page.waitForTimeout(500);
      
      // Verify content
      const content = await page.textContent('main');
      expect(content).toContain(module.expectedText);
      
      console.log(`✅ ${module.id} module working correctly`);
    }
  });

  test('should verify generic modules show proper interface', async ({ page }) => {
    const genericModules = ['purchase', 'accounting', 'pos', 'branches', 'security', 'reports', 'settings'];

    for (const moduleId of genericModules) {
      const navItem = page.locator(`[data-testid="nav-${moduleId}"]`);
      await navItem.click();
      await page.waitForTimeout(300);
      
      // Verify generic interface elements
      const content = await page.textContent('main');
      expect(content).toContain('Module interface is ready');
      expect(content).toContain('Status');
      expect(content).toContain('Ready');
      
      console.log(`✅ ${moduleId} shows proper generic interface`);
    }
  });
});
