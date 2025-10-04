// Simple Notification Button Test
// Copy ENTIRE content and paste into Chrome DevTools Console

console.clear();
console.log('=== NOTIFICATION BUTTON TEST ===\n');

// Find bell icon
const bell = document.querySelector('[class*="lucide-bell"]');
console.log('1. Bell icon found:', bell ? 'YES ✓' : 'NO ✗');

if (bell) {
  // Find button
  const btn = bell.closest('button');
  console.log('2. Button found:', btn ? 'YES ✓' : 'NO ✗');

  if (btn) {
    console.log('3. Button disabled:', btn.disabled);
    console.log('4. Button classes:', btn.className);

    // Find parent div
    const parent = btn.parentElement;
    console.log('5. Parent is relative:', parent?.classList.contains('relative'));

    // Find dropdown
    const dropdown = parent?.querySelector('[class*="absolute"]');
    console.log('6. Dropdown found:', dropdown ? 'YES ✓' : 'NO ✗');

    if (dropdown) {
      console.log('7. Dropdown classes:', dropdown.className);

      // Test click
      console.log('\n--- Testing Click ---');
      btn.click();

      setTimeout(() => {
        const visible = dropdown.style.display !== 'none' &&
                       !dropdown.classList.contains('hidden');
        console.log('8. Dropdown visible after click:', visible ? 'YES ✓' : 'NO ✗');

        if (!visible) {
          console.log('\n⚠️ ISSUE: Dropdown not showing');
          console.log('Dropdown element:', dropdown);
          console.log('React might not have loaded the component');
        }
      }, 300);
    }
  }
} else {
  console.log('⚠️ Bell icon not found in DOM');
  console.log('The Header component may not be rendered');
}
