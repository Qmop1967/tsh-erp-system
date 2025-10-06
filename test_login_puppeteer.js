#!/usr/bin/env node

/**
 * TSH ERP System Login Test using Puppeteer
 * This script tests the login functionality using Chrome DevTools Protocol via Puppeteer
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function testLogin() {
  let browser;

  try {
    console.log('🚀 Starting Chrome DevTools Login Test...\n');

    // Find Chrome executable
    const possiblePaths = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta',
    ];

    let chromePath;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        chromePath = p;
        break;
      }
    }

    if (!chromePath) {
      throw new Error('Chrome not found. Please install Google Chrome.');
    }

    console.log(`📡 Launching Chrome from: ${chromePath}`);
    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1280, height: 800 }
    });

    const page = await browser.newPage();
    console.log('✅ Chrome launched\n');

    // Enable console message capture
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // Enable request/response monitoring
    const apiRequests = [];
    page.on('request', request => {
      if (request.url().includes('/api/') || request.url().includes(':8000')) {
        apiRequests.push({
          url: request.url(),
          method: request.method()
        });
      }
    });

    // Navigate to login page
    const loginUrl = 'http://localhost:5173/';
    console.log(`🌐 Navigating to: ${loginUrl}`);
    await page.goto(loginUrl, { waitUntil: 'networkidle2' });
    console.log('✅ Page loaded\n');

    // Take screenshot of login page
    console.log('📸 Taking screenshot of login page...');
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    await page.screenshot({
      path: path.join(screenshotDir, 'login-page.png'),
      fullPage: true
    });
    console.log('✅ Screenshot saved to screenshots/login-page.png\n');

    // Get page title
    const title = await page.title();
    console.log(`📄 Page Title: ${title}\n`);

    // Check for login form elements
    console.log('🔍 Checking for login form elements...');
    const loginFormCheck = await page.evaluate(() => {
      const emailInput = document.querySelector('input[type="email"]') ||
                        document.querySelector('input[name="email"]');
      const passwordInput = document.querySelector('input[type="password"]');
      const loginButton = document.querySelector('button[type="submit"]');

      return {
        hasEmail: !!emailInput,
        hasPassword: !!passwordInput,
        hasButton: !!loginButton,
        emailPlaceholder: emailInput?.placeholder || 'Not found',
        passwordPlaceholder: passwordInput?.placeholder || 'Not found',
        buttonText: loginButton?.textContent.trim() || 'Not found'
      };
    });
    console.log('Login Form Elements:', JSON.stringify(loginFormCheck, null, 2));
    console.log('');

    // Fill login credentials
    console.log('🔐 Filling login credentials...');
    const emailSelector = 'input[type="email"]';
    const passwordSelector = 'input[type="password"]';

    await page.waitForSelector(emailSelector, { timeout: 5000 });
    await page.type(emailSelector, 'admin@tsh.com');
    console.log('✅ Email filled: admin@tsh.com');

    await page.type(passwordSelector, 'admin123');
    console.log('✅ Password filled\n');

    // Take screenshot after filling
    await page.screenshot({
      path: path.join(screenshotDir, 'login-filled.png'),
      fullPage: true
    });
    console.log('📸 Screenshot saved to screenshots/login-filled.png\n');

    // Click login button
    console.log('🖱️  Clicking login button...');
    const loginButtonSelector = 'button[type="submit"]';
    await page.click(loginButtonSelector);
    console.log('✅ Login button clicked\n');

    // Wait for navigation or response
    console.log('⏳ Waiting for login response...');
    try {
      await page.waitForNavigation({ timeout: 5000, waitUntil: 'networkidle2' });
    } catch (e) {
      console.log('⚠️  No navigation detected (might be SPA)');
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Check current URL
    const currentUrl = page.url();
    console.log(`📍 Current URL: ${currentUrl}\n`);

    // Check for error messages or success
    console.log('🔍 Checking for login result...');
    const loginResult = await page.evaluate(() => {
      const errorMsg = document.querySelector('.error, [class*="error" i], [role="alert"]');
      const dashboardIndicator = document.querySelector('[class*="dashboard" i], [class*="sidebar" i], nav');
      const pageHeading = document.querySelector('h1, h2');

      return {
        hasError: !!errorMsg,
        errorMessage: errorMsg?.textContent.trim() || 'No error message',
        hasDashboard: !!dashboardIndicator,
        pageHeading: pageHeading?.textContent.trim() || 'No heading found',
        currentPath: window.location.pathname,
        bodyClasses: document.body.className
      };
    });
    console.log('Login Result:', JSON.stringify(loginResult, null, 2));
    console.log('');

    // Take final screenshot
    await page.screenshot({
      path: path.join(screenshotDir, 'post-login.png'),
      fullPage: true
    });
    console.log('📸 Final screenshot saved to screenshots/post-login.png\n');

    // Display console logs
    console.log('📋 Browser Console Logs:');
    console.log('========================');
    consoleMessages.slice(0, 10).forEach(msg => {
      console.log(`[${msg.type.toUpperCase()}] ${msg.text}`);
    });
    if (consoleMessages.length > 10) {
      console.log(`... and ${consoleMessages.length - 10} more messages`);
    }
    console.log('');

    // Display API requests
    console.log('🌐 API Requests Made:');
    console.log('=====================');
    apiRequests.forEach(req => {
      console.log(`${req.method} ${req.url}`);
    });
    console.log('');

    // Summary
    console.log('📊 TEST SUMMARY');
    console.log('================');
    console.log(`✅ Login page loaded: ${title}`);
    console.log(`✅ Form elements found:`);
    console.log(`   - Email input: ${loginFormCheck.hasEmail}`);
    console.log(`   - Password input: ${loginFormCheck.hasPassword}`);
    console.log(`   - Submit button: ${loginFormCheck.hasButton}`);
    console.log(`✅ Credentials filled successfully`);
    console.log(`✅ Login button clicked`);
    console.log(`✅ Post-login URL: ${currentUrl}`);
    console.log(`✅ Dashboard/Nav found: ${loginResult.hasDashboard}`);
    console.log(`✅ Current page: ${loginResult.pageHeading}`);
    console.log(`✅ Login Status: ${loginResult.hasDashboard && !loginResult.hasError ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`✅ API calls made: ${apiRequests.length}`);
    console.log(`✅ Screenshots saved in ./screenshots/`);

    console.log('\n✅ Test completed successfully!');
    console.log('\nPress Ctrl+C to close the browser...');

    // Keep browser open for inspection
    await new Promise(() => {});

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

// Run the test
testLogin();
