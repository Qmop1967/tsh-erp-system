// Chrome DevTools Test Script for Notification Button
// Run this in the browser console to test notification functionality

console.log('🔔 Chrome DevTools Notification Button Test');
console.log('==========================================');

// Test 1: Check if NotificationProvider is available
console.log('📋 Test 1: Checking NotificationProvider...');
try {
    const notificationContext = document.querySelector('[data-testid="notification-provider"]');
    if (notificationContext || window.__NOTIFICATION_CONTEXT__) {
        console.log('✅ NotificationProvider is available');
    } else {
        console.log('⚠️  NotificationProvider context not directly visible, checking React components...');
    }
} catch (error) {
    console.log('❌ Error checking NotificationProvider:', error.message);
}

// Test 2: Check if notification button exists
console.log('\n📋 Test 2: Checking notification button...');
const notificationButton = document.querySelector('button[aria-label*="notification" i]') || 
                          document.querySelector('button svg[data-lucide="bell"]') ||
                          document.querySelector('button:has(svg[data-lucide="bell"])');

if (notificationButton) {
    console.log('✅ Notification button found:', notificationButton);
    console.log('   - Button classes:', notificationButton.className);
    console.log('   - Button is visible:', !notificationButton.hidden && notificationButton.offsetParent !== null);
    
    // Check for badge
    const badge = notificationButton.querySelector('span[class*="absolute"]');
    if (badge) {
        console.log('✅ Notification badge found:', badge.textContent);
        console.log('   - Badge classes:', badge.className);
    } else {
        console.log('⚠️  No notification badge found');
    }
} else {
    console.log('❌ Notification button not found');
}

// Test 3: Check notification dropdown
console.log('\n📋 Test 3: Checking notification dropdown...');
const notificationDropdown = document.querySelector('.notification-dropdown') ||
                            document.querySelector('[class*="notification"]');

if (notificationDropdown) {
    console.log('✅ Notification dropdown container found');
    
    // Try to open dropdown
    console.log('   - Attempting to open dropdown...');
    notificationButton?.click();
    
    setTimeout(() => {
        const dropdownContent = document.querySelector('[class*="absolute"][class*="right-0"]') ||
                               document.querySelector('[role="dialog"]') ||
                               document.querySelector('[class*="dropdown"]');
        
        if (dropdownContent && dropdownContent.style.display !== 'none') {
            console.log('✅ Notification dropdown opened successfully');
            console.log('   - Dropdown visible:', dropdownContent.offsetParent !== null);
            
            // Check for notification items
            const notificationItems = dropdownContent.querySelectorAll('[class*="notification"], [class*="px-4 py-3"]');
            console.log(`✅ Found ${notificationItems.length} notification items`);
            
            notificationItems.forEach((item, index) => {
                const title = item.querySelector('p[class*="font"]');
                const message = item.querySelector('p[class*="text-xs"]');
                console.log(`   Item ${index + 1}:`, {
                    title: title?.textContent || 'No title',
                    message: message?.textContent || 'No message',
                    read: !item.classList.contains('bg-blue-50')
                });
            });
            
            // Check for "Mark all as read" button
            const markAllReadBtn = dropdownContent.querySelector('button:contains("Mark all as read")') ||
                                 Array.from(dropdownContent.querySelectorAll('button')).find(btn => 
                                     btn.textContent.includes('Mark all'));
            
            if (markAllReadBtn) {
                console.log('✅ "Mark all as read" button found');
            }
            
        } else {
            console.log('❌ Notification dropdown not visible after clicking');
        }
    }, 100);
} else {
    console.log('❌ Notification dropdown container not found');
}

// Test 4: Check for test notification button (admin only)
console.log('\n📋 Test 4: Checking test notification button...');
const testButton = document.querySelector('button[title*="test" i]') ||
                   document.querySelector('button:has(svg[data-lucide="check"])');

if (testButton) {
    console.log('✅ Test notification button found (admin only)');
    console.log('   - Button title:', testButton.title);
} else {
    console.log('⚠️  Test notification button not found (may require admin permissions)');
}

// Test 5: Test notification functionality
console.log('\n📋 Test 5: Testing notification functionality...');
setTimeout(() => {
    if (testButton) {
        console.log('   - Clicking test notification button...');
        testButton.click();
        
        setTimeout(() => {
            // Check for toast notifications
            const toastNotifications = document.querySelectorAll('[class*="fixed"][class*="top-4"][class*="right-4"]');
            console.log(`✅ Found ${toastNotifications.length} toast notifications`);
            
            toastNotifications.forEach((toast, index) => {
                console.log(`   Toast ${index + 1}:`, {
                    visible: toast.offsetParent !== null,
                    title: toast.querySelector('p[class*="font"]')?.textContent,
                    message: toast.querySelector('p[class*="text-sm"]')?.textContent
                });
            });
            
            // Check updated badge count
            const updatedBadge = notificationButton?.querySelector('span[class*="absolute"]');
            if (updatedBadge) {
                console.log('✅ Updated badge count:', updatedBadge.textContent);
            }
        }, 500);
    }
}, 200);

// Test 6: Check React DevTools
console.log('\n📋 Test 6: React Component Check...');
if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__ && window.__REACT_DEVTOOLS_GLOBAL_HOOK__.rendererInterfaces) {
    console.log('✅ React DevTools available');
    console.log('   - You can inspect the Header component in React DevTools');
    console.log('   - Look for notification state and handlers');
} else {
    console.log('⚠️  React DevTools not available');
}

console.log('\n🎯 Manual Testing Steps:');
console.log('1. Click the bell icon to open notifications');
console.log('2. Click individual notifications to mark as read');
console.log('3. Click "Mark all as read" if available');
console.log('4. Click outside dropdown to close it');
console.log('5. If admin, click the checkmark icon to add test notifications');
console.log('6. Observe toast notifications appearing');

console.log('\n🔍 Check Network Tab for:');
console.log('- No errors in console');
console.log('- CSS and JS files loaded successfully');
console.log('- Component mounting/unmounting events');

console.log('\n✨ Test completed! Review the results above.');
