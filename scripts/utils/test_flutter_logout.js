// Flutter App Logout Test for Chrome DevTools Console
// Run this in the Flutter app's Chrome window

console.clear();
console.log('=== FLUTTER LOGOUT TEST ===\n');

// Step 1: Check if we're on login or home page
console.log('Step 1: Checking current page...');
const currentUrl = window.location.href;
console.log('Current URL:', currentUrl);
console.log('Current Path:', window.location.hash);

// Step 2: Check localStorage for auth data
console.log('\nStep 2: Checking localStorage for auth data...');
const keys = Object.keys(localStorage);
console.log('All localStorage keys:', keys);

const authKeys = keys.filter(k => k.includes('auth') || k.includes('token') || k.includes('user'));
console.log('Auth-related keys:', authKeys);

authKeys.forEach(key => {
  const value = localStorage.getItem(key);
  console.log(`  ${key}:`, value?.substring(0, 100));
});

// Step 3: Find logout button
console.log('\nStep 3: Looking for logout button...');

// In Flutter web, elements are rendered in a canvas/shadow DOM
// We need to use Flutter's element tree

// Try to find elements with logout-related text
const findLogoutButton = () => {
  // Flutter renders text as flt-semantics elements
  const allElements = document.querySelectorAll('*');
  const logoutElements = [];

  allElements.forEach(el => {
    const text = el.textContent || el.innerText || '';
    if (text.includes('خروج') || text.includes('logout') || text.includes('sign out')) {
      logoutElements.push({
        element: el,
        text: text.trim().substring(0, 50),
        tag: el.tagName,
        classes: el.className
      });
    }
  });

  return logoutElements;
};

const logoutButtons = findLogoutButton();
console.log('Found', logoutButtons.length, 'logout-related elements:');
logoutButtons.forEach((btn, i) => {
  console.log(`  [${i}] ${btn.tag}.${btn.classes}: "${btn.text}"`);
});

// Step 4: Check for Flutter semantic elements
console.log('\nStep 4: Checking Flutter semantic tree...');
const semanticNodes = document.querySelectorAll('flt-semantics');
console.log('Total semantic nodes:', semanticNodes.length);

const menuButtons = document.querySelectorAll('flt-semantics[role="button"]');
console.log('Button semantic nodes:', menuButtons.length);

// Step 5: Try to find and click logout programmatically
console.log('\nStep 5: Attempting to trigger logout...');

// Check if there's a menu/settings icon to click first
const menuIcons = Array.from(semanticNodes).filter(node => {
  const ariaLabel = node.getAttribute('aria-label');
  return ariaLabel && (ariaLabel.includes('menu') || ariaLabel.includes('القائمة'));
});

console.log('Menu icons found:', menuIcons.length);
if (menuIcons.length > 0) {
  console.log('Menu icon aria-labels:');
  menuIcons.forEach((icon, i) => {
    console.log(`  [${i}] ${icon.getAttribute('aria-label')}`);
  });
}

// Step 6: Manual test instructions
console.log('\n\n=== MANUAL TEST INSTRUCTIONS ===');
console.log('1. Navigate to the Menu/القائمة tab');
console.log('2. Scroll to bottom and click "تسجيل الخروج" (Logout)');
console.log('3. Click confirm in the dialog');
console.log('4. Check if you are redirected to login page');
console.log('5. Check if localStorage is cleared:');
console.log('   - Run: localStorage.getItem("flutter.auth_token")');
console.log('   - Should return: null');

// Step 7: Create helper function to monitor logout
console.log('\n\n=== HELPER FUNCTION ===');
console.log('Use this to monitor logout:');
console.log(`
window.monitorLogout = function() {
  console.log('Monitoring logout...');
  const originalClear = localStorage.clear;
  const originalRemove = localStorage.removeItem;

  localStorage.clear = function() {
    console.log('✓ localStorage.clear() called');
    return originalClear.apply(this, arguments);
  };

  localStorage.removeItem = function(key) {
    console.log('✓ localStorage.removeItem("' + key + '") called');
    return originalRemove.apply(this, arguments);
  };

  // Watch for URL changes
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  history.pushState = function() {
    console.log('✓ Navigation:', arguments[2]);
    return originalPushState.apply(this, arguments);
  };

  history.replaceState = function() {
    console.log('✓ Navigation (replace):', arguments[2]);
    return originalReplaceState.apply(this, arguments);
  };

  console.log('✓ Monitoring enabled. Now try to logout.');
};

// Auto-enable monitoring
window.monitorLogout();
`);

window.monitorLogout = function() {
  console.log('\n📊 Logout monitoring enabled!');
  const originalClear = localStorage.clear;
  const originalRemove = localStorage.removeItem;

  localStorage.clear = function() {
    console.log('✓ localStorage.clear() called');
    return originalClear.apply(this, arguments);
  };

  localStorage.removeItem = function(key) {
    console.log('✓ localStorage.removeItem("' + key + '") called');
    return originalRemove.apply(this, arguments);
  };

  // Watch for URL changes
  window.addEventListener('hashchange', function() {
    console.log('✓ URL hash changed to:', window.location.hash);
  });

  console.log('✓ Ready! Now try to logout and watch the console.');
};

// Enable monitoring
window.monitorLogout();

console.log('\n=== TEST READY ===');
console.log('Now click logout and watch this console for activity!');
