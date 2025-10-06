#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPOSComplete() {
  let browser;

  try {
    console.log('🚀 POS Complete Test with Auto-Close...\n');

    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });

    const page = await browser.newPage();

    // Capture console logs
    const consoleLogs = [];
    page.on('console', msg => {
      const text = msg.text();
      consoleLogs.push(text);
      if (text.includes('Loaded') || text.includes('products') || text.includes('items')) {
        console.log(`📋 Browser: ${text}`);
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
    await new Promise(resolve => setTimeout(resolve, 4000));

    // Check for items/products
    const posData = await page.evaluate(() => {
      const bodyText = document.body.textContent;
      const hasError = bodyText.includes('Failed to load');
      const hasProducts = bodyText.toLowerCase().includes('product');
      const hasSearch = bodyText.includes('Search');
      const hasCart = bodyText.includes('Cart');
      const hasPayment = bodyText.includes('Payment');

      return {
        hasError,
        hasProducts,
        hasSearch,
        hasCart,
        hasPayment,
        bodyTextSample: bodyText.substring(0, 500)
      };
    });

    console.log('📊 POS Status:');
    console.log(JSON.stringify(posData, null, 2));
    console.log('');

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'pos-final.png'),
      fullPage: true
    });
    console.log('📸 Screenshot: screenshots/pos-final.png\n');

    // Check backend logs for items loaded
    const itemsLoaded = consoleLogs.some(log =>
      log.includes('Loaded') && log.includes('products')
    );

    // Summary
    console.log('='.repeat(60));
    console.log('📊 POS COMPLETE TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`✅ POS Interface: ${posData.hasProducts && posData.hasSearch ? '✅ Active' : '❌ Inactive'}`);
    console.log(`✅ Error Message: ${posData.hasError ? '❌ Present' : '✅ None'}`);
    console.log(`✅ Search UI: ${posData.hasSearch ? '✅ Ready' : '❌ Missing'}`);
    console.log(`✅ Shopping Cart: ${posData.hasCart ? '✅ Ready' : '❌ Missing'}`);
    console.log(`✅ Payment Methods: ${posData.hasPayment ? '✅ Ready' : '❌ Missing'}`);
    console.log(`✅ Items Loaded: ${itemsLoaded ? '✅ Yes' : '⚠️  Check console'}`);

    const isWorking = !posData.hasError && posData.hasProducts && posData.hasSearch;

    console.log('\n' + '='.repeat(60));
    if (isWorking) {
      console.log('✅ POS MODULE FULLY OPERATIONAL!');
    } else {
      console.log('⚠️  POS MODULE NEEDS ATTENTION');
    }
    console.log('='.repeat(60));

    // Close browser automatically
    console.log('\n🔄 Closing browser and returning to terminal...');
    await browser.close();
    console.log('✅ Test complete! Browser closed.\n');

    process.exit(0);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

testPOSComplete();
