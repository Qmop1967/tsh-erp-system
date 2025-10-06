/**
 * Direct React Application Analysis
 * This script tests the TSH ERP React application by analyzing its DOM structure,
 * components, functionality, and performance directly.
 */

// This script should be run in the browser console or through DevTools
(function() {
    console.log('🚀 Starting TSH ERP React Application Analysis...\n');
    
    const results = {
        timestamp: new Date().toISOString(),
        tests: [],
        summary: {},
        issues: [],
        recommendations: []
    };
    
    // Helper function to add test results
    function addTest(name, status, details) {
        results.tests.push({ name, status, details, timestamp: new Date().toISOString() });
        console.log(`${status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️'} ${name}:`, details);
    }
    
    // Test 1: Basic Page Structure
    console.log('🧪 Test 1: Basic Page Structure');
    console.log('=' .repeat(50));
    
    const basicStructure = {
        title: document.title,
        url: window.location.href,
        hasReactRoot: !!document.getElementById('root'),
        reactDetected: typeof window.React !== 'undefined' || !!window._reactInternalInstance,
        bodyChildren: document.body.children.length,
        totalElements: document.querySelectorAll('*').length,
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight
        }
    };
    
    addTest('Page Title', basicStructure.title ? 'PASS' : 'FAIL', `"${basicStructure.title}"`);
    addTest('React Root Element', basicStructure.hasReactRoot ? 'PASS' : 'FAIL', `Found: ${basicStructure.hasReactRoot}`);
    addTest('React Detection', basicStructure.reactDetected ? 'PASS' : 'WARN', `Detected: ${basicStructure.reactDetected}`);
    addTest('DOM Content', basicStructure.bodyChildren > 0 ? 'PASS' : 'FAIL', `${basicStructure.bodyChildren} child elements`);
    addTest('Total Elements', basicStructure.totalElements > 10 ? 'PASS' : 'WARN', `${basicStructure.totalElements} elements`);
    
    // Test 2: TSH ERP Specific Components
    console.log('\n🧪 Test 2: TSH ERP Components Analysis');
    console.log('=' .repeat(50));
    
    const erpComponents = {
        sidebar: document.querySelectorAll('[class*="sidebar"], nav, [role="navigation"]').length,
        header: document.querySelectorAll('[class*="header"], header, [role="banner"]').length,
        mainContent: document.querySelectorAll('[class*="main"], main, [role="main"]').length,
        dashboard: document.querySelectorAll('[class*="dashboard"], [data-testid*="dashboard"]').length,
        buttons: document.querySelectorAll('button, [role="button"]').length,
        forms: document.querySelectorAll('form, input, textarea, select').length,
        links: document.querySelectorAll('a[href]').length,
        cards: document.querySelectorAll('[class*="card"], [class*="panel"]').length
    };
    
    Object.entries(erpComponents).forEach(([component, count]) => {
        const status = count > 0 ? 'PASS' : 'WARN';
        addTest(`${component.charAt(0).toUpperCase() + component.slice(1)} Elements`, status, `${count} found`);
    });
    
    // Test 3: Navigation and Routing
    console.log('\n🧪 Test 3: Navigation and Routing');
    console.log('=' .repeat(50));
    
    const navigationAnalysis = {
        internalLinks: Array.from(document.querySelectorAll('a[href]')).filter(link => {
            const href = link.getAttribute('href');
            return href && (href.startsWith('/') || href.startsWith('#') || href.includes('localhost'));
        }),
        externalLinks: Array.from(document.querySelectorAll('a[href]')).filter(link => {
            const href = link.getAttribute('href');
            return href && href.startsWith('http') && !href.includes('localhost');
        }),
        routeIndicators: document.querySelectorAll('[class*="route"], [class*="nav"], [class*="menu"]').length
    };
    
    // Extract sample navigation routes
    const sampleRoutes = navigationAnalysis.internalLinks.slice(0, 10).map(link => ({
        text: link.textContent?.trim().substring(0, 30) || 'No text',
        href: link.getAttribute('href'),
        visible: window.getComputedStyle(link).display !== 'none'
    }));
    
    addTest('Internal Navigation Links', navigationAnalysis.internalLinks.length > 0 ? 'PASS' : 'WARN', 
        `${navigationAnalysis.internalLinks.length} found`);
    addTest('External Links', 'INFO', `${navigationAnalysis.externalLinks.length} found`);
    addTest('Route Indicators', navigationAnalysis.routeIndicators > 0 ? 'PASS' : 'WARN', 
        `${navigationAnalysis.routeIndicators} found`);
    
    if (sampleRoutes.length > 0) {
        console.log('📍 Sample Navigation Routes:');
        sampleRoutes.forEach((route, index) => {
            console.log(`   ${index + 1}. "${route.text}" -> ${route.href} (${route.visible ? 'visible' : 'hidden'})`);
        });
    }
    
    // Test 4: ERP Business Logic Indicators
    console.log('\n🧪 Test 4: ERP Business Logic Indicators');
    console.log('=' .repeat(50));
    
    const businessLogic = {
        textContent: document.body.textContent || '',
        dataAttributes: document.querySelectorAll('[data-*]').length,
        formInputs: document.querySelectorAll('input[name], textarea[name], select[name]').length,
        tableElements: document.querySelectorAll('table, [role="table"], [class*="table"]').length,
        listElements: document.querySelectorAll('ul, ol, [role="list"], [class*="list"]').length
    };
    
    // Search for ERP-related keywords in the content
    const erpKeywords = [
        'TSH', 'ERP', 'Dashboard', 'Inventory', 'Sales', 'Customer', 'Order', 
        'Invoice', 'Purchase', 'Warehouse', 'Branch', 'User', 'Report', 
        'Account', 'Payment', 'Product', 'Vendor', 'Stock'
    ];
    
    const foundKeywords = erpKeywords.filter(keyword => 
        businessLogic.textContent.toLowerCase().includes(keyword.toLowerCase())
    );
    
    addTest('ERP Keywords Present', foundKeywords.length > 3 ? 'PASS' : 'WARN', 
        `Found: ${foundKeywords.join(', ')}`);
    addTest('Data Attributes', businessLogic.dataAttributes > 0 ? 'PASS' : 'INFO', 
        `${businessLogic.dataAttributes} elements with data attributes`);
    addTest('Form Inputs', businessLogic.formInputs > 0 ? 'PASS' : 'WARN', 
        `${businessLogic.formInputs} named form inputs`);
    addTest('Table Elements', businessLogic.tableElements > 0 ? 'PASS' : 'INFO', 
        `${businessLogic.tableElements} table elements`);
    addTest('List Elements', businessLogic.listElements > 0 ? 'PASS' : 'INFO', 
        `${businessLogic.listElements} list elements`);
    
    // Test 5: Responsive Design
    console.log('\n🧪 Test 5: Responsive Design');
    console.log('=' .repeat(50));
    
    const responsiveElements = {
        mediaQueries: Array.from(document.styleSheets).reduce((count, sheet) => {
            try {
                return count + Array.from(sheet.cssRules || []).filter(rule => 
                    rule.type === CSSRule.MEDIA_RULE
                ).length;
            } catch (e) {
                return count;
            }
        }, 0),
        flexboxElements: document.querySelectorAll('[class*="flex"], [style*="flex"]').length,
        gridElements: document.querySelectorAll('[class*="grid"], [style*="grid"]').length,
        responsiveClasses: document.querySelectorAll('[class*="sm:"], [class*="md:"], [class*="lg:"], [class*="xl:"]').length
    };
    
    addTest('Media Queries', responsiveElements.mediaQueries > 0 ? 'PASS' : 'WARN', 
        `${responsiveElements.mediaQueries} media queries found`);
    addTest('Flexbox Usage', responsiveElements.flexboxElements > 0 ? 'PASS' : 'INFO', 
        `${responsiveElements.flexboxElements} flex elements`);
    addTest('Grid Usage', responsiveElements.gridElements > 0 ? 'PASS' : 'INFO', 
        `${responsiveElements.gridElements} grid elements`);
    addTest('Responsive Classes', responsiveElements.responsiveClasses > 0 ? 'PASS' : 'INFO', 
        `${responsiveElements.responsiveClasses} responsive classes`);
    
    // Test 6: Accessibility
    console.log('\n🧪 Test 6: Accessibility Check');
    console.log('=' .repeat(50));
    
    const accessibility = {
        altTexts: document.querySelectorAll('img[alt]').length,
        totalImages: document.querySelectorAll('img').length,
        labeledInputs: document.querySelectorAll('input[aria-label], input[id]').length,
        totalInputs: document.querySelectorAll('input').length,
        headings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
        ariaLabels: document.querySelectorAll('[aria-label]').length,
        roles: document.querySelectorAll('[role]').length,
        langAttribute: !!document.documentElement.lang
    };
    
    const altTextCoverage = accessibility.totalImages > 0 ? 
        Math.round((accessibility.altTexts / accessibility.totalImages) * 100) : 100;
    const inputLabelCoverage = accessibility.totalInputs > 0 ? 
        Math.round((accessibility.labeledInputs / accessibility.totalInputs) * 100) : 100;
    
    addTest('Image Alt Text Coverage', altTextCoverage >= 80 ? 'PASS' : 'WARN', 
        `${altTextCoverage}% (${accessibility.altTexts}/${accessibility.totalImages})`);
    addTest('Input Label Coverage', inputLabelCoverage >= 80 ? 'PASS' : 'WARN', 
        `${inputLabelCoverage}% (${accessibility.labeledInputs}/${accessibility.totalInputs})`);
    addTest('Heading Structure', accessibility.headings > 0 ? 'PASS' : 'WARN', 
        `${accessibility.headings} heading elements`);
    addTest('ARIA Labels', accessibility.ariaLabels > 0 ? 'PASS' : 'INFO', 
        `${accessibility.ariaLabels} elements with aria-label`);
    addTest('ARIA Roles', accessibility.roles > 0 ? 'PASS' : 'INFO', 
        `${accessibility.roles} elements with roles`);
    addTest('Language Attribute', accessibility.langAttribute ? 'PASS' : 'WARN', 
        `Lang attribute: ${document.documentElement.lang || 'not set'}`);
    
    // Test 7: Performance Indicators
    console.log('\n🧪 Test 7: Performance Indicators');
    console.log('=' .repeat(50));
    
    const performance = {
        scriptsCount: document.querySelectorAll('script').length,
        stylesheetsCount: document.querySelectorAll('link[rel="stylesheet"]').length,
        imagesCount: document.querySelectorAll('img').length,
        totalRequests: performance.getEntriesByType ? performance.getEntriesByType('resource').length : 'N/A',
        domReadyTime: performance.timing ? 
            performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart : 'N/A'
    };
    
    addTest('Script Files', performance.scriptsCount < 10 ? 'PASS' : 'WARN', 
        `${performance.scriptsCount} script tags`);
    addTest('Stylesheets', performance.stylesheetsCount < 5 ? 'PASS' : 'WARN', 
        `${performance.stylesheetsCount} stylesheets`);
    addTest('Images', 'INFO', `${performance.imagesCount} images`);
    addTest('Total Network Requests', 'INFO', `${performance.totalRequests} requests`);
    addTest('DOM Ready Time', performance.domReadyTime !== 'N/A' && performance.domReadyTime < 2000 ? 'PASS' : 'INFO', 
        `${performance.domReadyTime}ms`);
    
    // Test 8: Error Detection
    console.log('\n🧪 Test 8: Error Detection');
    console.log('=' .repeat(50));
    
    const errorCheck = {
        brokenImages: Array.from(document.querySelectorAll('img')).filter(img => 
            !img.complete || img.naturalHeight === 0
        ).length,
        brokenLinks: Array.from(document.querySelectorAll('a[href]')).filter(link => {
            const href = link.getAttribute('href');
            return href === '#' || href === '' || href === 'javascript:void(0)';
        }).length,
        missingTexts: Array.from(document.querySelectorAll('*')).filter(el => 
            el.textContent?.trim() === '' && 
            el.children.length === 0 && 
            !['img', 'input', 'br', 'hr'].includes(el.tagName.toLowerCase())
        ).length
    };
    
    addTest('Broken Images', errorCheck.brokenImages === 0 ? 'PASS' : 'WARN', 
        `${errorCheck.brokenImages} potentially broken images`);
    addTest('Placeholder Links', errorCheck.brokenLinks === 0 ? 'PASS' : 'INFO', 
        `${errorCheck.brokenLinks} placeholder links`);
    addTest('Empty Elements', errorCheck.missingTexts < 5 ? 'PASS' : 'INFO', 
        `${errorCheck.missingTexts} potentially empty elements`);
    
    // Generate Summary
    const passedTests = results.tests.filter(test => test.status === 'PASS').length;
    const failedTests = results.tests.filter(test => test.status === 'FAIL').length;
    const warningTests = results.tests.filter(test => test.status === 'WARN').length;
    const totalTests = results.tests.length;
    
    results.summary = {
        totalTests,
        passed: passedTests,
        failed: failedTests,
        warnings: warningTests,
        successRate: Math.round((passedTests / totalTests) * 100),
        erpFeaturesDetected: foundKeywords.length,
        overallStatus: failedTests === 0 ? (warningTests < 3 ? 'EXCELLENT' : 'GOOD') : 'NEEDS_ATTENTION'
    };
    
    // Generate Recommendations
    if (failedTests > 0) {
        results.recommendations.push('Address failed tests to improve application quality');
    }
    if (warningTests > 5) {
        results.recommendations.push('Review warning items for potential improvements');
    }
    if (foundKeywords.length < 5) {
        results.recommendations.push('Consider adding more ERP-specific content and features');
    }
    if (accessibility.altTexts / accessibility.totalImages < 0.8) {
        results.recommendations.push('Improve image accessibility by adding alt text');
    }
    if (responsiveElements.responsiveClasses === 0) {
        results.recommendations.push('Consider implementing responsive design classes');
    }
    
    // Final Report
    console.log('\n📊 FINAL TEST REPORT');
    console.log('=' .repeat(50));
    console.log(`🎯 Overall Status: ${results.summary.overallStatus}`);
    console.log(`✅ Tests Passed: ${passedTests}/${totalTests} (${results.summary.successRate}%)`);
    console.log(`❌ Tests Failed: ${failedTests}`);
    console.log(`⚠️  Warnings: ${warningTests}`);
    console.log(`🏢 ERP Features Detected: ${foundKeywords.length} keywords`);
    
    if (results.recommendations.length > 0) {
        console.log('\n💡 Recommendations:');
        results.recommendations.forEach((rec, index) => {
            console.log(`   ${index + 1}. ${rec}`);
        });
    }
    
    console.log('\n🎉 Analysis completed!');
    console.log('Full results available in the returned object.');
    
    return results;
    
})();