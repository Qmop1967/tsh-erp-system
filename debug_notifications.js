// Debug script to test notification functionality
// Run this in the browser console at http://localhost:5173/

console.log('🔔 Debugging Notification System');
console.log('==================================');

// Check if React is loaded
if (typeof window.React === 'undefined') {
    console.log('❌ React not loaded');
} else {
    console.log('✅ React loaded');
}

// Check if the app is mounted
setTimeout(() => {
    const header = document.querySelector('header');
    if (header) {
        console.log('✅ Header component found');
        
        // Find notification button
        const notificationButton = header.querySelector('button svg[data-lucide="bell"]');
        if (notificationButton) {
            console.log('✅ Notification button found');
            
            // Check if badge exists
            const buttonParent = notificationButton.parentElement;
            const badge = buttonParent.querySelector('span[class*="absolute"]');
            if (badge) {
                console.log('✅ Badge found with text:', badge.textContent);
            } else {
                console.log('❌ Badge not found');
            }
            
            // Test click functionality
            console.log('🧪 Testing button click...');
            buttonParent.click();
            
            setTimeout(() => {
                // Check if dropdown appeared
                const dropdown = document.querySelector('[class*="absolute"][class*="right-0"]');
                if (dropdown && dropdown.offsetParent !== null) {
                    console.log('✅ Dropdown opened successfully');
                    
                    // Count notifications
                    const notifications = dropdown.querySelectorAll('[class*="px-4 py-3"]');
                    console.log('✅ Found', notifications.length, 'notifications');
                    
                    // Test clicking first notification
                    if (notifications.length > 0) {
                        console.log('🧪 Testing notification click...');
                        notifications[0].click();
                        
                        setTimeout(() => {
                            // Check for toast notifications
                            const toasts = document.querySelectorAll('[class*="fixed"][class*="top-4"][class*="right-4"]');
                            console.log('✅ Found', toasts.length, 'toast notifications');
                            
                            if (toasts.length > 0) {
                                const toastText = toasts[0].textContent;
                                console.log('✅ Toast content:', toastText);
                            }
                        }, 500);
                    }
                    
                } else {
                    console.log('❌ Dropdown not visible');
                }
            }, 500);
            
        } else {
            console.log('❌ Notification button not found');
        }
        
        // Check for test button (admin only)
        const testButton = header.querySelector('button svg[data-lucide="check"]');
        if (testButton) {
            console.log('✅ Test button found (admin)');
            const testButtonParent = testButton.parentElement;
            
            // Test adding a notification
            console.log('🧪 Testing add notification...');
            testButtonParent.click();
            
            setTimeout(() => {
                const newBadge = buttonParent.querySelector('span[class*="absolute"]');
                if (newBadge) {
                    console.log('✅ Updated badge count:', newBadge.textContent);
                }
                
                const newToasts = document.querySelectorAll('[class*="fixed"][class*="top-4"][class*="right-4"]');
                console.log('✅ Found', newToasts.length, 'toast notifications after test');
            }, 1000);
        } else {
            console.log('⚠️ Test button not found (may need admin login)');
        }
        
    } else {
        console.log('❌ Header component not found');
    }
    
    // Check for console errors
    const consoleErrors = [];
    const originalError = console.error;
    console.error = (...args) => {
        consoleErrors.push(args.join(' '));
        originalError.apply(console, args);
    };
    
    setTimeout(() => {
        if (consoleErrors.length === 0) {
            console.log('✅ No console errors detected');
        } else {
            console.log('⚠️ Console errors found:');
            consoleErrors.forEach(error => console.log('   -', error));
        }
    }, 2000);
    
}, 1000);

// Check authentication state
setTimeout(() => {
    // Try to access auth store through window if available
    if (window.__AUTH_STORE__) {
        console.log('✅ Auth store accessible');
        console.log('   User:', window.__AUTH_STORE__.user);
    } else {
        console.log('⚠️ Auth store not directly accessible');
    }
}, 1500);

console.log('🎯 Debug script initiated. Wait for results...');
