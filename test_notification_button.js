// Chrome DevTools Test Script for Notification Button
// This script tests the notification button functionality on the dashboard

(async function testNotificationButton() {
  console.log('=== NOTIFICATION BUTTON TESTING ===\n');

  const results = {
    buttonFound: false,
    buttonVisible: false,
    buttonEnabled: false,
    hasIcon: false,
    hasBadge: false,
    badgeCount: 0,
    clickable: false,
    dropdownFound: false,
    dropdownWorks: false,
    notifications: [],
    errors: []
  };

  try {
    // Test 1: Find Notification Button
    console.log('Test 1: Searching for Notification Button...\n');

    const possibleSelectors = [
      '[data-testid*="notification"]',
      '[class*="notification"]',
      '[aria-label*="notification"]',
      'button[title*="notification"]',
      '.notification-btn',
      '.notifications',
      '[class*="bell"]',
      'svg[class*="bell"]'
    ];

    let notificationButton = null;

    for (let selector of possibleSelectors) {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        console.log(`✓ Found ${elements.length} element(s) with selector: ${selector}`);
        elements.forEach((el, i) => {
          const parent = el.closest('button, a, [role="button"]') || el;
          console.log(`  [${i + 1}] Tag: ${parent.tagName}, Class: "${parent.className}"`);
          if (!notificationButton) notificationButton = parent;
        });
      }
    }

    // Also search by text content
    const allButtons = document.querySelectorAll('button, a, [role="button"]');
    for (let btn of allButtons) {
      const text = btn.textContent.toLowerCase();
      const title = (btn.getAttribute('title') || '').toLowerCase();
      const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();

      if (text.includes('notification') || title.includes('notification') ||
          ariaLabel.includes('notification') || text.includes('🔔')) {
        if (!notificationButton) notificationButton = btn;
        console.log(`✓ Found button by text/attribute: "${btn.textContent.trim() || title || ariaLabel}"`);
      }
    }

    if (notificationButton) {
      results.buttonFound = true;
      console.log('\n✓ Notification button found!');
      console.log(`  Element: ${notificationButton.tagName}`);
      console.log(`  Class: "${notificationButton.className}"`);
      console.log(`  ID: "${notificationButton.id || 'N/A'}"`);
      console.log(`  Text: "${notificationButton.textContent.trim()}"`);
    } else {
      console.log('\n✗ Notification button NOT found');
      results.errors.push('Notification button not found');
      return results;
    }

    // Test 2: Check Button Visibility
    console.log('\n\nTest 2: Checking Button Visibility...\n');

    const isVisible = notificationButton.offsetParent !== null;
    const computedStyle = window.getComputedStyle(notificationButton);
    const displayStyle = computedStyle.display;
    const visibilityStyle = computedStyle.visibility;
    const opacityStyle = computedStyle.opacity;

    results.buttonVisible = isVisible && displayStyle !== 'none' && visibilityStyle !== 'hidden';

    console.log(`  Visible: ${results.buttonVisible ? '✓ Yes' : '✗ No'}`);
    console.log(`  Display: ${displayStyle}`);
    console.log(`  Visibility: ${visibilityStyle}`);
    console.log(`  Opacity: ${opacityStyle}`);

    // Test 3: Check Button State
    console.log('\n\nTest 3: Checking Button State...\n');

    const isDisabled = notificationButton.disabled ||
                      notificationButton.hasAttribute('disabled') ||
                      notificationButton.classList.contains('disabled') ||
                      notificationButton.getAttribute('aria-disabled') === 'true';

    results.buttonEnabled = !isDisabled;

    console.log(`  Enabled: ${results.buttonEnabled ? '✓ Yes' : '✗ No'}`);
    console.log(`  Disabled attribute: ${notificationButton.disabled || notificationButton.hasAttribute('disabled') ? 'Yes' : 'No'}`);
    console.log(`  Has 'disabled' class: ${notificationButton.classList.contains('disabled') ? 'Yes' : 'No'}`);

    // Test 4: Check for Icon
    console.log('\n\nTest 4: Checking for Notification Icon...\n');

    const icon = notificationButton.querySelector('svg, i, img, [class*="icon"]');
    results.hasIcon = icon !== null;

    console.log(`  Has Icon: ${results.hasIcon ? '✓ Yes' : '✗ No'}`);
    if (icon) {
      console.log(`  Icon Type: ${icon.tagName}`);
      console.log(`  Icon Class: "${icon.className}"`);
    }

    // Test 5: Check for Badge/Count
    console.log('\n\nTest 5: Checking for Notification Badge/Count...\n');

    const badge = notificationButton.querySelector('.badge, [class*="badge"], [class*="count"], [class*="dot"]') ||
                  document.querySelector('[class*="notification"] .badge, [class*="notification"] [class*="count"]');

    results.hasBadge = badge !== null;

    if (badge) {
      const badgeText = badge.textContent.trim();
      results.badgeCount = parseInt(badgeText) || 0;
      console.log(`  Has Badge: ✓ Yes`);
      console.log(`  Badge Text: "${badgeText}"`);
      console.log(`  Badge Count: ${results.badgeCount}`);
      console.log(`  Badge Class: "${badge.className}"`);
    } else {
      console.log(`  Has Badge: ✗ No`);
    }

    // Test 6: Check Click Functionality
    console.log('\n\nTest 6: Testing Click Functionality...\n');

    results.clickable = notificationButton.onclick !== null ||
                       notificationButton.href ||
                       notificationButton.tagName === 'BUTTON';

    console.log(`  Clickable: ${results.clickable ? '✓ Yes' : '✗ No'}`);
    console.log(`  Has onclick handler: ${notificationButton.onclick !== null ? 'Yes' : 'No'}`);
    console.log(`  Has href: ${notificationButton.href ? 'Yes' : 'No'}`);

    // Test 7: Look for Dropdown/Panel
    console.log('\n\nTest 7: Searching for Notification Dropdown/Panel...\n');

    const dropdownSelectors = [
      '.notification-dropdown',
      '.notification-panel',
      '.notifications-menu',
      '[class*="notification"][class*="dropdown"]',
      '[class*="notification"][class*="panel"]',
      '[class*="notification"][class*="menu"]',
      '[role="menu"]',
      '[aria-labelledby]'
    ];

    let dropdown = null;
    for (let selector of dropdownSelectors) {
      const el = document.querySelector(selector);
      if (el) {
        dropdown = el;
        console.log(`✓ Found dropdown with selector: ${selector}`);
        break;
      }
    }

    // Also check next sibling
    if (!dropdown && notificationButton.nextElementSibling) {
      const next = notificationButton.nextElementSibling;
      if (next.classList.toString().includes('dropdown') ||
          next.classList.toString().includes('menu') ||
          next.classList.toString().includes('panel')) {
        dropdown = next;
        console.log('✓ Found dropdown as next sibling');
      }
    }

    // Check parent container for dropdown
    if (!dropdown) {
      const parent = notificationButton.parentElement;
      dropdown = parent?.querySelector('.dropdown, .menu, .panel, [role="menu"]');
      if (dropdown) {
        console.log('✓ Found dropdown in parent container');
      }
    }

    results.dropdownFound = dropdown !== null;

    if (dropdown) {
      console.log(`  Dropdown Class: "${dropdown.className}"`);
      console.log(`  Dropdown ID: "${dropdown.id || 'N/A'}"`);

      const dropdownVisible = dropdown.offsetParent !== null ||
                             window.getComputedStyle(dropdown).display !== 'none';
      console.log(`  Currently Visible: ${dropdownVisible ? 'Yes' : 'No'}`);

      // Find notification items
      const items = dropdown.querySelectorAll('[class*="notification-item"], li, [role="menuitem"]');
      console.log(`  Notification Items: ${items.length}`);

      items.forEach((item, i) => {
        const notif = {
          text: item.textContent.trim().substring(0, 60),
          read: item.classList.contains('read') || !item.classList.contains('unread'),
          visible: item.offsetParent !== null
        };
        results.notifications.push(notif);
        console.log(`    [${i + 1}] ${notif.text}... (${notif.read ? 'Read' : 'Unread'})`);
      });
    } else {
      console.log('✗ No dropdown/panel found');
    }

    // Test 8: Simulate Click to Test Dropdown
    console.log('\n\nTest 8: Testing Dropdown Interaction...\n');

    if (results.buttonEnabled && results.buttonVisible) {
      console.log('Simulating click on notification button...');

      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
      });

      notificationButton.dispatchEvent(clickEvent);

      // Wait for animation/transition
      await new Promise(resolve => setTimeout(resolve, 300));

      if (dropdown) {
        const dropdownVisibleAfterClick = dropdown.offsetParent !== null ||
                                         window.getComputedStyle(dropdown).display !== 'none' ||
                                         dropdown.classList.contains('show') ||
                                         dropdown.classList.contains('open');

        results.dropdownWorks = dropdownVisibleAfterClick;

        console.log(`  Dropdown after click: ${dropdownVisibleAfterClick ? '✓ Visible' : '✗ Hidden'}`);
        console.log(`  Dropdown has 'show' class: ${dropdown.classList.contains('show') ? 'Yes' : 'No'}`);
        console.log(`  Dropdown has 'open' class: ${dropdown.classList.contains('open') ? 'Yes' : 'No'}`);
      } else {
        console.log('  No dropdown to test');
      }
    } else {
      console.log('✗ Button not enabled or visible, skipping click test');
    }

    // Final Summary
    console.log('\n\n=== TEST SUMMARY ===');
    console.log(`Button Found: ${results.buttonFound ? '✓ YES' : '✗ NO'}`);
    console.log(`Button Visible: ${results.buttonVisible ? '✓ YES' : '✗ NO'}`);
    console.log(`Button Enabled: ${results.buttonEnabled ? '✓ YES' : '✗ NO'}`);
    console.log(`Has Icon: ${results.hasIcon ? '✓ YES' : '✗ NO'}`);
    console.log(`Has Badge: ${results.hasBadge ? '✓ YES' : '✗ NO'}`);
    if (results.hasBadge) {
      console.log(`Badge Count: ${results.badgeCount}`);
    }
    console.log(`Clickable: ${results.clickable ? '✓ YES' : '✗ NO'}`);
    console.log(`Dropdown Found: ${results.dropdownFound ? '✓ YES' : '✗ NO'}`);
    console.log(`Dropdown Works: ${results.dropdownWorks ? '✓ YES' : '✗ NO'}`);
    console.log(`Notifications: ${results.notifications.length}`);
    console.log(`Errors: ${results.errors.length}`);

    if (results.errors.length > 0) {
      console.log('\nErrors:');
      results.errors.forEach(err => console.log(`  - ${err}`));
    }

    console.log('\n=== RECOMMENDATIONS ===');
    if (!results.buttonFound) {
      console.log('⚠ Notification button not found. Check if it exists in the DOM.');
    }
    if (results.buttonFound && !results.buttonVisible) {
      console.log('⚠ Button found but not visible. Check CSS display/visibility properties.');
    }
    if (results.buttonFound && !results.buttonEnabled) {
      console.log('⚠ Button found but disabled. Check disabled attributes and classes.');
    }
    if (results.dropdownFound && !results.dropdownWorks) {
      console.log('⚠ Dropdown found but not working. Check click handlers and CSS transitions.');
    }

    return results;

  } catch (error) {
    console.error('Test failed with error:', error);
    results.errors.push(error.message);
    return results;
  }
})();
