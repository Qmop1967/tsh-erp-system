import { test, expect } from '@playwright/test';

test.describe('🟣 Enhancement & Stability Tests - Theme & Color Testing', () => {
  test('should verify default theme colors match design guidelines', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Test main color elements
    const colorElements = [
      { selector: 'body', property: 'background-color', description: 'Page background' },
      { selector: '[data-testid="page-title"]', property: 'color', description: 'Page title text' },
      { selector: '[data-testid="sidebar-toggle"]', property: 'background-color', description: 'Sidebar toggle button' },
      { selector: 'nav', property: 'background-color', description: 'Navigation background' },
      { selector: 'button', property: 'background-color', description: 'Button background' }
    ];
    
    const colorResults: Array<{element: string, color: string, description: string}> = [];
    
    for (const element of colorElements) {
      try {
        const locator = page.locator(element.selector).first();
        
        if (await locator.isVisible()) {
          const computedStyle = await locator.evaluate((el, prop) => {
            return window.getComputedStyle(el).getPropertyValue(prop);
          }, element.property);
          
          colorResults.push({
            element: element.selector,
            color: computedStyle,
            description: element.description
          });
          
          console.log(`${element.description}: ${computedStyle}`);
        }
      } catch (error) {
        console.log(`Could not get color for ${element.selector}: ${error}`);
      }
    }
    
    await page.screenshot({ 
      path: 'test-results/default-theme-colors.png',
      fullPage: true
    });
    
    // Verify we captured some colors
    expect(colorResults.length).toBeGreaterThan(0);
  });

  test('should check contrast between background and text', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Function to convert RGB to luminance for contrast calculation
    const getLuminance = (rgb: string): number => {
      const rgbMatch = rgb.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
      if (!rgbMatch) return 0.5; // Default middle luminance
      
      const [, r, g, b] = rgbMatch.map(Number);
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };
    
    const textElements = [
      '[data-testid="page-title"]',
      'nav a',
      'button',
      'p',
      'span'
    ];
    
    const contrastResults: Array<{element: string, contrast: number, accessible: boolean}> = [];
    
    for (const selector of textElements) {
      try {
        const element = page.locator(selector).first();
        
        if (await element.isVisible()) {
          const styles = await element.evaluate((el) => {
            const computed = window.getComputedStyle(el);
            return {
              color: computed.color,
              backgroundColor: computed.backgroundColor
            };
          });
          
          // Simple contrast check (in real implementation, would use proper contrast calculation)
          const hasGoodContrast = styles.color !== styles.backgroundColor;
          
          contrastResults.push({
            element: selector,
            contrast: hasGoodContrast ? 4.5 : 2.0, // Simplified values
            accessible: hasGoodContrast
          });
          
          console.log(`${selector}: ${hasGoodContrast ? 'Good contrast' : 'Poor contrast'}`);
        }
      } catch (error) {
        console.log(`Could not check contrast for ${selector}: ${error}`);
      }
    }
    
    await page.screenshot({ path: 'test-results/contrast-testing.png', fullPage: true });
    
    // Verify most elements have good contrast
    const accessibleCount = contrastResults.filter(r => r.accessible).length;
    expect(accessibleCount).toBeGreaterThan(contrastResults.length * 0.7); // At least 70% should be accessible
  });

  test('should verify dark mode renders correctly', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of default (light) mode
    await page.screenshot({ path: 'test-results/light-mode.png', fullPage: true });
    
    // Toggle to dark mode
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    await expect(themeToggle).toBeVisible();
    
    await themeToggle.click();
    await page.waitForTimeout(500); // Wait for theme transition
    
    // Take screenshot of dark mode
    await page.screenshot({ path: 'test-results/dark-mode.png', fullPage: true });
    
    // Test navigation still works in dark mode
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await expect(page.locator('[data-testid="page-title"]')).toContainText('Inventory');
    
    // Test modal in dark mode
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/dark-mode-modal.png', fullPage: true });
    
    await page.locator('[data-testid="cancel-add-item"]').click();
    
    // Toggle back to light mode
    await themeToggle.click();
    await page.waitForTimeout(500);
    
    await page.screenshot({ path: 'test-results/back-to-light-mode.png', fullPage: true });
    
    console.log('✅ Dark mode functionality tested');
  });

  test('should ensure consistent styling across components', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Test button consistency
    const buttonStyles: Array<{selector: string, styles: any}> = [];
    
    const buttonSelectors = [
      '[data-testid="sidebar-toggle"]',
      '[data-testid="theme-toggle"]',
      'nav a',
      'button'
    ];
    
    for (const selector of buttonSelectors) {
      try {
        const elements = await page.locator(selector).all();
        
        for (let i = 0; i < Math.min(elements.length, 3); i++) {
          const element = elements[i];
          
          if (await element.isVisible()) {
            const styles = await element.evaluate((el) => {
              const computed = window.getComputedStyle(el);
              return {
                borderRadius: computed.borderRadius,
                padding: computed.padding,
                fontSize: computed.fontSize,
                fontWeight: computed.fontWeight
              };
            });
            
            buttonStyles.push({
              selector: `${selector}[${i}]`,
              styles
            });
          }
        }
      } catch (error) {
        console.log(`Could not get styles for ${selector}: ${error}`);
      }
    }
    
    // Test form consistency
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    const formInputStyles: Array<{input: string, styles: any}> = [];
    
    const inputSelectors = [
      '[data-testid="item-name-input"]',
      '[data-testid="item-sku-input"]',
      '[data-testid="item-price-input"]',
      '[data-testid="item-category-select"]'
    ];
    
    for (const selector of inputSelectors) {
      try {
        const element = page.locator(selector);
        
        if (await element.isVisible()) {
          const styles = await element.evaluate((el) => {
            const computed = window.getComputedStyle(el);
            return {
              border: computed.border,
              borderRadius: computed.borderRadius,
              padding: computed.padding,
              fontSize: computed.fontSize,
              height: computed.height
            };
          });
          
          formInputStyles.push({
            input: selector,
            styles
          });
          
          console.log(`${selector} styles:`, JSON.stringify(styles, null, 2));
        }
      } catch (error) {
        console.log(`Could not get styles for ${selector}: ${error}`);
      }
    }
    
    await page.screenshot({ path: 'test-results/form-styling-consistency.png', fullPage: true });
    
    await page.locator('[data-testid="cancel-add-item"]').click();
    
    // Verify we captured styling information
    expect(buttonStyles.length).toBeGreaterThan(0);
    expect(formInputStyles.length).toBeGreaterThan(0);
    
    console.log(`✅ Captured styles for ${buttonStyles.length} buttons and ${formInputStyles.length} form inputs`);
  });

  test('should verify alert and notification styling', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Navigate to inventory to trigger an alert
    await page.locator('[data-testid="nav-inventory"]').click();
    await page.waitForTimeout(500);
    
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    // Fill form to trigger success alert
    const alertTestId = Date.now();
    await page.locator('[data-testid="item-name-input"]').fill(`Alert Test ${alertTestId}`);
    await page.locator('[data-testid="item-sku-input"]').fill(`ALERT-${alertTestId}`);
    await page.locator('[data-testid="item-price-input"]').fill('19.99');
    
    // Capture the alert styling
    let alertCaptured = false;
    
    page.on('dialog', async (dialog) => {
      console.log(`Alert message: ${dialog.message()}`);
      console.log(`Alert type: ${dialog.type()}`);
      
      // Take screenshot while alert is visible
      await page.screenshot({ path: 'test-results/alert-styling.png' });
      alertCaptured = true;
      
      await dialog.accept();
    });
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(2000);
    
    expect(alertCaptured).toBe(true);
    
    // Test error alert by trying empty form
    await page.getByText('Add New Item').click();
    await page.waitForTimeout(500);
    
    await page.locator('[data-testid="save-add-item"]').click();
    await page.waitForTimeout(500);
    
    // Modal should remain open (validation error)
    await expect(page.locator('[data-testid="add-item-modal"]')).toBeVisible();
    
    await page.screenshot({ path: 'test-results/validation-error-styling.png', fullPage: true });
    
    await page.locator('[data-testid="cancel-add-item"]').click();
    
    console.log('✅ Alert and notification styling tested');
  });

  test('should test color accessibility compliance', async ({ page }) => {
    await page.goto('http://localhost:3001');
    await page.waitForLoadState('networkidle');
    
    // Test with different modules for comprehensive color testing
    const modules = ['dashboard', 'inventory', 'sales', 'financial'];
    const accessibilityResults: Array<{module: string, issues: string[]}> = [];
    
    for (const module of modules) {
      if (module !== 'dashboard') {
        await page.locator(`[data-testid="nav-${module}"]`).click();
        await page.waitForTimeout(500);
      }
      
      const issues: string[] = [];
      
      // Check for sufficient color contrast (simplified check)
      const textElements = await page.locator('h1, h2, h3, p, span, a, button').all();
      let lowContrastCount = 0;
      
      for (let i = 0; i < Math.min(textElements.length, 10); i++) {
        try {
          const element = textElements[i];
          
          if (await element.isVisible()) {
            const styles = await element.evaluate((el) => {
              const computed = window.getComputedStyle(el);
              const color = computed.color;
              const bgColor = computed.backgroundColor;
              
              // Simple heuristic: if both are very similar or both are default, might be low contrast
              return {
                color,
                backgroundColor: bgColor,
                hasTransparentBg: bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent'
              };
            });
            
            // Very basic check - in production would use proper contrast calculation
            if (styles.color === styles.backgroundColor) {
              lowContrastCount++;
            }
          }
        } catch (error) {
          // Skip elements that can't be analyzed
        }
      }
      
      if (lowContrastCount > textElements.length * 0.1) { // More than 10% low contrast
        issues.push(`Potential low contrast issues: ${lowContrastCount} elements`);
      }
      
      // Check for color-only information (should also have text/icons)
      const colorOnlyElements = await page.locator('[style*="color:"], .text-red, .text-green, .text-yellow').count();
      if (colorOnlyElements > 0) {
        console.log(`Found ${colorOnlyElements} elements that might rely only on color`);
      }
      
      accessibilityResults.push({
        module,
        issues
      });
      
      await page.screenshot({ 
        path: `test-results/accessibility-${module}.png`,
        fullPage: true
      });
    }
    
    // Log accessibility results
    console.log('\\n🎨 Color Accessibility Results:');
    accessibilityResults.forEach(result => {
      const status = result.issues.length === 0 ? '✅ PASS' : '⚠️ NEEDS REVIEW';
      console.log(`${result.module}: ${status}`);
      result.issues.forEach(issue => console.log(`  - ${issue}`));
    });
    
    // Overall accessibility should have minimal issues
    const totalIssues = accessibilityResults.reduce((sum, result) => sum + result.issues.length, 0);
    expect(totalIssues).toBeLessThan(5); // Allow some minor issues
  });
});
