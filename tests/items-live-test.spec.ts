import { test, expect } from '@playwright/test';

test.describe('Items Page - Live Styling Test', () => {
  test('Complete visual and interaction test', async ({ page }) => {
    console.log('🚀 Starting live test of Items page...');

    // Navigate to Items page
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);

    await page.click('[data-testid="nav-inventory"]');
    await page.waitForTimeout(1000);

    await page.click('[data-testid="submenu-items"]');
    await page.waitForTimeout(3000);

    console.log('✅ Navigation successful');

    // Wait for items to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // 1. Take initial screenshot
    await page.screenshot({
      path: 'test-results/live-test-1-initial.png',
      fullPage: true
    });
    console.log('📸 Screenshot 1: Initial page load');

    // 2. Test search functionality
    await page.fill('input[placeholder*="Search"]', 'iPhone');
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: 'test-results/live-test-2-search.png',
      fullPage: true
    });
    console.log('📸 Screenshot 2: Search functionality');

    // Clear search
    await page.fill('input[placeholder*="Search"]', '');
    await page.waitForTimeout(500);

    // 3. Test sorting
    await page.selectOption('select:has-text("Sort by")', 'price');
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: 'test-results/live-test-3-sort.png',
      fullPage: true
    });
    console.log('📸 Screenshot 3: Sort by price');

    // 4. Hover over action buttons
    await page.hover('button:has(svg):nth-of-type(1)');
    await page.waitForTimeout(500);
    await page.screenshot({
      path: 'test-results/live-test-4-hover.png',
      fullPage: false
    });
    console.log('📸 Screenshot 4: Hover effects');

    // 5. Test Grid View
    const gridButton = page.locator('button:has-text(""), button svg').filter({ hasText: '' }).last();
    await page.click('button[class*="rounded-lg"]:has(svg):nth-of-type(2)');
    await page.waitForTimeout(2000);
    await page.screenshot({
      path: 'test-results/live-test-5-grid-view.png',
      fullPage: true
    });
    console.log('📸 Screenshot 5: Grid view');

    // 6. Back to List View
    await page.click('button[class*="rounded-lg"]:has(svg):nth-of-type(1)');
    await page.waitForTimeout(1000);

    // 7. Test pagination (if available)
    const nextButton = page.locator('button:has-text("Next")');
    if (await nextButton.isVisible() && !(await nextButton.isDisabled())) {
      await nextButton.click();
      await page.waitForTimeout(1000);
      await page.screenshot({
        path: 'test-results/live-test-6-pagination.png',
        fullPage: true
      });
      console.log('📸 Screenshot 6: Pagination');
    }

    // 8. Check stats cards
    const totalItems = await page.textContent('text=Total Items');
    const activeItems = await page.textContent('text=Active Items');
    const totalValue = await page.textContent('text=Total Value');
    console.log('📊 Stats:', { totalItems, activeItems, totalValue });

    // 9. Final full page screenshot
    await page.screenshot({
      path: 'test-results/live-test-7-final.png',
      fullPage: true
    });
    console.log('📸 Screenshot 7: Final state');

    // 10. Capture just the table area
    const table = page.locator('table');
    await table.screenshot({
      path: 'test-results/live-test-8-table-detail.png'
    });
    console.log('📸 Screenshot 8: Table detail');

    // 11. Capture stats cards
    const statsCards = page.locator('div.grid').first();
    await statsCards.screenshot({
      path: 'test-results/live-test-9-stats-cards.png'
    });
    console.log('📸 Screenshot 9: Stats cards');

    console.log('✨ Live test completed successfully!');
  });

  test('Check styling elements', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
    await page.click('[data-testid="nav-inventory"]');
    await page.waitForTimeout(1000);
    await page.click('[data-testid="submenu-items"]');
    await page.waitForTimeout(3000);

    // Check for gradient backgrounds
    const hasGradient = await page.locator('div[class*="gradient"]').count();
    console.log(`🎨 Gradient elements found: ${hasGradient}`);

    // Check for rounded corners
    const hasRounded = await page.locator('[class*="rounded"]').count();
    console.log(`🔘 Rounded elements found: ${hasRounded}`);

    // Check for shadows
    const hasShadow = await page.locator('[class*="shadow"]').count();
    console.log(`🌑 Shadow elements found: ${hasShadow}`);

    // Check for hover effects
    const hasHover = await page.locator('[class*="hover"]').count();
    console.log(`👆 Hover elements found: ${hasHover}`);

    // Check icons
    const iconCount = await page.locator('svg').count();
    console.log(`🎯 Icons found: ${iconCount}`);

    expect(hasGradient).toBeGreaterThan(0);
    expect(hasRounded).toBeGreaterThan(10);
    expect(hasShadow).toBeGreaterThan(5);
    expect(iconCount).toBeGreaterThan(15);

    console.log('✅ All styling elements verified!');
  });
});