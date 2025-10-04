// Chrome DevTools Test Script for Sale Module
// This script tests if the sale module is enabled, active, and all dropdown submenus work properly

(async function testSaleModule() {
  console.log('=== SALE MODULE TESTING ===\n');

  const results = {
    moduleFound: false,
    moduleActive: false,
    dropdowns: [],
    errors: []
  };

  try {
    // Test 1: Find Sale Module in Navigation
    console.log('Test 1: Searching for Sale Module...');

    const saleLinks = Array.from(document.querySelectorAll('a, button, [role="button"]'))
      .filter(el => {
        const text = el.textContent.toLowerCase();
        return text.includes('sale') && !text.includes('salesperson');
      });

    if (saleLinks.length > 0) {
      results.moduleFound = true;
      console.log(`✓ Found ${saleLinks.length} sale-related element(s)`);
      saleLinks.forEach((link, i) => {
        console.log(`  [${i + 1}] Text: "${link.textContent.trim()}"`);
        console.log(`      Tag: ${link.tagName}`);
        console.log(`      Classes: ${link.className}`);
        console.log(`      Href: ${link.href || 'N/A'}`);
      });
    } else {
      console.log('✗ No sale module found');
      results.errors.push('Sale module not found in navigation');
    }

    // Test 2: Check if module is visible and enabled
    console.log('\nTest 2: Checking Module Visibility & State...');

    for (let link of saleLinks) {
      const isVisible = link.offsetParent !== null;
      const isDisabled = link.disabled || link.hasAttribute('disabled') ||
                        link.classList.contains('disabled') ||
                        link.getAttribute('aria-disabled') === 'true';

      console.log(`  Element: "${link.textContent.trim()}"`);
      console.log(`    Visible: ${isVisible ? '✓ Yes' : '✗ No'}`);
      console.log(`    Enabled: ${!isDisabled ? '✓ Yes' : '✗ No'}`);

      if (isVisible && !isDisabled) {
        results.moduleActive = true;
      }
    }

    // Test 3: Find all dropdown menus related to Sale
    console.log('\nTest 3: Finding Sale Dropdowns & Submenus...');

    // Look for dropdown containers
    const dropdownSelectors = [
      '.dropdown',
      '[class*="dropdown"]',
      '[data-dropdown]',
      '.menu-item',
      '[role="menu"]',
      'nav ul li'
    ];

    const allDropdowns = new Set();
    dropdownSelectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(el => {
        if (el.textContent.toLowerCase().includes('sale') &&
            !el.textContent.toLowerCase().includes('salesperson')) {
          allDropdowns.add(el);
        }
      });
    });

    console.log(`Found ${allDropdowns.size} sale dropdown container(s)`);

    // Test 4: Test each dropdown
    console.log('\nTest 4: Testing Dropdown Functionality...');

    for (let dropdown of allDropdowns) {
      const dropdownTest = {
        element: dropdown.textContent.trim().substring(0, 50),
        hasSubmenu: false,
        submenuItems: [],
        clickable: false,
        expanded: false
      };

      // Find submenu
      const submenu = dropdown.querySelector('ul, .submenu, .dropdown-menu, [role="menu"]');
      if (submenu) {
        dropdownTest.hasSubmenu = true;
        const items = submenu.querySelectorAll('li, a, [role="menuitem"]');
        dropdownTest.submenuItems = Array.from(items).map(item => ({
          text: item.textContent.trim(),
          visible: item.offsetParent !== null,
          enabled: !item.disabled && !item.hasAttribute('disabled')
        }));
      }

      // Check if clickable
      const clickableElement = dropdown.querySelector('a, button, [role="button"]') || dropdown;
      dropdownTest.clickable = clickableElement.onclick !== null ||
                                clickableElement.href ||
                                clickableElement.tagName === 'BUTTON';

      // Check if expanded
      dropdownTest.expanded = dropdown.classList.contains('open') ||
                             dropdown.classList.contains('expanded') ||
                             dropdown.classList.contains('active') ||
                             dropdown.getAttribute('aria-expanded') === 'true';

      results.dropdowns.push(dropdownTest);

      console.log(`\n  Dropdown: "${dropdownTest.element}"`);
      console.log(`    Has Submenu: ${dropdownTest.hasSubmenu ? '✓ Yes' : '✗ No'}`);
      console.log(`    Clickable: ${dropdownTest.clickable ? '✓ Yes' : '✗ No'}`);
      console.log(`    Expanded: ${dropdownTest.expanded ? '✓ Yes' : '✗ No'}`);

      if (dropdownTest.submenuItems.length > 0) {
        console.log(`    Submenu Items (${dropdownTest.submenuItems.length}):`);
        dropdownTest.submenuItems.forEach((item, i) => {
          console.log(`      [${i + 1}] "${item.text.substring(0, 40)}"`);
          console.log(`          Visible: ${item.visible ? '✓' : '✗'}, Enabled: ${item.enabled ? '✓' : '✗'}`);
        });
      }
    }

    // Test 5: Simulate hover/click to test interactivity
    console.log('\n\nTest 5: Testing Dropdown Interactions...');

    for (let dropdown of allDropdowns) {
      const trigger = dropdown.querySelector('a, button, [role="button"]') || dropdown;

      console.log(`\n  Testing: "${trigger.textContent.trim().substring(0, 40)}"`);

      // Simulate mouseenter
      const mouseenterEvent = new MouseEvent('mouseenter', { bubbles: true });
      trigger.dispatchEvent(mouseenterEvent);

      await new Promise(resolve => setTimeout(resolve, 100));

      const submenu = dropdown.querySelector('ul, .submenu, .dropdown-menu');
      if (submenu) {
        const isVisibleAfterHover = submenu.offsetParent !== null ||
                                   window.getComputedStyle(submenu).display !== 'none';
        console.log(`    Submenu after hover: ${isVisibleAfterHover ? '✓ Visible' : '✗ Hidden'}`);
      }

      // Simulate click
      const clickEvent = new MouseEvent('click', { bubbles: true });
      trigger.dispatchEvent(clickEvent);

      await new Promise(resolve => setTimeout(resolve, 100));

      if (submenu) {
        const isVisibleAfterClick = submenu.offsetParent !== null ||
                                   window.getComputedStyle(submenu).display !== 'none';
        console.log(`    Submenu after click: ${isVisibleAfterClick ? '✓ Visible' : '✗ Hidden'}`);
      }
    }

    // Final Summary
    console.log('\n\n=== TEST SUMMARY ===');
    console.log(`Sale Module Found: ${results.moduleFound ? '✓ YES' : '✗ NO'}`);
    console.log(`Sale Module Active: ${results.moduleActive ? '✓ YES' : '✗ NO'}`);
    console.log(`Dropdowns Found: ${results.dropdowns.length}`);
    console.log(`Errors: ${results.errors.length}`);

    if (results.errors.length > 0) {
      console.log('\nErrors:');
      results.errors.forEach(err => console.log(`  - ${err}`));
    }

    // Return results for programmatic access
    return results;

  } catch (error) {
    console.error('Test failed with error:', error);
    results.errors.push(error.message);
    return results;
  }
})();
