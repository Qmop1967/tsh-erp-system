/**
 * TSH ERP Login Page - Manual Chrome DevTools MCP Verification
 * 
 * This script provides a quick manual verification of the login page
 * using Chrome DevTools MCP capabilities.
 */

const { chromium } = require('playwright');

async function manualVerificationTest() {
  console.log('🔍 TSH ERP Login Page - Manual Chrome DevTools MCP Verification\n');
  
  let browser, page;
  
  try {
    // Launch browser with DevTools
    browser = await chromium.launch({ 
      headless: false,
      devtools: true,
      args: ['--remote-debugging-port=9222']
    });
    
    page = await browser.newPage();
    
    console.log('✅ Chrome DevTools MCP initialized');
    console.log('🌐 Navigating to http://localhost:5173');
    
    // Navigate to login page
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    
    console.log('📸 Taking screenshot...');
    await page.screenshot({ 
      path: 'test-results/manual-verification-login.png', 
      fullPage: true 
    });
    
    // Check page elements
    const title = await page.title();
    const emailInput = await page.locator('input[type="email"]').count();
    const passwordInput = await page.locator('input[type="password"]').count();
    const submitButton = await page.locator('button[type="submit"]').count();
    
    console.log('📋 Page Analysis:');
    console.log(`   Title: "${title}"`);
    console.log(`   Email Input: ${emailInput > 0 ? '✅ Found' : '❌ Missing'}`);
    console.log(`   Password Input: ${passwordInput > 0 ? '✅ Found' : '❌ Missing'}`);
    console.log(`   Submit Button: ${submitButton > 0 ? '✅ Found' : '❌ Missing'}`);
    
    // Test form interaction
    if (emailInput > 0 && passwordInput > 0) {
      console.log('🧪 Testing form interaction...');
      
      await page.locator('input[type="email"]').fill('admin@tsh-erp.com');
      await page.locator('input[type="password"]').fill('admin123');
      
      console.log('✅ Form fields filled successfully');
      console.log('📸 Taking screenshot with filled form...');
      
      await page.screenshot({ 
        path: 'test-results/manual-verification-filled.png', 
        fullPage: true 
      });
      
      console.log('🔄 Ready for manual login test');
      console.log('💡 Browser will remain open for manual testing');
      console.log('💡 Press Ctrl+C to close browser when done');
      
      // Keep browser open for manual interaction
      await new Promise(resolve => {
        process.on('SIGINT', () => {
          console.log('\\n🔚 Closing browser...');
          resolve();
        });
      });
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
    console.log('✨ Manual verification complete');
  }
}

if (require.main === module) {
  manualVerificationTest();
}

module.exports = { manualVerificationTest };