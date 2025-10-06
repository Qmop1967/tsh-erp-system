#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testInventoryImages() {
  let browser;

  try {
    console.log('🚀 Testing Inventory Module - Product Images\n');

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

    // Navigate to Inventory
    console.log('📦 Navigating to Inventory...');
    await page.goto('http://localhost:5173/inventory', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Check for items with images
    const inventoryData = await page.evaluate(() => {
      const bodyText = document.body.textContent;

      // Look for product cards or table
      const productElements = document.querySelectorAll('[class*="product"], [class*="item"], img[src*="products"]');

      // Get first image src
      const firstImage = document.querySelector('img[src*="products"]');

      return {
        hasInventory: bodyText.includes('Inventory') || bodyText.includes('Product'),
        productElementsCount: productElements.length,
        hasImages: !!firstImage,
        firstImageSrc: firstImage ? firstImage.src : null,
        bodyTextSample: bodyText.substring(0, 500)
      };
    });

    console.log('📊 Inventory Status:');
    console.log(JSON.stringify(inventoryData, null, 2));
    console.log('');

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'inventory-with-images.png'),
      fullPage: true
    });
    console.log('📸 Screenshot: screenshots/inventory-with-images.png\n');

    // Summary
    console.log('============================================================');
    console.log('📊 INVENTORY IMAGE TEST SUMMARY');
    console.log('============================================================');
    console.log(`✅ Inventory Module: ${inventoryData.hasInventory ? '✅ Active' : '❌ Not Found'}`);
    console.log(`✅ Product Elements: ${inventoryData.productElementsCount}`);
    console.log(`✅ Product Images: ${inventoryData.hasImages ? '✅ Displayed' : '❌ Not Found'}`);
    if (inventoryData.firstImageSrc) {
      console.log(`✅ First Image URL: ${inventoryData.firstImageSrc}`);
    }
    console.log('============================================================');

    console.log('\n🔄 Closing browser...');
    await browser.close();
    console.log('✅ Test complete!\n');

    process.exit(0);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

testInventoryImages();
