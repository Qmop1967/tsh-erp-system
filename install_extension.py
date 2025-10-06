#!/usr/bin/env python3
"""
BrowserTools Chrome Extension Installation Helper
This script provides step-by-step guidance for installing the Chrome extension
"""

import os
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("🚀 BrowserTools Chrome Extension Installation Helper")
    print("=" * 50)
    
    # Check if extension files exist
    extension_path = Path("/Users/khaleelal-mulla/Downloads/chrome-extension")
    if not extension_path.exists():
        print("❌ Extension files not found!")
        print("Please ensure the extension has been downloaded and extracted.")
        return
    
    print("✅ Extension files found at:", extension_path)
    
    # List extension files
    print("\n📁 Extension files:")
    for file in extension_path.glob("*"):
        print(f"   - {file.name}")
    
    print("\n" + "=" * 50)
    print("📋 INSTALLATION INSTRUCTIONS")
    print("=" * 50)
    
    print("\nStep 1: Open Chrome Extension Management")
    print("   • Open Chrome browser")
    print("   • Type: chrome://extensions/ in address bar")
    print("   • Press Enter")
    
    print("\nStep 2: Enable Developer Mode")
    print("   • Look for 'Developer mode' toggle in top-right")
    print("   • Click to enable it")
    
    print("\nStep 3: Load the Extension")
    print("   • Click 'Load unpacked' button")
    print(f"   • Navigate to: {extension_path}")
    print("   • Select the folder and click 'Select'")
    
    print("\nStep 4: Verify Installation")
    print("   • You should see 'BrowserToolsMCP' in extensions list")
    print("   • Make sure it's enabled (toggle switch on)")
    
    print("\nStep 5: Connect to Your Project")
    print("   • Open your TSH ERP System: http://localhost:5173")
    print("   • Open DevTools (F12 or right-click → Inspect)")
    print("   • Click 'BrowserToolsMCP' tab")
    print("   • Extension should connect automatically")
    
    print("\n" + "=" * 50)
    print("🔧 AUTOMATED ACTIONS")
    print("=" * 50)
    
    # Try to open Chrome with the extensions page
    try:
        print("\n🌐 Opening Chrome Extension Management page...")
        # This will open Chrome to the extensions page
        subprocess.run([
            "open", "-a", "Google Chrome", "chrome://extensions/"
        ], check=False)
        print("✅ Chrome Extension Management page opened")
    except Exception as e:
        print(f"⚠️  Could not auto-open Chrome: {e}")
        print("Please manually open chrome://extensions/")
    
    print("\n" + "=" * 50)
    print("📝 QUICK COPY-PASTE COMMANDS")
    print("=" * 50)
    
    print(f"\nExtension path (copy this):")
    print(f"{extension_path}")
    
    print("\nChrome extensions URL:")
    print("chrome://extensions/")
    
    print("\n" + "=" * 50)
    print("✨ Once installed, you can:")
    print("   • Take screenshots of your UI")
    print("   • Monitor console logs")
    print("   • Track network activity")
    print("   • Run accessibility audits")
    print("   • Perform SEO analysis")
    print("   • Check performance metrics")
    print("=" * 50)

if __name__ == "__main__":
    main()
