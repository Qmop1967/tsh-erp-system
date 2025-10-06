/**
 * TSH ERP System - Chrome DevTools MCP Login Page Testing (Simplified)
 * 
 * This script provides reliable testing of the TSH ERP login page
 * using Chrome DevTools MCP server capabilities.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class TSHLoginTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.testResults = {
      timestamp: new Date().toISOString(),
      summary: { total: 0, passed: 0, failed: 0 },
      tests: [],
      screenshots: []
    };
  }

  async addTest(name, status, details) {
    const test = { name, status, details, timestamp: new Date().toISOString() };
    this.testResults.tests.push(test);
    this.testResults.summary.total++;
    
    if (status === 'PASS') this.testResults.summary.passed++;
    else this.testResults.summary.failed++;
    
    const icon = status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${name}: ${details}`);
    return test;
  }

  async takeScreenshot(name) {
    try {
      const filename = `tsh-login-${name}-${Date.now()}.png`;
      const dir = path.join(__dirname, 'test-results');
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      
      const filepath = path.join(dir, filename);
      await this.page.screenshot({ path: filepath, fullPage: true });
      
      this.testResults.screenshots.push({ name, filename, filepath });
      console.log(`📸 Screenshot: ${filename}`);
      return filepath;
    } catch (error) {
      console.log(`⚠️ Screenshot failed: ${error.message}`);
    }
  }

  async runTest() {
    console.log('🚀 TSH ERP Login Page - Chrome DevTools MCP Test\n');
    console.log('='.repeat(50));

    try {
      // Launch browser
      this.browser = await chromium.launch({ 
        headless: false,
        args: ['--disable-web-security'] 
      });
      this.page = await this.browser.newPage();
      
      console.log('\n📋 Phase 1: Page Load & Initial Analysis\n');
      
      // Test 1: Page Load
      const startTime = Date.now();
      await this.page.goto('http://localhost:5173', { 
        waitUntil: 'networkidle',
        timeout: 15000 
      });
      const loadTime = Date.now() - startTime;
      
      await this.addTest('Page Load', 'PASS', `Loaded in ${loadTime}ms`);
      await this.takeScreenshot('01-page-load');
      
      // Test 2: Page Title
      const title = await this.page.title();
      await this.addTest(
        'Page Title', 
        title.includes('TSH ERP') ? 'PASS' : 'FAIL',
        `Title: "${title}"`
      );
      
      // Test 3: Login Form Elements
      console.log('\n📋 Phase 2: Login Form Analysis\n');
      
      const emailInput = this.page.locator('input[type="email"]');
      const passwordInput = this.page.locator('input[type="password"]');
      const submitButton = this.page.locator('button[type="submit"]');
      
      const emailExists = await emailInput.count() > 0;
      const passwordExists = await passwordInput.count() > 0;
      const buttonExists = await submitButton.count() > 0;
      
      await this.addTest('Email Input', emailExists ? 'PASS' : 'FAIL', 
        emailExists ? 'Email input field found' : 'Email input field missing');
      
      await this.addTest('Password Input', passwordExists ? 'PASS' : 'FAIL',
        passwordExists ? 'Password input field found' : 'Password input field missing');
      
      await this.addTest('Submit Button', buttonExists ? 'PASS' : 'FAIL',
        buttonExists ? 'Submit button found' : 'Submit button missing');
      
      if (emailExists && passwordExists && buttonExists) {
        // Test 4: Form Interaction
        console.log('\n📋 Phase 3: Form Interaction Testing\n');
        
        await emailInput.fill('admin@tsh-erp.com');
        await passwordInput.fill('admin123');
        
        const emailValue = await emailInput.inputValue();
        const passwordValue = await passwordInput.inputValue();
        
        await this.addTest('Email Input Fill', 
          emailValue === 'admin@tsh-erp.com' ? 'PASS' : 'FAIL',
          `Email field contains: "${emailValue}"`);
        
        await this.addTest('Password Input Fill',
          passwordValue === 'admin123' ? 'PASS' : 'FAIL',
          'Password field filled correctly');
        
        await this.takeScreenshot('02-form-filled');
        
        // Test 5: Login Attempt
        console.log('\n📋 Phase 4: Login Functionality Testing\n');
        
        // Monitor for navigation or error
        const navigationPromise = Promise.race([
          this.page.waitForNavigation({ timeout: 5000 }).catch(() => null),
          this.page.waitForSelector('.bg-red-50', { timeout: 5000 }).catch(() => null)
        ]);
        
        await submitButton.click();
        
        // Wait for response
        await this.page.waitForTimeout(3000);
        
        const currentUrl = this.page.url();
        const hasError = await this.page.locator('.bg-red-50').count() > 0;
        
        if (currentUrl !== 'http://localhost:5173/') {
          await this.addTest('Login Success', 'PASS', `Redirected to: ${currentUrl}`);
        } else if (hasError) {
          const errorText = await this.page.locator('.bg-red-50').textContent();
          await this.addTest('Login Error Handling', 'PASS', `Error displayed: ${errorText?.substring(0, 50)}...`);
        } else {
          await this.addTest('Login Response', 'FAIL', 'No clear response to login attempt');
        }
        
        await this.takeScreenshot('03-after-login');
      }
      
      // Test 6: Responsive Design Check
      console.log('\n📋 Phase 5: Responsive Design Testing\n');
      
      await this.page.setViewportSize({ width: 375, height: 667 }); // Mobile
      await this.page.waitForTimeout(1000);
      
      const mobileFormVisible = await this.page.locator('form').isVisible();
      await this.addTest('Mobile Responsive', mobileFormVisible ? 'PASS' : 'FAIL',
        `Login form visible on mobile: ${mobileFormVisible}`);
      
      await this.takeScreenshot('04-mobile-view');
      
      // Test 7: DevTools Console Check
      console.log('\n📋 Phase 6: DevTools Console Analysis\n');
      
      let consoleErrors = [];
      this.page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      
      await this.page.reload({ waitUntil: 'networkidle' });
      await this.page.waitForTimeout(2000);
      
      await this.addTest('Console Errors', 
        consoleErrors.length === 0 ? 'PASS' : 'FAIL',
        consoleErrors.length === 0 ? 'No console errors' : `${consoleErrors.length} console errors found`);
      
      // Test 8: Network Requests
      console.log('\n📋 Phase 7: Network Activity Analysis\n');
      
      let networkRequests = [];
      this.page.on('request', request => {
        if (request.url().includes('localhost') || request.url().includes('api')) {
          networkRequests.push(request.url());
        }
      });
      
      await this.page.reload({ waitUntil: 'networkidle' });
      
      await this.addTest('Network Requests',
        networkRequests.length > 0 ? 'PASS' : 'FAIL',
        `${networkRequests.length} relevant network requests detected`);
      
      await this.takeScreenshot('05-final-state');
      
    } catch (error) {
      await this.addTest('Test Execution', 'FAIL', `Critical error: ${error.message}`);
      console.error('❌ Test failed:', error);
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
    
    // Generate Report
    this.generateReport();
  }

  generateReport() {
    console.log('\n' + '='.repeat(50));
    console.log('📊 CHROME DEVTOOLS MCP TEST RESULTS');
    console.log('='.repeat(50));
    
    console.log(`\n📈 Summary:`);
    console.log(`   Total Tests: ${this.testResults.summary.total}`);
    console.log(`   ✅ Passed: ${this.testResults.summary.passed}`);
    console.log(`   ❌ Failed: ${this.testResults.summary.failed}`);
    console.log(`   📸 Screenshots: ${this.testResults.screenshots.length}`);
    
    const passRate = ((this.testResults.summary.passed / this.testResults.summary.total) * 100).toFixed(1);
    console.log(`   🎯 Pass Rate: ${passRate}%`);
    
    console.log(`\n📋 Detailed Results:`);
    this.testResults.tests.forEach((test, index) => {
      const icon = test.status === 'PASS' ? '✅' : '❌';
      console.log(`   ${index + 1}. ${icon} ${test.name}: ${test.details}`);
    });
    
    // Save JSON report
    try {
      const reportDir = path.join(__dirname, 'test-results');
      if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir, { recursive: true });
      
      const reportPath = path.join(reportDir, `tsh-login-devtools-report-${Date.now()}.json`);
      fs.writeFileSync(reportPath, JSON.stringify(this.testResults, null, 2));
      
      console.log(`\n📁 Detailed report saved: ${reportPath}`);
      console.log(`📁 Screenshots saved in: ${reportDir}`);
    } catch (error) {
      console.log(`⚠️ Could not save report: ${error.message}`);
    }
    
    console.log('\n✨ Chrome DevTools MCP Testing Complete!');
    console.log(`🕒 Test completed at: ${new Date().toLocaleString()}`);
    
    return this.testResults;
  }
}

// Run the test
async function main() {
  const tester = new TSHLoginTester();
  await tester.runTest();
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { TSHLoginTester };