#!/usr/bin/env node

const puppeteer = require('puppeteer-core');

async function checkImages() {
  let browser;

  try {
    console.log('🔍 Checking Image Display in POS\n');

    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });

    const page = await browser.newPage();

    // Listen to console logs from the page
    page.on('console', msg => {
      if (msg.text().includes('PRODUCT_DATA:')) {
        console.log(msg.text());
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

    // Navigate to POS
    console.log('🛒 Navigating to POS...');
    await page.goto('http://localhost:5173/pos', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Check what products are loaded
    const productData = await page.evaluate(() => {
      // Log first 3 products to console
      const products = document.querySelectorAll('[class*="grid"] > div');
      const productInfo = [];

      products.forEach((product, idx) => {
        if (idx < 5) {
          const img = product.querySelector('img');
          const text = product.textContent;
          const info = {
            index: idx,
            hasImg: !!img,
            imgSrc: img ? img.src : null,
            productText: text.substring(0, 50)
          };
          productInfo.push(info);
          console.log('PRODUCT_DATA:', JSON.stringify(info));
        }
      });

      return productInfo;
    });

    console.log('\n📊 Product Data from Browser:');
    console.log('='.repeat(60));
    productData.forEach(p => {
      console.log(`Product ${p.index + 1}:`);
      console.log(`  Has Image Tag: ${p.hasImg ? '✅ Yes' : '❌ No'}`);
      console.log(`  Image Src: ${p.imgSrc || 'NONE'}`);
      console.log(`  Text: ${p.productText}...`);
      console.log('');
    });
    console.log('='.repeat(60));

    console.log('\n⏸️  Keeping browser open for 15 seconds...');
    await new Promise(resolve => setTimeout(resolve, 15000));

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

checkImages();
