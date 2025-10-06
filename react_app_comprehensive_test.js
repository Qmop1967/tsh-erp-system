/**
 * Comprehensive React Application Testing via Chrome DevTools MCP
 * Tests the TSH ERP System frontend application
 */

const { chromium } = require('playwright');

async function testReactApp() {
    console.log('🚀 Starting comprehensive React application testing...\n');
    
    let browser, page;
    
    try {
        // Connect to the existing Chrome instance with remote debugging
        browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
        
        // Get the existing page or create a new one
        const context = browser.contexts()[0];
        const pages = context.pages();
        page = pages.length > 0 ? pages[0] : await context.newPage();
        
        // Navigate to the React app
        console.log('📍 Navigating to React application at http://localhost:5173/');
        await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
        
        console.log('✅ Page loaded successfully\n');
        
        // Test 1: Page Load and Basic Structure
        console.log('🧪 Test 1: Page Load and Basic Structure');
        console.log('=' .repeat(50));
        
        const title = await page.title();
        console.log(`📄 Page Title: ${title}`);
        
        const url = page.url();
        console.log(`🌐 Current URL: ${url}`);
        
        // Check if React is loaded
        const reactVersion = await page.evaluate(() => {
            return window.React ? window.React.version || 'React loaded (version unknown)' : 'React not detected';
        });
        console.log(`⚛️  React Status: ${reactVersion}`);
        
        // Test 2: DOM Structure Analysis
        console.log('\n🧪 Test 2: DOM Structure Analysis');
        console.log('=' .repeat(50));
        
        const bodyContent = await page.evaluate(() => {
            const body = document.body;
            return {
                hasContent: body.children.length > 0,
                childrenCount: body.children.length,
                classes: body.className,
                hasReactRoot: !!document.getElementById('root')
            };
        });
        
        console.log(`📦 Body has content: ${bodyContent.hasContent}`);
        console.log(`🔢 Children count: ${bodyContent.childrenCount}`);
        console.log(`🎨 Body classes: ${bodyContent.classes || 'none'}`);
        console.log(`⚛️  React root found: ${bodyContent.hasReactRoot}`);
        
        // Test 3: React Components Detection
        console.log('\n🧪 Test 3: React Components Detection');
        console.log('=' .repeat(50));
        
        const reactComponents = await page.evaluate(() => {
            const root = document.getElementById('root');
            if (!root) return { found: false, message: 'No React root element found' };
            
            const componentElements = [];
            const walker = document.createTreeWalker(
                root,
                NodeFilter.SHOW_ELEMENT,
                {
                    acceptNode: (node) => {
                        // Look for React-specific attributes or components
                        if (node.tagName && (
                            node.hasAttribute('data-reactroot') ||
                            node.className.includes('react') ||
                            node.className.includes('App') ||
                            node.className.includes('layout') ||
                            node.className.includes('sidebar') ||
                            node.className.includes('header')
                        )) {
                            return NodeFilter.FILTER_ACCEPT;
                        }
                        return NodeFilter.FILTER_SKIP;
                    }
                }
            );
            
            let node;
            while (node = walker.nextNode()) {
                componentElements.push({
                    tag: node.tagName,
                    classes: node.className,
                    id: node.id || 'no-id'
                });
            }
            
            return {
                found: componentElements.length > 0,
                components: componentElements,
                totalElements: root.querySelectorAll('*').length
            };
        });
        
        console.log(`🔍 React components found: ${reactComponents.found}`);
        console.log(`📊 Total DOM elements: ${reactComponents.totalElements}`);
        
        if (reactComponents.components && reactComponents.components.length > 0) {
            console.log('🧩 Detected components:');
            reactComponents.components.forEach((comp, index) => {
                console.log(`   ${index + 1}. ${comp.tag} - Classes: ${comp.classes} - ID: ${comp.id}`);
            });
        }
        
        // Test 4: UI Layout Analysis
        console.log('\n🧪 Test 4: UI Layout Analysis');
        console.log('=' .repeat(50));
        
        const layoutAnalysis = await page.evaluate(() => {
            const selectors = [
                '[class*="sidebar"]',
                '[class*="header"]',
                '[class*="nav"]',
                '[class*="menu"]',
                '[class*="dashboard"]',
                '[class*="layout"]',
                '[class*="main"]',
                '[class*="content"]'
            ];
            
            const foundElements = {};
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    foundElements[selector] = {
                        count: elements.length,
                        visible: Array.from(elements).some(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && style.visibility !== 'hidden';
                        })
                    };
                }
            });
            
            return foundElements;
        });
        
        console.log('🎨 Layout elements detected:');
        Object.entries(layoutAnalysis).forEach(([selector, info]) => {
            console.log(`   ${selector}: ${info.count} found, visible: ${info.visible}`);
        });
        
        // Test 5: Interactive Elements Test
        console.log('\n🧪 Test 5: Interactive Elements Test');
        console.log('=' .repeat(50));
        
        const interactiveElements = await page.evaluate(() => {
            const clickableSelectors = [
                'button',
                'a[href]',
                '[role="button"]',
                '[onclick]',
                'input[type="submit"]',
                'input[type="button"]'
            ];
            
            const formSelectors = [
                'input',
                'textarea',
                'select',
                'form'
            ];
            
            const clickable = clickableSelectors.reduce((acc, selector) => {
                const elements = document.querySelectorAll(selector);
                acc[selector] = elements.length;
                return acc;
            }, {});
            
            const forms = formSelectors.reduce((acc, selector) => {
                const elements = document.querySelectorAll(selector);
                acc[selector] = elements.length;
                return acc;
            }, {});
            
            return { clickable, forms };
        });
        
        console.log('🖱️  Clickable elements:');
        Object.entries(interactiveElements.clickable).forEach(([selector, count]) => {
            if (count > 0) console.log(`   ${selector}: ${count}`);
        });
        
        console.log('📝 Form elements:');
        Object.entries(interactiveElements.forms).forEach(([selector, count]) => {
            if (count > 0) console.log(`   ${selector}: ${count}`);
        });
        
        // Test 6: Console Errors and Warnings
        console.log('\n🧪 Test 6: Console Errors and Warnings');
        console.log('=' .repeat(50));
        
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push({
                type: msg.type(),
                text: msg.text(),
                timestamp: new Date().toISOString()
            });
        });
        
        // Wait a bit to collect console messages
        await page.waitForTimeout(2000);
        
        const errors = consoleMessages.filter(msg => msg.type === 'error');
        const warnings = consoleMessages.filter(msg => msg.type === 'warning');
        
        console.log(`❌ Console errors: ${errors.length}`);
        errors.forEach((error, index) => {
            console.log(`   ${index + 1}. ${error.text}`);
        });
        
        console.log(`⚠️  Console warnings: ${warnings.length}`);
        warnings.forEach((warning, index) => {
            console.log(`   ${index + 1}. ${warning.text}`);
        });
        
        // Test 7: Performance Metrics
        console.log('\n🧪 Test 7: Performance Metrics');
        console.log('=' .repeat(50));
        
        const performanceMetrics = await page.evaluate(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            
            return {
                loadTime: navigation ? Math.round(navigation.loadEventEnd - navigation.loadEventStart) : 'N/A',
                domContentLoaded: navigation ? Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart) : 'N/A',
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 'N/A',
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 'N/A'
            };
        });
        
        console.log(`⚡ Load time: ${performanceMetrics.loadTime}ms`);
        console.log(`📋 DOM Content Loaded: ${performanceMetrics.domContentLoaded}ms`);
        console.log(`🎨 First Paint: ${Math.round(performanceMetrics.firstPaint)}ms`);
        console.log(`🖼️  First Contentful Paint: ${Math.round(performanceMetrics.firstContentfulPaint)}ms`);
        
        // Test 8: Accessibility Check
        console.log('\n🧪 Test 8: Basic Accessibility Check');
        console.log('=' .repeat(50));
        
        const accessibilityCheck = await page.evaluate(() => {
            return {
                hasTitle: !!document.title,
                hasLang: !!document.documentElement.lang,
                altTexts: document.querySelectorAll('img[alt]').length,
                totalImages: document.querySelectorAll('img').length,
                labeledInputs: document.querySelectorAll('input[id]').length,
                totalInputs: document.querySelectorAll('input').length,
                headings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
                ariaLabels: document.querySelectorAll('[aria-label]').length
            };
        });
        
        console.log(`📋 Has page title: ${accessibilityCheck.hasTitle}`);
        console.log(`🌐 Has lang attribute: ${accessibilityCheck.hasLang}`);
        console.log(`🖼️  Images with alt text: ${accessibilityCheck.altTexts}/${accessibilityCheck.totalImages}`);
        console.log(`🏷️  Labeled inputs: ${accessibilityCheck.labeledInputs}/${accessibilityCheck.totalInputs}`);
        console.log(`📚 Heading elements: ${accessibilityCheck.headings}`);
        console.log(`♿ ARIA labels: ${accessibilityCheck.ariaLabels}`);
        
        // Test 9: Mobile Responsiveness
        console.log('\n🧪 Test 9: Mobile Responsiveness Test');
        console.log('=' .repeat(50));
        
        // Test different viewport sizes
        const viewports = [
            { name: 'Mobile', width: 375, height: 667 },
            { name: 'Tablet', width: 768, height: 1024 },
            { name: 'Desktop', width: 1920, height: 1080 }
        ];
        
        for (const viewport of viewports) {
            await page.setViewportSize({ width: viewport.width, height: viewport.height });
            await page.waitForTimeout(500); // Allow layout to adjust
            
            const layoutInfo = await page.evaluate(() => {
                return {
                    bodyWidth: document.body.offsetWidth,
                    bodyHeight: document.body.offsetHeight,
                    hasHorizontalScroll: document.body.scrollWidth > window.innerWidth,
                    hasVerticalScroll: document.body.scrollHeight > window.innerHeight
                };
            });
            
            console.log(`📱 ${viewport.name} (${viewport.width}x${viewport.height}):`);
            console.log(`   Body size: ${layoutInfo.bodyWidth}x${layoutInfo.bodyHeight}`);
            console.log(`   Horizontal scroll: ${layoutInfo.hasHorizontalScroll}`);
            console.log(`   Vertical scroll: ${layoutInfo.hasVerticalScroll}`);
        }
        
        // Reset to desktop size
        await page.setViewportSize({ width: 1920, height: 1080 });
        
        // Test 10: Navigation Testing
        console.log('\n🧪 Test 10: Navigation Testing');
        console.log('=' .repeat(50));
        
        const navigationTest = await page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            const internalLinks = links.filter(link => {
                const href = link.getAttribute('href');
                return href && (href.startsWith('/') || href.startsWith('#') || href.includes('localhost'));
            });
            
            const externalLinks = links.filter(link => {
                const href = link.getAttribute('href');
                return href && (href.startsWith('http') && !href.includes('localhost'));
            });
            
            return {
                totalLinks: links.length,
                internalLinks: internalLinks.length,
                externalLinks: externalLinks.length,
                internalHrefs: internalLinks.slice(0, 5).map(link => link.getAttribute('href')) // First 5 for sample
            };
        });
        
        console.log(`🔗 Total links: ${navigationTest.totalLinks}`);
        console.log(`🏠 Internal links: ${navigationTest.internalLinks}`);
        console.log(`🌍 External links: ${navigationTest.externalLinks}`);
        
        if (navigationTest.internalHrefs.length > 0) {
            console.log('📍 Sample internal routes:');
            navigationTest.internalHrefs.forEach((href, index) => {
                console.log(`   ${index + 1}. ${href}`);
            });
        }
        
        console.log('\n🎉 Testing completed successfully!');
        
        return {
            success: true,
            timestamp: new Date().toISOString(),
            summary: {
                pageTitle: title,
                reactLoaded: reactVersion !== 'React not detected',
                totalElements: reactComponents.totalElements,
                consoleErrors: errors.length,
                consoleWarnings: warnings.length,
                performanceLoadTime: performanceMetrics.loadTime,
                totalLinks: navigationTest.totalLinks,
                accessibilityScore: {
                    hasTitle: accessibilityCheck.hasTitle,
                    hasLang: accessibilityCheck.hasLang,
                    altTextCoverage: accessibilityCheck.totalImages > 0 ? 
                        Math.round((accessibilityCheck.altTexts / accessibilityCheck.totalImages) * 100) : 100
                }
            }
        };
        
    } catch (error) {
        console.error('❌ Testing failed:', error.message);
        return {
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        };
    } finally {
        if (browser) {
            console.log('\n🔚 Closing browser connection...');
            // Don't close the browser as it was externally launched
        }
    }
}

// Export for module use or run directly
if (require.main === module) {
    testReactApp().then(result => {
        console.log('\n📊 Final Result:', JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
    });
} else {
    module.exports = { testReactApp };
}