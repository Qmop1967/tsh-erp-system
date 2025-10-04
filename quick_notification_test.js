console.clear();
console.log('=== NOTIFICATION BUTTON TEST ===');

// Find bell icon
const bell = document.querySelector('svg.lucide-bell');
console.log('Bell icon:', bell);

if (bell) {
  const btn = bell.closest('button');
  console.log('Button:', btn);
  console.log('Button disabled:', btn ? btn.disabled : 'N/A');

  if (btn) {
    const parent = btn.parentElement;
    console.log('Parent element:', parent);
    console.log('Parent has relative class:', parent ? parent.classList.contains('relative') : false);

    const allChildren = parent ? Array.from(parent.children) : [];
    console.log('Parent children count:', allChildren.length);

    allChildren.forEach((child, i) => {
      console.log('Child', i, ':', child.tagName, child.className);
    });

    // Try to click
    console.log('\nClicking button...');
    btn.click();

    setTimeout(() => {
      console.log('After click - checking children again:');
      const children = parent ? Array.from(parent.children) : [];
      children.forEach((child, i) => {
        console.log('Child', i, ':', child.tagName, 'visible:', child.offsetParent !== null);
      });
    }, 500);
  }
} else {
  console.log('ERROR: Bell icon not found!');
  console.log('Searching for ANY bell elements...');
  const allBells = document.querySelectorAll('[class*="bell"]');
  console.log('Found', allBells.length, 'elements with bell in class');
  allBells.forEach(el => console.log(el));
}
