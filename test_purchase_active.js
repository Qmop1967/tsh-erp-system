#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPurchaseActive() {
  let browser;

  try {
    console.log('🚀 Testing Activated Purchase Module...\n');

    const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1280, height: 800 }
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

    // Navigate directly to /purchase
    console.log('🔍 Navigating to /purchase...');
    await page.goto('http://localhost:5173/purchase', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check page content
    const pageInfo = await page.evaluate(() => {
      const heading = document.querySelector('h1');
      const hasPurchaseOrders = document.body.textContent.includes('Purchase Orders');
      const hasCreateButton = document.body.textContent.includes('Create Purchase Order');
      const hasTable = !!document.querySelector('table');
      const purchaseOrderCount = document.querySelectorAll('tr').length - 1; // Minus header

      return {
        heading: heading?.textContent.trim() || 'No heading',
        hasPurchaseOrders,
        hasCreateButton,
        hasTable,
        purchaseOrderCount,
        currentUrl: window.location.href,
        bodyText: document.body.textContent.substring(0, 300)
      };
    });

    console.log('📊 Purchase Page Info:');
    console.log(JSON.stringify(pageInfo, null, 2));
    console.log('');

    // Take screenshot
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'purchase-page-active.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved: purchase-page-active.png\n');

    // Test navigation via sidebar
    console.log('🖱️  Testing sidebar navigation...');
    await page.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Try to click Purchase in sidebar
    await page.evaluate(() => {
      const purchaseLink = Array.from(document.querySelectorAll('a, button, div'))
        .find(el => {
          const text = el.textContent.trim();
          return text === 'Purchase' || text.toLowerCase() === 'purchase';
        });
      if (purchaseLink) {
        console.log('Found purchase link:', purchaseLink.textContent);
        purchaseLink.click();
      }
    });

    await new Promise(resolve => setTimeout(resolve, 2000));

    const afterClickUrl = page.url();
    console.log(`📍 URL after clicking sidebar: ${afterClickUrl}\n`);

    // Summary
    console.log('📊 TEST SUMMARY');
    console.log('===============');
    console.log(`✅ Purchase page heading: ${pageInfo.heading}`);
    console.log(`✅ Has "Purchase Orders" text: ${pageInfo.hasPurchaseOrders}`);
    console.log(`✅ Has "Create Purchase Order" button: ${pageInfo.hasCreateButton}`);
    console.log(`✅ Has table: ${pageInfo.hasTable}`);
    console.log(`✅ Purchase order rows: ${pageInfo.purchaseOrderCount}`);
    console.log(`✅ Direct navigation URL: ${pageInfo.currentUrl}`);
    console.log(`✅ Sidebar navigation URL: ${afterClickUrl}`);

    const isActive = pageInfo.hasPurchaseOrders &&
                    pageInfo.heading.includes('Purchase') &&
                    !pageInfo.heading.includes('Coming Soon');

    console.log('\n' + '='.repeat(50));
    if (isActive) {
      console.log('✅ PURCHASE MODULE IS NOW ACTIVE!');
    } else {
      console.log('❌ PURCHASE MODULE STILL NOT ACTIVE');
    }
    console.log('='.repeat(50));

    console.log('\nPress Ctrl+C to close the browser...');
    await new Promise(() => {});

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (browser) await browser.close();
    process.exit(1);
  }
}

testPurchaseActive();
