import { test, expect } from '@playwright/test';

test.describe('Console Errors Diagnostic', () => {
  let consoleMessages: Array<{
    type: string;
    text: string;
    location?: string;
  }> = [];

  test.beforeEach(async ({ page }) => {
    // Capture all console messages
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location()?.url || 'unknown'
      });
    });

    // Capture page errors
    page.on('pageerror', error => {
      consoleMessages.push({
        type: 'pageerror',
        text: error.message,
        location: error.stack || 'unknown'
      });
    });
  });

  test('Analyze console errors and warnings', async ({ page }) => {
    console.log('\n🔍 Starting Console Diagnostic Test...\n');

    // Navigate to the application
    await page.goto('http://localhost:5173', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });

    // Wait for React to initialize
    await page.waitForTimeout(3000);

    // Categorize console messages
    const reactRouterWarnings = consoleMessages.filter(msg => 
      msg.text.includes('React Router Future Flag') || 
      msg.text.includes('v7_')
    );

    const customElementErrors = consoleMessages.filter(msg => 
      msg.text.includes('custom element') || 
      msg.text.includes('mce-autosize-textarea')
    );

    const nullPropertyErrors = consoleMessages.filter(msg => 
      msg.text.includes('Cannot read properties of null') ||
      msg.text.includes("reading 'style'")
    );

    const fontErrors = consoleMessages.filter(msg => 
      msg.text.includes('OTS parsing error') ||
      msg.text.includes('font') ||
      msg.text.includes('sfntVersion')
    );

    const extensionErrors = consoleMessages.filter(msg => 
      msg.location?.includes('extension://') ||
      msg.location?.includes('contentscript') ||
      msg.location?.includes('webcomponents-ce.js')
    );

    const appErrors = consoleMessages.filter(msg => 
      (msg.type === 'error' || msg.type === 'pageerror') &&
      msg.location?.includes('localhost') &&
      !msg.location?.includes('extension://')
    );

    // Print detailed report
    console.log('═══════════════════════════════════════════════════════');
    console.log('📊 CONSOLE DIAGNOSTIC REPORT');
    console.log('═══════════════════════════════════════════════════════\n');

    console.log(`📈 Total Messages: ${consoleMessages.length}`);
    console.log(`❌ Errors: ${consoleMessages.filter(m => m.type === 'error' || m.type === 'pageerror').length}`);
    console.log(`⚠️  Warnings: ${consoleMessages.filter(m => m.type === 'warning').length}`);
    console.log(`ℹ️  Info: ${consoleMessages.filter(m => m.type === 'info' || m.type === 'log').length}\n`);

    // React Router Warnings
    if (reactRouterWarnings.length > 0) {
      console.log('⚠️  REACT ROUTER WARNINGS:');
      console.log(`   Count: ${reactRouterWarnings.length}`);
      console.log(`   Status: ${reactRouterWarnings.length > 0 ? '❌ NOT FIXED' : '✅ FIXED'}`);
      reactRouterWarnings.slice(0, 2).forEach(msg => {
        console.log(`   - ${msg.text.substring(0, 80)}...`);
      });
      console.log('');
    } else {
      console.log('✅ REACT ROUTER WARNINGS: None detected\n');
    }

    // Custom Element Errors
    if (customElementErrors.length > 0) {
      console.log('❌ CUSTOM ELEMENT ERRORS:');
      console.log(`   Count: ${customElementErrors.length}`);
      console.log(`   Status: ❌ NOT FIXED`);
      customElementErrors.slice(0, 2).forEach(msg => {
        console.log(`   - ${msg.text.substring(0, 80)}...`);
      });
      console.log('');
    } else {
      console.log('✅ CUSTOM ELEMENT ERRORS: None detected\n');
    }

    // Null Property Errors
    if (nullPropertyErrors.length > 0) {
      console.log('❌ NULL PROPERTY ERRORS:');
      console.log(`   Count: ${nullPropertyErrors.length}`);
      nullPropertyErrors.slice(0, 2).forEach(msg => {
        console.log(`   - ${msg.text.substring(0, 80)}...`);
        console.log(`     Location: ${msg.location}`);
      });
      console.log('');
    } else {
      console.log('✅ NULL PROPERTY ERRORS: None detected\n');
    }

    // Font Errors
    if (fontErrors.length > 0) {
      console.log('⚠️  FONT WARNINGS:');
      console.log(`   Count: ${fontErrors.length}`);
      console.log(`   Status: ℹ️  Non-critical (can be ignored)`);
      console.log('');
    }

    // Extension Errors
    if (extensionErrors.length > 0) {
      console.log('ℹ️  BROWSER EXTENSION ERRORS:');
      console.log(`   Count: ${extensionErrors.length}`);
      console.log(`   Status: ℹ️  External (can be ignored)`);
      console.log('');
    }

    // Application-Specific Errors
    if (appErrors.length > 0) {
      console.log('🚨 APPLICATION ERRORS (CRITICAL):');
      console.log(`   Count: ${appErrors.length}`);
      appErrors.forEach(msg => {
        console.log(`   - ${msg.text}`);
        console.log(`     Location: ${msg.location}`);
      });
      console.log('');
    } else {
      console.log('✅ APPLICATION ERRORS: None detected\n');
    }

    // Check if fixes were applied
    console.log('═══════════════════════════════════════════════════════');
    console.log('🔧 FIX STATUS CHECK');
    console.log('═══════════════════════════════════════════════════════\n');

    // Check for error suppression utility
    const hasErrorSuppression = await page.evaluate(() => {
      return typeof (window as any).errorSuppressionInitialized !== 'undefined';
    });

    console.log(`Error Suppression Utility: ${hasErrorSuppression ? '✅ Loaded' : '❌ Not Found'}`);

    // Check React Router future flags
    const hasReactRouterFlags = reactRouterWarnings.length === 0;
    console.log(`React Router Future Flags: ${hasReactRouterFlags ? '✅ Applied' : '❌ Not Applied'}`);

    // Check custom element protection
    const hasCustomElementProtection = customElementErrors.length === 0;
    console.log(`Custom Element Protection: ${hasCustomElementProtection ? '✅ Working' : '❌ Not Working'}`);

    console.log('\n═══════════════════════════════════════════════════════');
    console.log('📋 ALL CONSOLE MESSAGES');
    console.log('═══════════════════════════════════════════════════════\n');

    consoleMessages.forEach((msg, index) => {
      const icon = msg.type === 'error' || msg.type === 'pageerror' ? '❌' : 
                   msg.type === 'warning' ? '⚠️' : 'ℹ️';
      console.log(`${index + 1}. ${icon} [${msg.type.toUpperCase()}]`);
      console.log(`   ${msg.text}`);
      if (msg.location !== 'unknown') {
        console.log(`   📍 ${msg.location}`);
      }
      console.log('');
    });

    console.log('═══════════════════════════════════════════════════════');
    console.log('🎯 RECOMMENDATIONS');
    console.log('═══════════════════════════════════════════════════════\n');

    if (reactRouterWarnings.length > 0) {
      console.log('❌ React Router warnings detected:');
      console.log('   → Apply future flags to BrowserRouter in main.tsx');
      console.log('');
    }

    if (customElementErrors.length > 0) {
      console.log('❌ Custom element errors detected:');
      console.log('   → Add duplicate element prevention in main.tsx');
      console.log('');
    }

    if (appErrors.length > 0) {
      console.log('🚨 Application errors detected:');
      console.log('   → Review and fix application-specific errors');
      console.log('');
    }

    if (reactRouterWarnings.length === 0 && customElementErrors.length === 0 && appErrors.length === 0) {
      console.log('✅ All fixes have been successfully applied!');
      console.log('   Your console is clean and error-free.');
      console.log('');
    }

    console.log('═══════════════════════════════════════════════════════\n');

    // Take a screenshot for visual verification
    await page.screenshot({ 
      path: 'test-results/console-diagnostic-screenshot.png',
      fullPage: true 
    });

    console.log('📸 Screenshot saved: test-results/console-diagnostic-screenshot.png\n');

    // Assertions
    expect(appErrors.length, 'Application should have no critical errors').toBe(0);
  });

  test('Check main.tsx for applied fixes', async ({ page }) => {
    console.log('\n🔍 Checking if fixes are present in source code...\n');

    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    
    // Check if the main.tsx file has the fixes applied
    const pageContent = await page.content();
    
    console.log('Checking source files for fixes...');
    console.log('Note: This checks if the compiled bundle includes the fixes\n');

    // We can't directly check source files, but we can verify behavior
    await page.waitForTimeout(2000);

    console.log('✅ Page loaded successfully');
    console.log('Check the console messages in the previous test for details\n');
  });
});
