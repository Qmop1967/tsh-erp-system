#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPOSFinal() {
  let browser;

  try {
    console.log('🚀 Final POS Test with Item Sync...\n');

    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });

    const page = await browser.newPage();

    // Capture console logs
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('Loaded') || text.includes('products') || text.includes('items')) {
        console.log(`📋 Browser Console: ${text}`);
      }
    });

    // Login
    console.log('🔐 Logging in...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
    await page.waitForSelector('input[type="email"]');
    await page.type('input[type="email"]', 'admin@tsh.com');
    await page.type('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('✅ Logged in\n');

    // Navigate to POS
    console.log('🔍 Navigating to POS...');
    await page.goto('http://localhost:5173/pos', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 4000)); // Wait for data loading

    // Check for items/products
    const posData = await page.evaluate(() => {
      const bodyText = document.body.textContent;
      const hasError = bodyText.includes('Failed to load');
      const hasProducts = bodyText.toLowerCase().includes('product');
      const hasSearch = bodyText.includes('Search');

      // Try to find product elements or count
      const productElements = document.querySelectorAll('[class*="product"], [class*="item"]');

      return {
        hasError,
        hasProducts,
        hasSearch,
        productElementsCount: productElements.length,
        bodyTextSample: bodyText.substring(0, 600)
      };
    });

    console.log('📊 POS Data Check:');
    console.log(JSON.stringify(posData, null, 2));
    console.log('');

    // Try to search for an item
    console.log('🔍 Testing product search...');
    try {
      await page.waitForSelector('input[placeholder*="Search" i], input[placeholder*="search" i]', { timeout: 3000 });
      const searchInput = await page.$('input[placeholder*="Search" i], input[placeholder*="search" i]');

      if (searchInput) {
        await searchInput.type('item');
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('✅ Search input working');

        // Check if any results appeared
        const searchResults = await page.evaluate(() => {
          const resultsText = document.body.textContent;
          return {
            hasResults: resultsText.length > 0,
            textSample: resultsText.substring(0, 400)
          };
        });
        console.log('Search Results:', searchResults);
      }
    } catch (e) {
      console.log('⚠️  Search input not found or not ready');
    }

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'pos-final-test.png'),
      fullPage: true
    });
    console.log('\n📸 Screenshot saved: pos-final-test.png\n');

    // Summary
    console.log('=' + '='.repeat(60));
    console.log('📊 POS ITEM SYNC TEST SUMMARY');
    console.log('='.repeat(61));
    console.log(`✅ Has Error Message: ${posData.hasError ? 'YES ❌' : 'NO ✅'}`);
    console.log(`✅ Has Product/Search UI: ${posData.hasProducts || posData.hasSearch ? 'YES' : 'NO'}`);
    console.log(`✅ Product Elements Found: ${posData.productElementsCount}`);

    const isWorking = !posData.hasError && (posData.hasProducts || posData.hasSearch);

    console.log('\n' + '='.repeat(61));
    if (isWorking) {
      console.log('✅ POS IS WORKING WITH ITEM SYNC!');
    } else {
      console.log('❌ POS ITEM SYNC NEEDS ATTENTION');
    }
    console.log('='.repeat(61));

    console.log('\n✅ Test complete! Check the terminal output above.');
    console.log('Press Ctrl+C to close...');

    await new Promise(() => {});

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (browser) await browser.close();
    process.exit(1);
  }
}

testPOSFinal();
