#!/usr/bin/env node

/**
 * TSH ERP System Login Test using Chrome DevTools MCP
 * This script tests the login functionality using Chrome DevTools Protocol
 */

const { ChromeDevToolsMCP } = require('chrome-devtools-mcp');

async function testLogin() {
  const mcp = new ChromeDevToolsMCP();

  try {
    console.log('🚀 Starting Chrome DevTools MCP Login Test...\n');

    // Connect to Chrome
    console.log('📡 Connecting to Chrome...');
    await mcp.connect();
    console.log('✅ Connected to Chrome\n');

    // Navigate to login page
    const loginUrl = 'http://localhost:5173/';
    console.log(`🌐 Navigating to: ${loginUrl}`);
    await mcp.navigate(loginUrl);
    await mcp.wait(2000); // Wait for page load
    console.log('✅ Page loaded\n');

    // Take screenshot of login page
    console.log('📸 Taking screenshot of login page...');
    const loginScreenshot = await mcp.screenshot();
    console.log('✅ Screenshot captured\n');

    // Get page title
    console.log('📄 Getting page title...');
    const title = await mcp.evaluate('document.title');
    console.log(`✅ Page Title: ${title}\n`);

    // Check for login form elements
    console.log('🔍 Checking for login form elements...');
    const hasLoginForm = await mcp.evaluate(`
      const emailInput = document.querySelector('input[type="email"], input[name="email"], input[placeholder*="email" i]');
      const passwordInput = document.querySelector('input[type="password"]');
      const loginButton = document.querySelector('button[type="submit"], button:has-text("login" i), button:has-text("sign in" i)');

      return {
        hasEmail: !!emailInput,
        hasPassword: !!passwordInput,
        hasButton: !!loginButton,
        emailPlaceholder: emailInput?.placeholder || 'Not found',
        passwordPlaceholder: passwordInput?.placeholder || 'Not found'
      };
    `);
    console.log('Login Form Elements:', hasLoginForm);
    console.log('');

    // Try to find and fill login credentials
    console.log('🔐 Attempting to fill login credentials...');
    const fillResult = await mcp.evaluate(`
      const emailInput = document.querySelector('input[type="email"], input[name="email"], input[placeholder*="email" i]');
      const passwordInput = document.querySelector('input[type="password"]');

      if (emailInput && passwordInput) {
        emailInput.value = 'admin@tsh.com';
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        emailInput.dispatchEvent(new Event('change', { bubbles: true }));

        passwordInput.value = 'admin123';
        passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
        passwordInput.dispatchEvent(new Event('change', { bubbles: true }));

        return { success: true, message: 'Credentials filled successfully' };
      }
      return { success: false, message: 'Login form not found' };
    `);
    console.log('Fill Result:', fillResult);
    console.log('');

    // Take screenshot after filling
    console.log('📸 Taking screenshot after filling credentials...');
    await mcp.wait(500);
    const filledScreenshot = await mcp.screenshot();
    console.log('✅ Screenshot captured\n');

    // Try to click login button
    console.log('🖱️  Attempting to click login button...');
    const clickResult = await mcp.evaluate(`
      const loginButton = document.querySelector('button[type="submit"]');
      if (loginButton) {
        loginButton.click();
        return { success: true, message: 'Login button clicked' };
      }
      return { success: false, message: 'Login button not found' };
    `);
    console.log('Click Result:', clickResult);
    console.log('');

    // Wait for navigation or response
    console.log('⏳ Waiting for login response...');
    await mcp.wait(3000);

    // Check current URL
    const currentUrl = await mcp.evaluate('window.location.href');
    console.log(`📍 Current URL: ${currentUrl}\n`);

    // Check for error messages or success
    console.log('🔍 Checking for login result...');
    const loginResult = await mcp.evaluate(`
      const errorMsg = document.querySelector('.error, [class*="error" i], [role="alert"]');
      const dashboardIndicator = document.querySelector('[class*="dashboard" i], [class*="home" i]');

      return {
        hasError: !!errorMsg,
        errorMessage: errorMsg?.textContent || 'No error message',
        hasDashboard: !!dashboardIndicator,
        currentPath: window.location.pathname
      };
    `);
    console.log('Login Result:', loginResult);
    console.log('');

    // Take final screenshot
    console.log('📸 Taking final screenshot...');
    const finalScreenshot = await mcp.screenshot();
    console.log('✅ Final screenshot captured\n');

    // Get console logs
    console.log('📋 Getting browser console logs...');
    const consoleLogs = await mcp.evaluate(`
      const logs = window.__consoleLogs || [];
      return logs.length > 0 ? logs : ['No console logs captured'];
    `);
    console.log('Console Logs:', consoleLogs);
    console.log('');

    // Check network requests
    console.log('🌐 Checking network activity...');
    const networkInfo = await mcp.evaluate(`
      const perfEntries = performance.getEntriesByType('resource');
      const apiCalls = perfEntries.filter(e => e.name.includes('/api/') || e.name.includes(':8000'));
      return {
        totalRequests: perfEntries.length,
        apiCalls: apiCalls.length,
        recentAPIs: apiCalls.slice(-5).map(e => ({ url: e.name, duration: e.duration }))
      };
    `);
    console.log('Network Info:', networkInfo);
    console.log('');

    // Summary
    console.log('📊 TEST SUMMARY');
    console.log('================');
    console.log(`✅ Login page loaded: ${title}`);
    console.log(`✅ Form elements found: Email=${hasLoginForm.hasEmail}, Password=${hasLoginForm.hasPassword}, Button=${hasLoginForm.hasButton}`);
    console.log(`✅ Credentials filled: ${fillResult.success}`);
    console.log(`✅ Login attempted: ${clickResult.success}`);
    console.log(`✅ Final URL: ${currentUrl}`);
    console.log(`✅ Login successful: ${loginResult.hasDashboard || currentUrl.includes('dashboard')}`);

    await mcp.disconnect();
    console.log('\n✅ Test completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the test
testLogin();
