/**
 * Simplified React Application Test using Chrome DevTools
 */

const puppeteer = require('puppeteer-core');

async function testReactAppSimple() {
    console.log('🚀 Starting React application testing...\n');
    
    let browser, page;
    
    try {
        // Connect to existing Chrome instance
        browser = await puppeteer.connect({
            browserURL: 'http://127.0.0.1:9222',
            defaultViewport: null
        });
        
        // Get all pages and find our React app page
        const pages = await browser.pages();
        page = pages.find(p => p.url().includes('localhost:5173')) || pages[0];
        
        if (!page.url().includes('localhost:5173')) {
            await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
        }
        
        console.log('📍 Connected to React application at:', page.url());
        
        // Test 1: Basic Page Analysis
        console.log('\n🧪 Test 1: Basic Page Analysis');
        console.log('=' .repeat(40));
        
        const basicInfo = await page.evaluate(() => {
            return {
                title: document.title,
                url: window.location.href,
                hasReactRoot: !!document.getElementById('root'),
                reactDetected: typeof window.React !== 'undefined',
                bodyHasContent: document.body.children.length > 0,
                totalElements: document.querySelectorAll('*').length
            };
        });
        
        console.log(`📄 Page Title: ${basicInfo.title}`);
        console.log(`🌐 URL: ${basicInfo.url}`);
        console.log(`⚛️  React Root Found: ${basicInfo.hasReactRoot}`);
        console.log(`⚛️  React Detected: ${basicInfo.reactDetected}`);
        console.log(`📦 Body Has Content: ${basicInfo.bodyHasContent}`);
        console.log(`🔢 Total DOM Elements: ${basicInfo.totalElements}`);
        
        // Test 2: UI Components Detection
        console.log('\n🧪 Test 2: UI Components Detection');
        console.log('=' .repeat(40));
        
        const uiComponents = await page.evaluate(() => {
            const componentSelectors = [
                { name: 'Sidebar', selectors: ['[class*="sidebar"]', 'nav', '[role="navigation"]'] },
                { name: 'Header', selectors: ['[class*="header"]', 'header', '[role="banner"]'] },
                { name: 'Main Content', selectors: ['[class*="main"]', 'main', '[role="main"]'] },
                { name: 'Buttons', selectors: ['button', '[role="button"]'] },
                { name: 'Forms', selectors: ['form', 'input', 'textarea'] },
                { name: 'Links', selectors: ['a[href]'] }
            ];
            
            const results = {};
            componentSelectors.forEach(component => {
                let count = 0;
                component.selectors.forEach(selector => {
                    count += document.querySelectorAll(selector).length;
                });
                results[component.name] = count;
            });
            
            return results;
        });
        
        Object.entries(uiComponents).forEach(([component, count]) => {
            console.log(`${component.padEnd(15)}: ${count} found`);
        });
        
        // Test 3: TSH ERP Specific Elements
        console.log('\n🧪 Test 3: TSH ERP Specific Elements');
        console.log('=' .repeat(40));
        
        const erpElements = await page.evaluate(() => {
            const erpSelectors = [
                { name: 'Dashboard', selectors: ['[class*="dashboard"]', '[data-testid*="dashboard"]'] },
                { name: 'Inventory', selectors: ['[class*="inventory"]', '[href*="inventory"]'] },
                { name: 'Customers', selectors: ['[class*="customer"]', '[href*="customer"]'] },
                { name: 'Sales', selectors: ['[class*="sales"]', '[href*="sales"]'] },
                { name: 'Settings', selectors: ['[class*="settings"]', '[href*="settings"]'] },
                { name: 'User Menu', selectors: ['[class*="user"]', '[class*="profile"]'] }
            ];
            
            const results = {};
            erpSelectors.forEach(element => {
                let count = 0;
                element.selectors.forEach(selector => {
                    count += document.querySelectorAll(selector).length;
                });
                results[element.name] = count;
            });
            
            // Also check for text content that might indicate ERP features
            const textContent = document.body.textContent || '';
            const erpKeywords = ['TSH', 'ERP', 'Dashboard', 'Inventory', 'Sales', 'Customer', 'Order'];
            const foundKeywords = erpKeywords.filter(keyword => 
                textContent.toLowerCase().includes(keyword.toLowerCase())
            );
            
            return { elements: results, keywords: foundKeywords };
        });
        
        console.log('ERP Elements:');
        Object.entries(erpElements.elements).forEach(([element, count]) => {
            console.log(`  ${element.padEnd(15)}: ${count} found`);
        });
        
        console.log(`\n📝 ERP Keywords Found: ${erpElements.keywords.join(', ') || 'None'}`);
        
        // Test 4: Functionality Test
        console.log('\n🧪 Test 4: Basic Functionality Test');
        console.log('=' .repeat(40));
        
        // Test clicking on navigation elements if they exist
        const navigationTest = await page.evaluate(() => {
            const clickableElements = document.querySelectorAll('a[href], button, [role="button"]');
            const navigationElements = Array.from(clickableElements).filter(el => {
                const text = el.textContent?.toLowerCase() || '';
                const href = el.getAttribute('href') || '';
                return text.includes('dashboard') || text.includes('inventory') || 
                       text.includes('customer') || href.includes('dashboard') ||
                       href.includes('inventory') || href.includes('customer');
            });
            
            return {
                totalClickable: clickableElements.length,
                navigationElements: navigationElements.length,
                sampleNavigation: navigationElements.slice(0, 3).map(el => ({
                    text: el.textContent?.trim().substring(0, 30),
                    href: el.getAttribute('href'),
                    tag: el.tagName.toLowerCase()
                }))
            };
        });
        
        console.log(`🖱️  Total Clickable Elements: ${navigationTest.totalClickable}`);
        console.log(`🧭 Navigation Elements: ${navigationTest.navigationElements}`);
        
        if (navigationTest.sampleNavigation.length > 0) {
            console.log('Sample Navigation Elements:');
            navigationTest.sampleNavigation.forEach((nav, index) => {
                console.log(`  ${index + 1}. ${nav.tag}: "${nav.text}" -> ${nav.href || 'no href'}`);
            });
        }
        
        // Test 5: Console Messages
        console.log('\n🧪 Test 5: Console Messages Check');
        console.log('=' .repeat(40));
        
        // Set up console message listeners
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push({
                type: msg.type(),
                text: msg.text(),
                timestamp: new Date().toISOString()
            });
        });
        
        // Trigger a small interaction to generate any console messages
        await page.evaluate(() => {
            // Scroll a bit to trigger any lazy loading or scroll events
            window.scrollTo(0, 100);
            window.scrollTo(0, 0);
        });
        
        await page.waitForTimeout(2000); // Wait for any async operations
        
        const errors = consoleMessages.filter(msg => msg.type === 'error');
        const warnings = consoleMessages.filter(msg => msg.type === 'warning');
        const logs = consoleMessages.filter(msg => msg.type === 'log');
        
        console.log(`❌ Console Errors: ${errors.length}`);
        console.log(`⚠️  Console Warnings: ${warnings.length}`);
        console.log(`📋 Console Logs: ${logs.length}`);
        
        if (errors.length > 0) {
            console.log('Recent Errors:');
            errors.slice(0, 3).forEach((error, index) => {
                console.log(`  ${index + 1}. ${error.text.substring(0, 100)}`);
            });
        }
        
        // Test 6: Performance Check
        console.log('\n🧪 Test 6: Performance Check');
        console.log('=' .repeat(40));
        
        const performanceMetrics = await page.metrics();
        console.log(`💾 JS Heap Used: ${Math.round(performanceMetrics.JSHeapUsedSize / 1024 / 1024)} MB`);
        console.log(`💽 JS Heap Total: ${Math.round(performanceMetrics.JSHeapTotalSize / 1024 / 1024)} MB`);
        console.log(`📊 DOM Nodes: ${performanceMetrics.Nodes}`);
        console.log(`🎭 Event Listeners: ${performanceMetrics.JSEventListeners}`);
        
        // Final summary
        const testResult = {
            success: true,
            timestamp: new Date().toISOString(),
            summary: {
                pageLoaded: basicInfo.bodyHasContent,
                reactDetected: basicInfo.reactDetected,
                hasReactRoot: basicInfo.hasReactRoot,
                totalElements: basicInfo.totalElements,
                uiComponents: uiComponents,
                erpFeatures: erpElements.keywords.length > 0,
                consoleErrors: errors.length,
                navigationElements: navigationTest.navigationElements,
                performanceMemory: Math.round(performanceMetrics.JSHeapUsedSize / 1024 / 1024)
            }
        };
        
        console.log('\n🎉 Testing completed successfully!');
        return testResult;
        
    } catch (error) {
        console.error('❌ Testing failed:', error.message);
        return {
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

// Run the test
if (require.main === module) {
    testReactAppSimple().then(result => {
        console.log('\n📊 Final Test Result:');
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
    });
}

module.exports = { testReactAppSimple };