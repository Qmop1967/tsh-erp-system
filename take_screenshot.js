const puppeteer = require('puppeteer');

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false, // Set to true if you don't want to see the browser
    ignoreHTTPSErrors: true // Important for localhost with HTTPS
  });

  const page = await browser.newPage();
  
  // Set viewport size
  await page.setViewport({
    width: 1920,
    height: 1080
  });

  console.log('Navigating to https://localhost:5173...');
  
  try {
    await page.goto('https://localhost:5173', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('Page loaded successfully!');
    
    // Wait a bit for any animations to complete
    await page.waitForTimeout(1000);

    // Take screenshot
    const screenshotPath = './screenshot.png';
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log(`Screenshot saved to: ${screenshotPath}`);
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
    console.log('Browser closed.');
  }
})();
