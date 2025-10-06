#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPOSActive() {
  let browser;

  try {
    console.log('🚀 Testing Activated POS Module...\n');

    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });

    const page = await browser.newPage();

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
    console.log('🔍 Navigating to /pos...');
    await page.goto('http://localhost:5173/pos', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Check page content
    const posPageInfo = await page.evaluate(() => {
      const bodyText = document.body.textContent;

      return {
        currentUrl: window.location.href,
        hasPOS: bodyText.toLowerCase().includes('point of sale') || bodyText.toLowerCase().includes('pos'),
        hasComingSoon: bodyText.includes('Coming Soon') || bodyText.includes('coming soon'),
        hasCart: bodyText.toLowerCase().includes('cart') || bodyText.toLowerCase().includes('shopping'),
        hasProducts: bodyText.toLowerCase().includes('product') || bodyText.toLowerCase().includes('search'),
        hasPayment: bodyText.toLowerCase().includes('payment') || bodyText.toLowerCase().includes('cash'),
        hasTotal: bodyText.toLowerCase().includes('total') || bodyText.toLowerCase().includes('subtotal'),
        bodyTextSample: bodyText.substring(0, 500)
      };
    });

    console.log('📊 POS Page Info:');
    console.log(JSON.stringify(posPageInfo, null, 2));
    console.log('');

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'pos-active.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved: pos-active.png\n');

    // Summary
    console.log('📊 POS MODULE ACTIVATION TEST');
    console.log('==============================');
    console.log(`✅ Current URL: ${posPageInfo.currentUrl}`);
    console.log(`✅ Has "Coming Soon": ${posPageInfo.hasComingSoon ? 'YES ❌' : 'NO ✅'}`);
    console.log(`✅ Has POS content: ${posPageInfo.hasPOS ? 'YES' : 'NO'}`);
    console.log(`✅ Has Cart: ${posPageInfo.hasCart ? 'YES' : 'NO'}`);
    console.log(`✅ Has Products: ${posPageInfo.hasProducts ? 'YES' : 'NO'}`);
    console.log(`✅ Has Payment: ${posPageInfo.hasPayment ? 'YES' : 'NO'}`);
    console.log(`✅ Has Total: ${posPageInfo.hasTotal ? 'YES' : 'NO'}`);

    const isActive = !posPageInfo.hasComingSoon &&
                    (posPageInfo.hasCart || posPageInfo.hasProducts || posPageInfo.hasPayment);

    console.log('\n' + '='.repeat(50));
    if (isActive) {
      console.log('✅ POS MODULE IS NOW ACTIVE!');
    } else {
      console.log('❌ POS MODULE ACTIVATION FAILED');
    }
    console.log('='.repeat(50));

    console.log('\nPress Ctrl+C to close the browser...');
    await new Promise(() => {});

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    if (browser) await browser.close();
    process.exit(1);
  }
}

testPOSActive();
