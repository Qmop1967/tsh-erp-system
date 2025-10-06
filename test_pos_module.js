#!/usr/bin/env node

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testPOSModule() {
  let browser;

  try {
    console.log('🚀 Testing POS (Point of Sale) Module...\n');

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

    // Check if POS exists in sidebar
    console.log('🔍 Checking POS in sidebar...');
    const posInSidebar = await page.evaluate(() => {
      const allLinks = Array.from(document.querySelectorAll('a, button, div'));
      const posLinks = allLinks.filter(el => {
        const text = el.textContent.trim().toLowerCase();
        return text === 'pos' || text === 'point of sale' || text.includes('point of sale');
      });

      return {
        found: posLinks.length > 0,
        count: posLinks.length,
        texts: posLinks.map(el => el.textContent.trim()).slice(0, 5)
      };
    });

    console.log('POS in Sidebar:', JSON.stringify(posInSidebar, null, 2));
    console.log('');

    // Try to navigate to /pos
    console.log('🔍 Navigating to /pos...');
    await page.goto('http://localhost:5173/pos', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check page content
    const posPageInfo = await page.evaluate(() => {
      const heading = document.querySelector('h1, h2, h3');
      const bodyText = document.body.textContent;

      return {
        heading: heading?.textContent.trim() || 'No heading',
        hasPOS: bodyText.toLowerCase().includes('point of sale') || bodyText.toLowerCase().includes('pos'),
        hasComingSoon: bodyText.includes('Coming Soon') || bodyText.includes('coming soon'),
        hasProducts: bodyText.toLowerCase().includes('product'),
        hasCart: bodyText.toLowerCase().includes('cart'),
        hasCheckout: bodyText.toLowerCase().includes('checkout'),
        currentUrl: window.location.href,
        bodyTextSample: bodyText.substring(0, 400)
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
      path: path.join(screenshotDir, 'pos-module-test.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved: pos-module-test.png\n');

    // Try alternative routes
    const alternativeRoutes = ['/point-of-sale', '/sales', '/pos/new'];

    for (const route of alternativeRoutes) {
      console.log(`🔍 Trying route: ${route}`);
      await page.goto(`http://localhost:5173${route}`, { waitUntil: 'networkidle2' });
      await new Promise(resolve => setTimeout(resolve, 1000));

      const routeInfo = await page.evaluate(() => {
        return {
          url: window.location.href,
          heading: document.querySelector('h1, h2, h3')?.textContent.trim() || 'No heading'
        };
      });

      console.log(`  URL: ${routeInfo.url}`);
      console.log(`  Heading: ${routeInfo.heading}`);
      console.log('');
    }

    // Summary
    console.log('📊 POS MODULE TEST SUMMARY');
    console.log('==========================');
    console.log(`✅ POS found in sidebar: ${posInSidebar.found ? 'YES' : 'NO'}`);
    console.log(`✅ Main route (/pos) heading: ${posPageInfo.heading}`);
    console.log(`✅ Has "Coming Soon": ${posPageInfo.hasComingSoon ? 'YES' : 'NO'}`);
    console.log(`✅ Has POS content: ${posPageInfo.hasPOS ? 'YES' : 'NO'}`);
    console.log(`✅ Has Products: ${posPageInfo.hasProducts ? 'YES' : 'NO'}`);
    console.log(`✅ Has Cart: ${posPageInfo.hasCart ? 'YES' : 'NO'}`);
    console.log(`✅ Has Checkout: ${posPageInfo.hasCheckout ? 'YES' : 'NO'}`);

    const isActive = posInSidebar.found &&
                    !posPageInfo.hasComingSoon &&
                    (posPageInfo.hasPOS || posPageInfo.hasProducts);

    console.log('\n' + '='.repeat(50));
    if (isActive) {
      console.log('✅ POS MODULE IS ACTIVE');
    } else if (posPageInfo.hasComingSoon) {
      console.log('❌ POS MODULE SHOWS "COMING SOON"');
    } else if (!posInSidebar.found) {
      console.log('❌ POS MODULE NOT FOUND IN SIDEBAR');
    } else {
      console.log('❌ POS MODULE IS NOT ACTIVE');
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

testPOSModule();
