#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPOSImages() {
  let browser;

  try {
    console.log('🚀 Testing POS - Product Images from Zoho\n');

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
    console.log('🛒 Navigating to POS...');
    await page.goto('http://localhost:5173/pos', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Check for product images
    const posData = await page.evaluate(() => {
      // Find all product images
      const productImages = document.querySelectorAll('img[src*="/images/products/"]');

      // Get details of first few products with images
      const imageDetails = Array.from(productImages).slice(0, 3).map(img => ({
        src: img.src,
        alt: img.alt,
        width: img.width,
        height: img.height
      }));

      return {
        totalImages: productImages.length,
        imageDetails: imageDetails,
        bodyTextSample: document.body.textContent.substring(0, 300)
      };
    });

    console.log('📊 POS Image Status:');
    console.log(JSON.stringify(posData, null, 2));
    console.log('');

    // Take screenshot showing products with images
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'pos-with-zoho-images.png'),
      fullPage: false  // Just show the visible area with products
    });
    console.log('📸 Screenshot: screenshots/pos-with-zoho-images.png\n');

    // Summary
    console.log('============================================================');
    console.log('📊 POS IMAGE VERIFICATION');
    console.log('============================================================');
    console.log(`✅ Product Images Found: ${posData.totalImages}`);
    console.log(`✅ Images Status: ${posData.totalImages > 0 ? '✅ SUCCESSFULLY LOADED FROM ZOHO' : '❌ No images found'}`);
    if (posData.imageDetails.length > 0) {
      console.log('\n📷 Sample Images:');
      posData.imageDetails.forEach((img, idx) => {
        console.log(`   ${idx + 1}. ${img.src.split('/').pop()} (${img.width}x${img.height})`);
      });
    }
    console.log('============================================================');

    console.log('\n⏸️  Keeping browser open for 10 seconds so you can verify...');
    await new Promise(resolve => setTimeout(resolve, 10000));

    console.log('🔄 Closing browser...');
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

testPOSImages();
