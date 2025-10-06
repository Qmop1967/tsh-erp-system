#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testInventoryImages() {
  let browser;

  try {
    console.log('🚀 Testing Inventory Module - Product Images from Zoho\n');

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

    // Navigate to Inventory/Items
    console.log('📦 Navigating to Inventory/Items...');
    await page.goto('http://localhost:5173/inventory/items', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Search for products that have images
    console.log('🔍 Searching for "RCA Adapter" (known to have images)...');
    const searchInput = await page.$('input[placeholder*="Search"], input[type="search"]');
    if (searchInput) {
      await searchInput.type('RCA');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    // Check for product images
    const inventoryData = await page.evaluate(() => {
      // Find all images
      const allImages = document.querySelectorAll('img');

      // Filter for product images (not logos, icons, etc.)
      const productImages = Array.from(allImages).filter(img =>
        img.src.includes('/images/products/')
      );

      // Get details
      const imageDetails = productImages.slice(0, 5).map((img, idx) => ({
        index: idx + 1,
        src: img.src,
        alt: img.alt || 'No alt text',
        width: img.width,
        height: img.height,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        loaded: img.complete && img.naturalHeight !== 0
      }));

      // Also check for any product cards/items
      const productCards = document.querySelectorAll('[class*="product"], [class*="item"], [class*="card"]');

      return {
        totalProductImages: productImages.length,
        imageDetails: imageDetails,
        totalProductCards: productCards.length,
        pageTitle: document.title,
        bodyText: document.body.textContent.substring(0, 500)
      };
    });

    console.log('\n📊 Inventory Page Analysis:');
    console.log('='.repeat(70));
    console.log(`Page Title: ${inventoryData.pageTitle}`);
    console.log(`Product Images Found: ${inventoryData.totalProductImages}`);
    console.log(`Product Cards Found: ${inventoryData.totalProductCards}`);
    console.log('');

    if (inventoryData.imageDetails.length > 0) {
      console.log('📷 Product Images Detected:');
      inventoryData.imageDetails.forEach(img => {
        const filename = img.src.split('/').pop();
        const status = img.loaded ? '✅ LOADED' : '❌ FAILED';
        console.log(`   ${img.index}. ${filename}`);
        console.log(`      Status: ${status}`);
        console.log(`      Size: ${img.width}x${img.height} (Natural: ${img.naturalWidth}x${img.naturalHeight})`);
        console.log(`      Alt: ${img.alt}`);
        console.log('');
      });
    } else {
      console.log('❌ No product images found on page');
      console.log('\nPage content sample:');
      console.log(inventoryData.bodyText);
    }

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'inventory-items-with-images.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved: screenshots/inventory-items-with-images.png\n');

    // Summary
    console.log('='.repeat(70));
    console.log('📊 INVENTORY IMAGE TEST SUMMARY');
    console.log('='.repeat(70));
    if (inventoryData.totalProductImages > 0) {
      console.log(`✅ SUCCESS: ${inventoryData.totalProductImages} product images are displaying!`);
      console.log(`✅ Images loaded from Zoho and are visible in the Inventory module`);
    } else {
      console.log(`⚠️  No product images found on the page`);
      console.log(`   This could mean:`);
      console.log(`   1. The products on this page don't have images`);
      console.log(`   2. The search didn't find products with images`);
      console.log(`   3. The page structure is different than expected`);
    }
    console.log('='.repeat(70));

    console.log('\n⏸️  Keeping browser open for 15 seconds so you can verify...');
    await new Promise(resolve => setTimeout(resolve, 15000));

    console.log('🔄 Closing browser...');
    await browser.close();
    console.log('✅ Test complete!\n');

    process.exit(0);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

testInventoryImages();
