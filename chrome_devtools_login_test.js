/**
 * TSH ERP System - Login Page Testing via Chrome DevTools MCP
 * 
 * This script provides comprehensive testing of the TSH ERP login page
 * using Chrome DevTools MCP server capabilities for deep inspection.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class TSHLoginPageTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.testResults = {
      timestamp: new Date().toISOString(),
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        warnings: 0
      },
      tests: [],
      screenshots: [],
      performance: {},
      console_logs: [],
      network_requests: [],
      errors: []
    };
  }

  async initialize() {
    console.log('🚀 Initializing Chrome DevTools MCP Testing for TSH ERP Login Page...\n');
    
    // Launch browser with DevTools protocol enabled
    this.browser = await chromium.launch({
      headless: false, // Keep visible for DevTools interaction
      devtools: true,
      args: [
        '--remote-debugging-port=9222',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--allow-running-insecure-content'
      ]
    });

    this.page = await this.browser.newPage();
    
    // Enable all DevTools domains
    await this.page.route('**/*', route => route.continue());
    
    // Set viewport for consistent testing
    await this.page.setViewportSize({ width: 1920, height: 1080 });
    
    // Setup event listeners for comprehensive monitoring
    this.setupEventListeners();
    
    console.log('✅ Chrome DevTools MCP initialized successfully\n');
  }

  setupEventListeners() {
    // Console monitoring
    this.page.on('console', msg => {
      this.testResults.console_logs.push({
        type: msg.type(),
        text: msg.text(),
        timestamp: new Date().toISOString(),
        location: msg.location()
      });
    });

    // Network monitoring
    this.page.on('request', request => {
      this.testResults.network_requests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        timestamp: new Date().toISOString(),
        type: 'request'
      });
    });

    this.page.on('response', response => {
      this.testResults.network_requests.push({
        url: response.url(),
        status: response.status(),
        headers: response.headers(),
        timestamp: new Date().toISOString(),
        type: 'response'
      });
    });

    // Error monitoring
    this.page.on('pageerror', error => {
      this.testResults.errors.push({
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        type: 'javascript_error'
      });
    });
  }

  async addTest(name, status, details, screenshot = null) {
    const test = {
      name,
      status, // PASS, FAIL, WARNING
      details,
      timestamp: new Date().toISOString(),
      screenshot
    };
    
    this.testResults.tests.push(test);
    this.testResults.summary.total++;
    
    if (status === 'PASS') this.testResults.summary.passed++;
    else if (status === 'FAIL') this.testResults.summary.failed++;
    else if (status === 'WARNING') this.testResults.summary.warnings++;
    
    const statusIcon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️';
    console.log(`${statusIcon} ${name}: ${details}`);
    
    return test;
  }

  async takeScreenshot(name, description) {
    const filename = `tsh-login-test-${name}-${Date.now()}.png`;
    const filepath = path.join(__dirname, 'test-results', filename);
    
    // Ensure directory exists
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    await this.page.screenshot({ 
      path: filepath, 
      fullPage: true,
      quality: 90
    });
    
    this.testResults.screenshots.push({
      name,
      description,
      filename,
      filepath,
      timestamp: new Date().toISOString()
    });
    
    console.log(`📸 Screenshot saved: ${filename}`);
    return filepath;
  }

  async testPageLoad() {
    console.log('📋 Phase 1: Page Load Testing\n');
    
    try {
      const startTime = Date.now();
      
      // Navigate to login page
      await this.page.goto('http://localhost:5173', { 
        waitUntil: 'networkidle',
        timeout: 10000 
      });
      
      const loadTime = Date.now() - startTime;
      this.testResults.performance.page_load_time = loadTime;
      
      await this.takeScreenshot('01-initial-load', 'Initial page load');
      
      // Test page title
      const title = await this.page.title();
      await this.addTest(
        'Page Title',
        title.includes('TSH ERP') ? 'PASS' : 'FAIL',
        `Title: "${title}"`
      );
      
      // Test page load time
      await this.addTest(
        'Page Load Performance',
        loadTime < 3000 ? 'PASS' : loadTime < 5000 ? 'WARNING' : 'FAIL',
        `Load time: ${loadTime}ms`
      );
      
      // Test if login form is visible
      const loginCard = await this.page.isVisible('.min-h-screen');
      await this.addTest(
        'Login Container Visibility',
        loginCard ? 'PASS' : 'FAIL',
        loginCard ? 'Login container is visible' : 'Login container not found'
      );
      
    } catch (error) {
      await this.addTest('Page Load', 'FAIL', `Error: ${error.message}`);
    }
  }

  async testLoginFormElements() {
    console.log('\n📋 Phase 2: Login Form Elements Testing\n');
    
    try {
      // Test email input field
      const emailInput = await this.page.locator('input[type="email"]');
      const emailExists = await emailInput.count() > 0;
      const emailPlaceholder = emailExists ? await emailInput.getAttribute('placeholder') : '';
      
      await this.addTest(
        'Email Input Field',
        emailExists ? 'PASS' : 'FAIL',
        emailExists ? `Found with placeholder: "${emailPlaceholder}"` : 'Email input not found'
      );
      
      // Test password input field
      const passwordInput = await this.page.locator('input[type="password"]');
      const passwordExists = await passwordInput.count() > 0;
      const passwordPlaceholder = passwordExists ? await passwordInput.getAttribute('placeholder') : '';
      
      await this.addTest(
        'Password Input Field',
        passwordExists ? 'PASS' : 'FAIL',
        passwordExists ? `Found with placeholder: "${passwordPlaceholder}"` : 'Password input not found'
      );
      
      // Test login button
      const loginButton = await this.page.locator('button[type="submit"]');
      const buttonExists = await loginButton.count() > 0;
      const buttonText = buttonExists ? await loginButton.textContent() : '';
      
      await this.addTest(
        'Login Submit Button',
        buttonExists ? 'PASS' : 'FAIL',
        buttonExists ? `Found with text: "${buttonText}"` : 'Login button not found'
      );
      
      // Test form validation attributes
      const emailRequired = emailExists ? await emailInput.getAttribute('required') !== null : false;
      const passwordRequired = passwordExists ? await passwordInput.getAttribute('required') !== null : false;
      
      await this.addTest(
        'Form Validation',
        (emailRequired && passwordRequired) ? 'PASS' : 'WARNING',
        `Email required: ${emailRequired}, Password required: ${passwordRequired}`
      );
      
      // Test accessibility labels
      const emailLabel = await this.page.locator('label[for="email"]').count() > 0;
      const passwordLabel = await this.page.locator('label[for="password"]').count() > 0;
      
      await this.addTest(
        'Accessibility Labels',
        (emailLabel && passwordLabel) ? 'PASS' : 'WARNING',
        `Email label: ${emailLabel}, Password label: ${passwordLabel}`
      );
      
      await this.takeScreenshot('02-form-elements', 'Login form elements analysis');
      
    } catch (error) {
      await this.addTest('Form Elements Test', 'FAIL', `Error: ${error.message}`);
    }
  }

  async testFormInteractions() {
    console.log('\n📋 Phase 3: Form Interactions Testing\n');
    
    try {
      // Test email input interaction
      const emailInput = await this.page.locator('input[type="email"]');
      if (await emailInput.count() > 0) {
        await emailInput.fill('test@example.com');
        const emailValue = await emailInput.inputValue();
        
        await this.addTest(
          'Email Input Interaction',
          emailValue === 'test@example.com' ? 'PASS' : 'FAIL',
          `Input value: "${emailValue}"`
        );
      }
      
      // Test password input interaction
      const passwordInput = await this.page.locator('input[type="password"]');
      if (await passwordInput.count() > 0) {
        await passwordInput.fill('testpassword');
        const passwordValue = await passwordInput.inputValue();
        
        await this.addTest(
          'Password Input Interaction',
          passwordValue === 'testpassword' ? 'PASS' : 'FAIL',
          `Input value: "${passwordValue.replace(/./g, '*')}"`
        );
      }
      
      await this.takeScreenshot('03-form-filled', 'Form with test credentials filled');
      
      // Clear form
      await emailInput.fill('');
      await passwordInput.fill('');
      
    } catch (error) {
      await this.addTest('Form Interactions Test', 'FAIL', `Error: ${error.message}`);
    }
  }

  async testValidLogin() {
    console.log('\n📋 Phase 4: Valid Login Testing\n');
    
    try {
      const emailInput = await this.page.locator('input[type="email"]');
      const passwordInput = await this.page.locator('input[type="password"]');
      const loginButton = await this.page.locator('button[type="submit"]');
      
      // Fill with valid credentials
      await emailInput.fill('admin@tsh-erp.com');
      await passwordInput.fill('admin123');
      
      await this.takeScreenshot('04-valid-credentials', 'Valid credentials entered');
      
      // Monitor network requests during login
      const loginPromise = this.page.waitForResponse(
        response => response.url().includes('login') || response.url().includes('auth'),
        { timeout: 10000 }
      );
      
      // Submit form
      await loginButton.click();
      
      try {
        const response = await loginPromise;
        const status = response.status();
        const responseBody = await response.text();
        
        await this.addTest(
          'Login API Response',
          status === 200 ? 'PASS' : 'FAIL',
          `Status: ${status}, Response: ${responseBody.substring(0, 100)}...`
        );
        
        // Wait for navigation or dashboard
        await this.page.waitForTimeout(3000);
        
        const currentUrl = this.page.url();
        const isRedirected = !currentUrl.includes('localhost:5173') || currentUrl.includes('dashboard');
        
        await this.addTest(
          'Login Navigation',
          isRedirected ? 'PASS' : 'FAIL',
          `Current URL: ${currentUrl}`
        );
        
        await this.takeScreenshot('05-after-login', 'Page after login attempt');
        
      } catch (error) {
        await this.addTest('Login Network Request', 'FAIL', `No login response received: ${error.message}`);
      }
      
    } catch (error) {
      await this.addTest('Valid Login Test', 'FAIL', `Error: ${error.message}`);
    }
  }

  async testInvalidLogin() {
    console.log('\n📋 Phase 5: Invalid Login Testing\n');
    
    try {
      // Navigate back to login if redirected
      if (!this.page.url().includes('localhost:5173')) {
        await this.page.goto('http://localhost:5173');
        await this.page.waitForLoadState('networkidle');
      }
      
      const emailInput = await this.page.locator('input[type="email"]');
      const passwordInput = await this.page.locator('input[type="password"]');
      const loginButton = await this.page.locator('button[type="submit"]');
      
      // Test with invalid credentials
      await emailInput.fill('invalid@test.com');
      await passwordInput.fill('wrongpassword');
      
      await this.takeScreenshot('06-invalid-credentials', 'Invalid credentials entered');
      
      // Submit form
      await loginButton.click();
      
      // Wait for error message
      await this.page.waitForTimeout(2000);
      
      // Check for error display
      const errorMessage = await this.page.locator('.bg-red-50, .text-red-700, .error').first();
      const hasError = await errorMessage.count() > 0;
      const errorText = hasError ? await errorMessage.textContent() : '';
      
      await this.addTest(
        'Invalid Login Error Handling',
        hasError ? 'PASS' : 'FAIL',
        hasError ? `Error shown: "${errorText}"` : 'No error message displayed'
      );
      
      await this.takeScreenshot('07-error-message', 'Error message display');
      
    } catch (error) {
      await this.addTest('Invalid Login Test', 'FAIL', `Error: ${error.message}`);
    }
  }

  async testResponsiveDesign() {
    console.log('\n📋 Phase 6: Responsive Design Testing\n');
    
    const viewports = [
      { name: 'Desktop', width: 1920, height: 1080 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Mobile', width: 375, height: 667 }
    ];
    
    for (const viewport of viewports) {
      try {
        await this.page.setViewportSize({ width: viewport.width, height: viewport.height });
        await this.page.waitForTimeout(1000);
        
        const loginCard = await this.page.locator('.max-w-md').first();
        const isVisible = await loginCard.isVisible();
        
        await this.addTest(
          `${viewport.name} Responsive Design`,
          isVisible ? 'PASS' : 'FAIL',
          `Login form visibility at ${viewport.width}x${viewport.height}: ${isVisible}`
        );
        
        await this.takeScreenshot(`08-${viewport.name.toLowerCase()}`, `${viewport.name} view`);
        
      } catch (error) {
        await this.addTest(`${viewport.name} Responsive Test`, 'FAIL', `Error: ${error.message}`);
      }
    }
    
    // Reset to desktop view
    await this.page.setViewportSize({ width: 1920, height: 1080 });
  }

  async testPerformanceMetrics() {
    console.log('\n📋 Phase 7: Performance Metrics Analysis\n');
    
    try {
      // Get performance metrics
      const metrics = await this.page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
      });
      
      this.testResults.performance = { ...this.testResults.performance, ...metrics };
      
      await this.addTest(
        'DOM Content Loaded',
        metrics.domContentLoaded < 1000 ? 'PASS' : 'WARNING',
        `${metrics.domContentLoaded.toFixed(2)}ms`
      );
      
      await this.addTest(
        'First Contentful Paint',
        metrics.firstContentfulPaint < 2000 ? 'PASS' : 'WARNING',
        `${metrics.firstContentfulPaint.toFixed(2)}ms`
      );
      
    } catch (error) {
      await this.addTest('Performance Metrics', 'FAIL', `Error: ${error.message}`);
    }
  }

  async generateReport() {
    console.log('\n📋 Generating Comprehensive Test Report...\n');
    
    const report = {
      ...this.testResults,
      browser_info: {
        userAgent: await this.page.evaluate(() => navigator.userAgent),
        viewport: await this.page.viewportSize(),
        url: this.page.url()
      },
      test_environment: {
        backend_url: 'http://localhost:8000',
        frontend_url: 'http://localhost:5173',
        test_framework: 'Chrome DevTools MCP + Playwright'
      }
    };
    
    // Save detailed JSON report
    const reportPath = path.join(__dirname, 'test-results', `tsh-login-test-report-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Generate HTML report
    const htmlReport = this.generateHTMLReport(report);
    const htmlReportPath = path.join(__dirname, 'test-results', `tsh-login-test-report-${Date.now()}.html`);
    fs.writeFileSync(htmlReportPath, htmlReport);
    
    console.log('📊 Test Results Summary:');
    console.log(`   Total Tests: ${report.summary.total}`);
    console.log(`   ✅ Passed: ${report.summary.passed}`);
    console.log(`   ❌ Failed: ${report.summary.failed}`);
    console.log(`   ⚠️  Warnings: ${report.summary.warnings}`);
    console.log(`\n📁 Reports saved:`);
    console.log(`   JSON: ${reportPath}`);
    console.log(`   HTML: ${htmlReportPath}`);
    
    return report;
  }

  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSH ERP Login Page - Chrome DevTools MCP Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: flex; gap: 20px; margin-bottom: 20px; }
        .metric { background: white; padding: 15px; border-radius: 8px; border: 1px solid #ddd; flex: 1; text-align: center; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .warning { color: #ffc107; }
        .test-results { margin-bottom: 30px; }
        .test-item { padding: 10px; border-bottom: 1px solid #eee; }
        .screenshots { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .screenshot { border: 1px solid #ddd; padding: 10px; border-radius: 8px; }
        .timestamp { color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 TSH ERP System - Login Page Test Report</h1>
        <p><strong>Test Framework:</strong> Chrome DevTools MCP + Playwright</p>
        <p><strong>Timestamp:</strong> ${report.timestamp}</p>
        <p><strong>Frontend URL:</strong> ${report.test_environment.frontend_url}</p>
        <p><strong>Backend URL:</strong> ${report.test_environment.backend_url}</p>
    </div>

    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div style="font-size: 2em; font-weight: bold;">${report.summary.total}</div>
        </div>
        <div class="metric pass">
            <h3>Passed</h3>
            <div style="font-size: 2em; font-weight: bold;">${report.summary.passed}</div>
        </div>
        <div class="metric fail">
            <h3>Failed</h3>
            <div style="font-size: 2em; font-weight: bold;">${report.summary.failed}</div>
        </div>
        <div class="metric warning">
            <h3>Warnings</h3>
            <div style="font-size: 2em; font-weight: bold;">${report.summary.warnings}</div>
        </div>
    </div>

    <div class="test-results">
        <h2>📋 Test Results</h2>
        ${report.tests.map(test => `
            <div class="test-item">
                <span class="${test.status.toLowerCase()}">${test.status === 'PASS' ? '✅' : test.status === 'FAIL' ? '❌' : '⚠️'}</span>
                <strong>${test.name}</strong>: ${test.details}
                <div class="timestamp">${test.timestamp}</div>
            </div>
        `).join('')}
    </div>

    <div class="performance">
        <h2>⚡ Performance Metrics</h2>
        <ul>
            <li><strong>Page Load Time:</strong> ${report.performance.page_load_time || 0}ms</li>
            <li><strong>DOM Content Loaded:</strong> ${report.performance.domContentLoaded || 0}ms</li>
            <li><strong>First Contentful Paint:</strong> ${report.performance.firstContentfulPaint || 0}ms</li>
        </ul>
    </div>

    <div class="screenshots">
        <h2>📸 Screenshots</h2>
        ${report.screenshots.map(screenshot => `
            <div class="screenshot">
                <h4>${screenshot.name}</h4>
                <p>${screenshot.description}</p>
                <p><strong>File:</strong> ${screenshot.filename}</p>
                <div class="timestamp">${screenshot.timestamp}</div>
            </div>
        `).join('')}
    </div>

    <div class="console-logs">
        <h2>📝 Console Logs (${report.console_logs.length})</h2>
        ${report.console_logs.slice(0, 10).map(log => `
            <div class="test-item">
                <strong>[${log.type.toUpperCase()}]</strong> ${log.text}
                <div class="timestamp">${log.timestamp}</div>
            </div>
        `).join('')}
        ${report.console_logs.length > 10 ? `<p><em>... and ${report.console_logs.length - 10} more logs</em></p>` : ''}
    </div>

    <div class="network-requests">
        <h2>🌐 Network Activity Summary</h2>
        <p><strong>Total Requests:</strong> ${report.network_requests.filter(r => r.type === 'request').length}</p>
        <p><strong>Total Responses:</strong> ${report.network_requests.filter(r => r.type === 'response').length}</p>
    </div>
</body>
</html>`;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async runFullTest() {
    try {
      await this.initialize();
      
      await this.testPageLoad();
      await this.testLoginFormElements();
      await this.testFormInteractions();
      await this.testValidLogin();
      await this.testInvalidLogin();
      await this.testResponsiveDesign();
      await this.testPerformanceMetrics();
      
      const report = await this.generateReport();
      
      return report;
      
    } catch (error) {
      console.error('❌ Test execution failed:', error);
      await this.addTest('Test Execution', 'FAIL', `Critical error: ${error.message}`);
    } finally {
      await this.cleanup();
    }
  }
}

// Run the comprehensive test
async function main() {
  console.log('🎯 TSH ERP System - Chrome DevTools MCP Login Page Testing\n');
  console.log('=' .repeat(60));
  
  const tester = new TSHLoginPageTester();
  const report = await tester.runFullTest();
  
  console.log('\n' + '='.repeat(60));
  console.log('✨ Chrome DevTools MCP Testing Complete!');
  
  return report;
}

// Export for use as module or run directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { TSHLoginPageTester };