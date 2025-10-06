const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 1000
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  console.log('Navigating to TSH ERP System...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  console.log('Taking screenshot...');
  await page.screenshot({
    path: '/Users/khaleelal-mulla/TSH_ERP_System_Local/screenshots/homepage.png',
    fullPage: true
  });

  console.log('Opening DevTools Console...');
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text()
    });
  });

  // Get page title
  const title = await page.title();
  console.log('Page Title:', title);

  // Get page HTML
  const html = await page.content();
  console.log('Page HTML length:', html.length);

  // Check for JavaScript errors
  const errors = [];
  page.on('pageerror', error => {
    errors.push(error.message);
  });

  // Wait a bit to capture any console logs or errors
  await page.waitForTimeout(2000);

  console.log('\nConsole Messages:', JSON.stringify(consoleMessages, null, 2));
  console.log('\nJavaScript Errors:', errors.length > 0 ? errors : 'None');

  console.log('\nScreenshot saved to: /Users/khaleelal-mulla/TSH_ERP_System_Local/screenshots/homepage.png');

  await browser.close();
})();
