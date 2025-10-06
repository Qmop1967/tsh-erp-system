const puppeteer = require('puppeteer-core');

async function checkFrontend() {
    console.log('🔍 Connecting to Chrome DevTools...\n');
    
    let browser;
    try {
        // Connect to existing Chrome instance
        browser = await puppeteer.connect({
            browserURL: 'http://localhost:9222',
            defaultViewport: null
        });
        
        console.log('✅ Connected to Chrome\n');
        
        // Get all pages
        const pages = await browser.pages();
        console.log(`📄 Found ${pages.length} page(s)\n`);
        
        // Create or use first page
        let page;
        if (pages.length > 0) {
            page = pages[0];
        } else {
            page = await browser.newPage();
        }
        
        console.log('🌐 Navigating to http://localhost:5173...\n');
        
        // Navigate to frontend
        try {
            await page.goto('http://localhost:5173', {
                waitUntil: 'networkidle2',
                timeout: 30000
            });
            console.log('✅ Page loaded successfully\n');
        } catch (navError) {
            console.error('⚠️  Navigation error:', navError.message);
            console.log('Trying alternative approach...\n');
            
            // Try without waiting
            await page.goto('http://localhost:5173', {
                waitUntil: 'load',
                timeout: 15000
            });
        }
        
        // Wait a bit for React to render
        await page.waitForTimeout(2000);
        
        // Get page title
        const title = await page.title();
        console.log(`📌 Page Title: "${title}"\n`);
        
        // Get page URL
        const url = page.url();
        console.log(`🔗 Current URL: ${url}\n`);
        
        // Check for console errors
        console.log('🔍 Checking browser console...\n');
        const consoleLogs = [];
        
        page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            consoleLogs.push({ type, text });
            
            const emoji = {
                'error': '❌',
                'warning': '⚠️ ',
                'info': 'ℹ️ ',
                'log': '📝'
            }[type] || '📝';
            
            console.log(`${emoji} [${type.toUpperCase()}] ${text}`);
        });
        
        // Check for page errors
        page.on('pageerror', error => {
            console.log(`❌ [PAGE ERROR] ${error.message}`);
        });
        
        // Check for request failures
        page.on('requestfailed', request => {
            console.log(`❌ [REQUEST FAILED] ${request.url()} - ${request.failure().errorText}`);
        });
        
        // Wait to collect console messages
        await page.waitForTimeout(3000);
        
        // Get network requests
        console.log('\n🌐 Checking network activity...\n');
        
        // Take a screenshot
        console.log('📸 Taking screenshot...\n');
        await page.screenshot({
            path: '/Users/khaleelal-mulla/TSH_ERP_System_Local/frontend-screenshot.png',
            fullPage: false
        });
        console.log('✅ Screenshot saved: frontend-screenshot.png\n');
        
        // Check for React errors
        const reactErrors = await page.evaluate(() => {
            const errors = [];
            
            // Check for React error boundaries
            const errorElements = document.querySelectorAll('[data-error], .error-boundary, .react-error');
            errorElements.forEach(el => {
                errors.push({
                    type: 'React Error',
                    message: el.textContent || el.innerHTML
                });
            });
            
            // Check if React is loaded
            const hasReact = !!window.React || !!document.querySelector('[data-reactroot]');
            
            return {
                errors,
                hasReact,
                bodyClasses: document.body.className,
                bodyContent: document.body.innerText.substring(0, 200)
            };
        });
        
        console.log('⚛️  React Status:');
        console.log(`   - React detected: ${reactErrors.hasReact ? '✅ Yes' : '❌ No'}`);
        console.log(`   - Body classes: "${reactErrors.bodyClasses}"`);
        console.log(`   - Content preview: "${reactErrors.bodyContent.substring(0, 100)}..."\n`);
        
        if (reactErrors.errors.length > 0) {
            console.log('❌ React Errors Found:');
            reactErrors.errors.forEach(err => {
                console.log(`   - ${err.type}: ${err.message}`);
            });
        } else {
            console.log('✅ No React errors detected\n');
        }
        
        // Get all loaded resources
        const metrics = await page.metrics();
        console.log('📊 Page Metrics:');
        console.log(`   - Scripts: ${metrics.ScriptDuration || 'N/A'}`);
        console.log(`   - Layout: ${metrics.LayoutDuration || 'N/A'}`);
        console.log(`   - RecalcStyle: ${metrics.RecalcStyleDuration || 'N/A'}\n`);
        
        // Summary
        console.log('═══════════════════════════════════════');
        console.log('📋 SUMMARY');
        console.log('═══════════════════════════════════════');
        console.log(`✅ Frontend is accessible at: ${url}`);
        console.log(`📄 Page Title: ${title}`);
        console.log(`⚛️  React: ${reactErrors.hasReact ? 'Loaded' : 'Not detected'}`);
        console.log(`📊 Console Messages: ${consoleLogs.length}`);
        console.log(`❌ Errors: ${consoleLogs.filter(l => l.type === 'error').length}`);
        console.log(`⚠️  Warnings: ${consoleLogs.filter(l => l.type === 'warning').length}`);
        console.log('═══════════════════════════════════════\n');
        
        // Don't disconnect, keep browser open
        console.log('✅ Inspection complete! Browser remains open for further testing.\n');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.error(error.stack);
    }
}

// Run the check
checkFrontend().catch(console.error);
