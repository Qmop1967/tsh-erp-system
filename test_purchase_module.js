#!/usr/bin/env node

/**
 * TSH ERP System - Purchase Module Test
 * Tests if the Purchase module is active and functional
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPurchaseModule() {
  let browser;

  try {
    console.log('🚀 Testing Purchase Module...\n');

    // Find Chrome executable
    const possiblePaths = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ];

    let chromePath;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        chromePath = p;
        break;
      }
    }

    if (!chromePath) {
      throw new Error('Chrome not found');
    }

    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox'],
      defaultViewport: { width: 1280, height: 800 }
    });

    const page = await browser.newPage();

    // Capture console logs
    const consoleLogs = [];
    page.on('console', msg => {
      consoleLogs.push({ type: msg.type(), text: msg.text() });
    });

    // Track API requests
    const apiRequests = [];
    page.on('request', request => {
      if (request.url().includes('/api/') || request.url().includes(':8000')) {
        apiRequests.push({
          url: request.url(),
          method: request.method()
        });
      }
    });

    // Login first
    console.log('🔐 Logging in...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });

    await page.waitForSelector('input[type="email"]');
    await page.type('input[type="email"]', 'admin@tsh.com');
    await page.type('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('✅ Logged in successfully\n');

    // Screenshot the dashboard
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Check if Purchase module exists in sidebar
    console.log('🔍 Checking Purchase module in sidebar...');
    const purchaseModuleCheck = await page.evaluate(() => {
      // Look for Purchase module link/button
      const purchaseLinks = Array.from(document.querySelectorAll('a, button, div'))
        .filter(el => el.textContent.trim().toLowerCase().includes('purchase'));

      return {
        found: purchaseLinks.length > 0,
        count: purchaseLinks.length,
        texts: purchaseLinks.map(el => el.textContent.trim()),
        hrefs: purchaseLinks.map(el => el.getAttribute('href') || 'no-href')
      };
    });

    console.log('Purchase Module Links:', JSON.stringify(purchaseModuleCheck, null, 2));
    console.log('');

    if (!purchaseModuleCheck.found) {
      console.log('❌ Purchase module not found in sidebar');
      await page.screenshot({ path: path.join(screenshotDir, 'purchase-not-found.png'), fullPage: true });

      // List all available menu items
      const allMenuItems = await page.evaluate(() => {
        const menuItems = Array.from(document.querySelectorAll('nav a, nav button, aside a, aside button, [class*="sidebar" i] a, [class*="sidebar" i] button'))
          .map(el => el.textContent.trim())
          .filter(text => text.length > 0);
        return [...new Set(menuItems)];
      });

      console.log('📋 Available Menu Items:');
      allMenuItems.forEach(item => console.log(`  - ${item}`));

      console.log('\n⚠️  Purchase module is NOT active');
      await browser.close();
      return;
    }

    // Click on Purchase module
    console.log('🖱️  Clicking on Purchase module...');
    await page.evaluate(() => {
      const purchaseLink = Array.from(document.querySelectorAll('a, button, div'))
        .find(el => el.textContent.trim().toLowerCase().includes('purchase'));
      if (purchaseLink) purchaseLink.click();
    });

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check current URL
    const currentUrl = page.url();
    console.log(`📍 Current URL: ${currentUrl}\n`);

    // Take screenshot of Purchase page
    await page.screenshot({
      path: path.join(screenshotDir, 'purchase-module.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved: purchase-module.png\n');

    // Check Purchase page content
    console.log('🔍 Analyzing Purchase page...');
    const purchasePageInfo = await page.evaluate(() => {
      const heading = document.querySelector('h1, h2, h3');
      const buttons = Array.from(document.querySelectorAll('button'))
        .map(btn => btn.textContent.trim())
        .filter(text => text.length > 0);

      const tables = document.querySelectorAll('table');
      const forms = document.querySelectorAll('form');
      const inputs = document.querySelectorAll('input');

      // Look for purchase-related elements
      const purchaseOrders = Array.from(document.querySelectorAll('[class*="purchase" i], [id*="purchase" i]'))
        .map(el => el.className || el.id);

      return {
        pageHeading: heading?.textContent.trim() || 'No heading',
        hasContent: document.body.textContent.trim().length > 100,
        buttonCount: buttons.length,
        buttons: buttons.slice(0, 10),
        tableCount: tables.length,
        formCount: forms.length,
        inputCount: inputs.length,
        purchaseElements: purchaseOrders.slice(0, 5),
        currentPath: window.location.pathname
      };
    });

    console.log('Purchase Page Info:', JSON.stringify(purchasePageInfo, null, 2));
    console.log('');

    // Check for API calls to purchase endpoints
    const purchaseAPIs = apiRequests.filter(req =>
      req.url.toLowerCase().includes('purchase') ||
      req.url.toLowerCase().includes('po') ||
      req.url.toLowerCase().includes('vendor')
    );

    console.log('🌐 Purchase-related API Calls:');
    if (purchaseAPIs.length > 0) {
      purchaseAPIs.forEach(api => {
        console.log(`  ${api.method} ${api.url}`);
      });
    } else {
      console.log('  No purchase-related API calls detected');
    }
    console.log('');

    // Check for Purchase Orders, Vendors, etc.
    console.log('🔍 Looking for Purchase features...');
    const purchaseFeatures = await page.evaluate(() => {
      const bodyText = document.body.textContent.toLowerCase();

      return {
        hasPurchaseOrders: bodyText.includes('purchase order') || bodyText.includes('po'),
        hasVendors: bodyText.includes('vendor') || bodyText.includes('supplier'),
        hasItems: bodyText.includes('item') || bodyText.includes('product'),
        hasCreate: bodyText.includes('create') || bodyText.includes('add') || bodyText.includes('new'),
        hasTable: !!document.querySelector('table'),
        bodyTextSample: document.body.textContent.trim().substring(0, 500)
      };
    });

    console.log('Purchase Features:', JSON.stringify(purchaseFeatures, null, 2));
    console.log('');

    // Summary
    console.log('📊 PURCHASE MODULE TEST SUMMARY');
    console.log('================================');
    console.log(`✅ Purchase module found in menu: ${purchaseModuleCheck.found ? 'YES' : 'NO'}`);
    console.log(`✅ Purchase page URL: ${currentUrl}`);
    console.log(`✅ Page heading: ${purchasePageInfo.pageHeading}`);
    console.log(`✅ Has content: ${purchasePageInfo.hasContent ? 'YES' : 'NO'}`);
    console.log(`✅ Number of buttons: ${purchasePageInfo.buttonCount}`);
    console.log(`✅ Number of tables: ${purchasePageInfo.tableCount}`);
    console.log(`✅ Number of forms: ${purchasePageInfo.formCount}`);
    console.log(`✅ Number of inputs: ${purchasePageInfo.inputCount}`);
    console.log(`✅ Purchase-related API calls: ${purchaseAPIs.length}`);
    console.log(`✅ Has Purchase Orders: ${purchaseFeatures.hasPurchaseOrders ? 'YES' : 'NO'}`);
    console.log(`✅ Has Vendors: ${purchaseFeatures.hasVendors ? 'YES' : 'NO'}`);

    // Final verdict
    const isActive = purchaseModuleCheck.found &&
                     purchasePageInfo.hasContent &&
                     (purchasePageInfo.buttonCount > 0 || purchasePageInfo.tableCount > 0);

    console.log('\n' + '='.repeat(50));
    if (isActive) {
      console.log('✅ PURCHASE MODULE IS ACTIVE AND FUNCTIONAL');
    } else {
      console.log('❌ PURCHASE MODULE IS NOT FULLY ACTIVE');
    }
    console.log('='.repeat(50));

    console.log('\n📸 Screenshots saved in ./screenshots/');
    console.log('\nPress Ctrl+C to close the browser...');

    await new Promise(() => {});

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    if (browser) await browser.close();
    process.exit(1);
  }
}

testPurchaseModule();
