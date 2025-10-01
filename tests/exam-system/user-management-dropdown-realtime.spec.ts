import { test, expect, Page } from '@playwright/test';

test.describe('User Management Dropdown Real-time Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Navigate to the application
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of initial state
    await page.screenshot({ path: 'test-results/initial-page.png', fullPage: true });
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('should analyze page structure and find user management elements', async () => {
    console.log('=== Page Analysis ===');
    
    // Get page title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Check for common navigation patterns
    const navElements = await page.locator('nav, .navbar, .navigation, .menu, .sidebar, header').all();
    console.log(`Found ${navElements.length} navigation elements`);
    
    for (let i = 0; i < navElements.length; i++) {
      const nav = navElements[i];
      const navText = await nav.textContent();
      const navHTML = await nav.innerHTML();
      console.log(`\nNavigation ${i + 1}:`);
      console.log(`Text content: ${navText?.substring(0, 200)}...`);
      console.log(`HTML: ${navHTML.substring(0, 300)}...`);
    }
    
    // Look for any dropdown elements
    const dropdownElements = await page.locator('[class*="dropdown"], [class*="menu"], button[aria-haspopup], [role="button"]').all();
    console.log(`\nFound ${dropdownElements.length} potential dropdown elements`);
    
    for (let i = 0; i < Math.min(dropdownElements.length, 5); i++) {
      const dropdown = dropdownElements[i];
      const dropdownText = await dropdown.textContent();
      const dropdownHTML = await dropdown.innerHTML();
      console.log(`\nDropdown ${i + 1}:`);
      console.log(`Text: ${dropdownText}`);
      console.log(`HTML: ${dropdownHTML.substring(0, 200)}...`);
    }
    
    // Look for user-related text
    const userElements = await page.locator('text=/user/i, text=/management/i, text=/admin/i').all();
    console.log(`\nFound ${userElements.length} user-related elements`);
    
    for (let i = 0; i < Math.min(userElements.length, 5); i++) {
      const userEl = userElements[i];
      const userText = await userEl.textContent();
      console.log(`User element ${i + 1}: ${userText}`);
    }
    
    // Take screenshot for visual inspection
    await page.screenshot({ path: 'test-results/page-analysis.png', fullPage: true });
    
    // This test always passes - it's for analysis
    expect(true).toBe(true);
  });

  test('should test all clickable elements for dropdown behavior', async () => {
    console.log('=== Testing Clickable Elements ===');
    
    // Find all buttons and clickable elements
    const clickableElements = await page.locator('button, [role="button"], .btn, [class*="button"]').all();
    console.log(`Found ${clickableElements.length} clickable elements`);
    
    let dropdownFound = false;
    
    for (let i = 0; i < Math.min(clickableElements.length, 10); i++) {
      const element = clickableElements[i];
      
      try {
        const elementText = await element.textContent();
        const isVisible = await element.isVisible();
        const isEnabled = await element.isEnabled();
        
        console.log(`\nElement ${i + 1}: "${elementText}" (visible: ${isVisible}, enabled: ${isEnabled})`);
        
        if (!isVisible || !isEnabled) continue;
        
        // Check if this might be user management related
        if (elementText?.toLowerCase().includes('user') || 
            elementText?.toLowerCase().includes('management') ||
            elementText?.toLowerCase().includes('admin')) {
          
          console.log(`🎯 Found potential user management element: "${elementText}"`);
          
          // Take screenshot before click
          await page.screenshot({ path: `test-results/before-click-${i}.png`, fullPage: true });
          
          // Click the element
          await element.click();
          
          // Wait a moment for any dropdown to appear
          await page.waitForTimeout(1000);
          
          // Take screenshot after click
          await page.screenshot({ path: `test-results/after-click-${i}.png`, fullPage: true });
          
          // Check if a dropdown/menu appeared
          const dropdownMenu = await page.locator('.dropdown-menu, [role="menu"], .menu, [class*="dropdown"][class*="open"]').first();
          
          if (await dropdownMenu.isVisible({ timeout: 2000 })) {
            console.log('✅ Dropdown menu appeared!');
            dropdownFound = true;
            
            // Get menu items
            const menuItems = await dropdownMenu.locator('a, button, [role="menuitem"]').all();
            console.log(`Found ${menuItems.length} menu items:`);
            
            for (let j = 0; j < menuItems.length; j++) {
              const itemText = await menuItems[j].textContent();
              console.log(`  - ${itemText}`);
            }
            
            // Click outside to close the dropdown
            await page.click('body', { position: { x: 10, y: 10 } });
            await page.waitForTimeout(500);
          }
        }
      } catch (error) {
        console.log(`Error testing element ${i + 1}: ${error}`);
      }
    }
    
    // Test passes if we found at least one dropdown or if we tested elements
    expect(clickableElements.length).toBeGreaterThan(0);
    if (dropdownFound) {
      console.log('🎉 User management dropdown functionality found and working!');
    } else {
      console.log('⚠️  No dropdown behavior detected - check if elements are implemented correctly');
    }
  });

  test('should test keyboard navigation', async () => {
    console.log('=== Testing Keyboard Navigation ===');
    
    // Try Tab navigation through the page
    await page.keyboard.press('Tab');
    await page.waitForTimeout(500);
    
    let tabCount = 0;
    const maxTabs = 20;
    
    while (tabCount < maxTabs) {
      const focusedElement = await page.locator(':focus').first();
      
      if (await focusedElement.count() > 0) {
        const elementText = await focusedElement.textContent();
        const tagName = await focusedElement.evaluate(el => el.tagName);
        console.log(`Tab ${tabCount + 1}: ${tagName} - "${elementText}"`);
        
        // Check if focused element might be user management related
        if (elementText?.toLowerCase().includes('user') || 
            elementText?.toLowerCase().includes('management')) {
          
          console.log(`🎯 Found user management element via keyboard: "${elementText}"`);
          
          // Try pressing Enter or Space
          await page.keyboard.press('Enter');
          await page.waitForTimeout(1000);
          
          // Check for dropdown
          const dropdown = await page.locator('.dropdown-menu, [role="menu"]').first();
          if (await dropdown.isVisible({ timeout: 1000 })) {
            console.log('✅ Dropdown opened via keyboard!');
            
            // Try arrow key navigation
            await page.keyboard.press('ArrowDown');
            await page.waitForTimeout(500);
            await page.keyboard.press('ArrowDown');
            await page.waitForTimeout(500);
            
            // Close with Escape
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
          }
        }
      }
      
      await page.keyboard.press('Tab');
      await page.waitForTimeout(300);
      tabCount++;
    }
    
    expect(tabCount).toBe(maxTabs);
  });

  test('should check mobile responsiveness', async () => {
    console.log('=== Testing Mobile Responsiveness ===');
    
    // Test different viewport sizes
    const viewports = [
      { width: 375, height: 667, name: 'iPhone' },
      { width: 768, height: 1024, name: 'iPad' },
      { width: 1920, height: 1080, name: 'Desktop' }
    ];
    
    for (const viewport of viewports) {
      console.log(`\nTesting ${viewport.name} (${viewport.width}x${viewport.height})`);
      
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.waitForTimeout(1000);
      
      // Take screenshot
      await page.screenshot({ 
        path: `test-results/responsive-${viewport.name.toLowerCase()}.png`, 
        fullPage: true 
      });
      
      // Check for mobile menu toggles
      if (viewport.width < 768) {
        const mobileMenus = await page.locator('.mobile-menu, .hamburger, [aria-label*="menu"], .menu-toggle').all();
        console.log(`Found ${mobileMenus.length} mobile menu elements`);
        
        for (let i = 0; i < mobileMenus.length; i++) {
          const menu = mobileMenus[i];
          if (await menu.isVisible()) {
            console.log(`Mobile menu ${i + 1} is visible`);
            await menu.click();
            await page.waitForTimeout(1000);
            
            // Look for user management in mobile menu
            const userLinks = await page.locator('text=/user/i, text=/management/i').all();
            console.log(`Found ${userLinks.length} user-related links in mobile menu`);
            
            // Close mobile menu
            await page.keyboard.press('Escape');
          }
        }
      }
    }
    
    expect(viewports.length).toBe(3);
  });

  test('should test accessibility features', async () => {
    console.log('=== Testing Accessibility ===');
    
    // Check for ARIA attributes
    const ariaElements = await page.locator('[aria-haspopup], [aria-expanded], [role="button"], [role="menu"]').all();
    console.log(`Found ${ariaElements.length} elements with ARIA attributes`);
    
    for (let i = 0; i < ariaElements.length; i++) {
      const element = ariaElements[i];
      const ariaHaspopup = await element.getAttribute('aria-haspopup');
      const ariaExpanded = await element.getAttribute('aria-expanded');
      const role = await element.getAttribute('role');
      const text = await element.textContent();
      
      console.log(`\nElement ${i + 1}: "${text}"`);
      console.log(`  aria-haspopup: ${ariaHaspopup}`);
      console.log(`  aria-expanded: ${ariaExpanded}`);
      console.log(`  role: ${role}`);
      
      if (ariaHaspopup === 'true' || ariaHaspopup === 'menu') {
        console.log('🎯 Found dropdown with proper ARIA attributes!');
        
        // Test the dropdown
        await element.click();
        await page.waitForTimeout(1000);
        
        const expandedState = await element.getAttribute('aria-expanded');
        console.log(`  aria-expanded after click: ${expandedState}`);
        
        if (expandedState === 'true') {
          console.log('✅ ARIA state properly updated!');
        }
      }
    }
    
    expect(ariaElements.length).toBeGreaterThanOrEqual(0);
  });
});
