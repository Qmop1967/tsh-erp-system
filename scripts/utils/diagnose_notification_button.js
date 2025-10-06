// Enhanced Notification Button Diagnostic Script
// Run this in Chrome DevTools Console to diagnose and potentially fix the notification button

(async function diagnoseNotificationButton() {
  console.log('=== NOTIFICATION BUTTON DIAGNOSTIC ===\n');

  // Step 1: Find the notification button
  console.log('Step 1: Locating notification button...\n');

  // Try multiple methods to find the button
  const bellIcon = document.querySelector('svg.lucide-bell, [class*="lucide-bell"]');
  console.log('Bell icon found:', bellIcon ? '✓ YES' : '✗ NO');

  if (bellIcon) {
    console.log('Bell icon details:');
    console.log('  Parent element:', bellIcon.parentElement?.tagName);
    console.log('  Parent classes:', bellIcon.parentElement?.className);

    const button = bellIcon.closest('button');
    console.log('Closest button found:', button ? '✓ YES' : '✗ NO');

    if (button) {
      console.log('\nButton details:');
      console.log('  Tag:', button.tagName);
      console.log('  Type:', button.type);
      console.log('  Classes:', button.className);
      console.log('  Disabled:', button.disabled);
      console.log('  Has onclick:', button.onclick !== null);

      // Check for event listeners
      console.log('\nChecking for event listeners...');
      const listeners = getEventListeners(button);
      console.log('  Event listeners:', Object.keys(listeners).length > 0 ? Object.keys(listeners) : 'None');

      if (listeners.click) {
        console.log('  ✓ Click listener found:', listeners.click.length, 'handler(s)');
      } else {
        console.log('  ✗ NO click listener found');
      }

      // Check parent for dropdown
      console.log('\nChecking for dropdown container...');
      const parent = button.parentElement;
      console.log('  Parent tag:', parent?.tagName);
      console.log('  Parent classes:', parent?.className);
      console.log('  Has "relative" class:', parent?.classList.contains('relative'));

      // Look for dropdown
      const dropdown = parent?.querySelector('div[class*="absolute"]');
      console.log('  Dropdown found:', dropdown ? '✓ YES' : '✗ NO');

      if (dropdown) {
        console.log('\nDropdown details:');
        console.log('  Classes:', dropdown.className);
        console.log('  Display:', window.getComputedStyle(dropdown).display);
        console.log('  Visibility:', window.getComputedStyle(dropdown).visibility);
        console.log('  Children count:', dropdown.children.length);
      }

      // Test button functionality
      console.log('\n\nStep 2: Testing button click...\n');

      console.log('Simulating click event...');
      button.click();

      await new Promise(resolve => setTimeout(resolve, 200));

      if (dropdown) {
        const isVisible = window.getComputedStyle(dropdown).display !== 'none';
        console.log('Dropdown visible after click:', isVisible ? '✓ YES' : '✗ NO');

        if (!isVisible) {
          console.log('\n⚠ ISSUE DETECTED: Dropdown not showing after click');
          console.log('\nTrying to debug...');

          // Check if React state is working
          console.log('Checking React state management...');

          // Try clicking again
          console.log('\nRetrying click...');
          button.click();

          await new Promise(resolve => setTimeout(resolve, 300));

          const isVisibleNow = window.getComputedStyle(dropdown).display !== 'none';
          console.log('Dropdown visible after second click:', isVisibleNow ? '✓ YES' : '✗ NO');
        }
      }

      // Check z-index
      console.log('\n\nStep 3: Checking z-index and positioning...\n');
      if (dropdown) {
        const styles = window.getComputedStyle(dropdown);
        console.log('  Position:', styles.position);
        console.log('  Z-index:', styles.zIndex);
        console.log('  Top:', styles.top);
        console.log('  Right:', styles.right);
        console.log('  Left:', styles.left);
      }

      // Summary
      console.log('\n\n=== DIAGNOSTIC SUMMARY ===');
      console.log('Button found:', '✓');
      console.log('Button enabled:', !button.disabled ? '✓' : '✗');
      console.log('Has event listener:', listeners?.click ? '✓' : '✗');
      console.log('Dropdown found:', dropdown ? '✓' : '✗');
      console.log('Dropdown working:', dropdown && window.getComputedStyle(dropdown).display !== 'none' ? '✓' : '✗');

      // Provide fix if needed
      if (dropdown && window.getComputedStyle(dropdown).display === 'none') {
        console.log('\n\n=== ATTEMPTING FIX ===');
        console.log('Manually showing dropdown for testing...');
        dropdown.style.display = 'block';
        console.log('✓ Dropdown force-shown. If you can see it now, the issue is with the React state management.');

        setTimeout(() => {
          dropdown.style.display = '';
          console.log('Reset dropdown display style');
        }, 3000);
      }

    } else {
      console.log('✗ Could not find button element');
    }
  } else {
    console.log('✗ Bell icon not found in DOM');
    console.log('\nSearching for any notification-related elements...');

    const notifElements = document.querySelectorAll('[class*="notif"], [class*="bell"]');
    console.log('Found', notifElements.length, 'notification-related elements');

    notifElements.forEach((el, i) => {
      console.log(`[${i + 1}]`, el.tagName, el.className);
    });
  }

  return 'Diagnostic complete';
})();
