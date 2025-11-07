// Minimal test without any imports
console.log('main.tsx loaded');

const root = document.getElementById('root');
if (root) {
    console.log('Root element found');
    root.innerHTML = `
        <div style="padding: 20px; background-color: #f8f9fa; min-height: 100vh; font-family: Arial, sans-serif;">
            <h1 style="color: #333; font-size: 2rem; margin-bottom: 1rem;">
                🔍 TSH ERP System - Pure JS Test
            </h1>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #22c55e; margin: 0 0 10px 0;">✅ Pure JavaScript Working!</h2>
                <p style="color: #666; margin: 0;">
                    This confirms the HTML/JS/Vite pipeline is working. 
                    The issue is likely with React or TypeScript compilation.
                </p>
                <p style="color: #666; margin: 10px 0 0 0; font-size: 0.9rem;">
                    Current time: ${new Date().toLocaleTimeString()}
                </p>
            </div>
        </div>
    `;
} else {
    console.error('Root element not found!');
}
