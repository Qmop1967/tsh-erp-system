#!/bin/bash

echo "🔐 TSH Admin App - Certificate Installation Helper"
echo "================================================="

CERTIFICATES_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard/ios/certificates"
PROFILES_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard/ios/profiles"

# Function to install development certificate
install_certificate() {
    echo ""
    echo "🔐 Installing Development Certificate"
    echo "===================================="
    
    # Look for .p12 files in certificates directory
    P12_FILES=$(find "$CERTIFICATES_DIR" -name "*.p12" 2>/dev/null)
    
    if [ -n "$P12_FILES" ]; then
        echo "✅ Found certificate files:"
        echo "$P12_FILES" | while read -r file; do
            echo "   • $(basename "$file")"
        done
        echo ""
        
        # Install each .p12 file
        echo "$P12_FILES" | while read -r p12_file; do
            if [ -f "$p12_file" ]; then
                echo "🔑 Installing: $(basename "$p12_file")"
                echo "Please enter the password for this certificate when prompted:"
                
                # Import into keychain
                security import "$p12_file" -k ~/Library/Keychains/login.keychain-db -T /usr/bin/codesign
                
                if [ $? -eq 0 ]; then
                    echo "✅ Certificate installed successfully"
                else
                    echo "❌ Failed to install certificate"
                fi
            fi
        done
    else
        echo "⚠️  No .p12 certificate files found in:"
        echo "   $CERTIFICATES_DIR"
        echo ""
        echo "📋 Please:"
        echo "1. Download your iOS Development Certificate from Apple Developer Portal"
        echo "2. Save the .p12 file to: $CERTIFICATES_DIR"
        echo "3. Run this script again"
    fi
}

# Function to install provisioning profile
install_provisioning_profile() {
    echo ""
    echo "📋 Installing Provisioning Profile"
    echo "================================="
    
    # Look for .mobileprovision files
    PROFILE_FILES=$(find "$PROFILES_DIR" -name "*.mobileprovision" 2>/dev/null)
    
    if [ -n "$PROFILE_FILES" ]; then
        echo "✅ Found provisioning profile files:"
        echo "$PROFILE_FILES" | while read -r file; do
            echo "   • $(basename "$file")"
        done
        echo ""
        
        # Install each profile
        echo "$PROFILE_FILES" | while read -r profile_file; do
            if [ -f "$profile_file" ]; then
                echo "📱 Installing: $(basename "$profile_file")"
                
                # Copy to provisioning profiles directory
                PROFILES_LIBRARY="$HOME/Library/MobileDevice/Provisioning Profiles"
                mkdir -p "$PROFILES_LIBRARY"
                
                cp "$profile_file" "$PROFILES_LIBRARY/"
                
                if [ $? -eq 0 ]; then
                    echo "✅ Provisioning profile installed successfully"
                    
                    # Show profile info
                    echo "📋 Profile information:"
                    security cms -D -i "$profile_file" 2>/dev/null | grep -A 1 -E "Name|UUID|TeamName" | head -6
                else
                    echo "❌ Failed to install provisioning profile"
                fi
            fi
        done
    else
        echo "⚠️  No .mobileprovision files found in:"
        echo "   $PROFILES_DIR"
        echo ""
        echo "📋 Please:"
        echo "1. Download your iOS Provisioning Profile from Apple Developer Portal"
        echo "2. Save the .mobileprovision file to: $PROFILES_DIR"
        echo "3. Run this script again"
    fi
}

# Function to verify keychain certificates
verify_certificates() {
    echo ""
    echo "🔍 Verifying Installed Certificates"
    echo "==================================="
    
    echo "📋 iOS Development Certificates in Keychain:"
    security find-identity -v -p codesigning | grep "iPhone Developer\|Apple Development" || echo "   No iOS development certificates found"
    
    echo ""
    echo "📋 Distribution Certificates in Keychain:"
    security find-identity -v -p codesigning | grep "iPhone Distribution\|Apple Distribution" || echo "   No iOS distribution certificates found"
}

# Function to verify provisioning profiles
verify_profiles() {
    echo ""
    echo "🔍 Verifying Installed Provisioning Profiles"
    echo "============================================"
    
    PROFILES_LIBRARY="$HOME/Library/MobileDevice/Provisioning Profiles"
    
    if [ -d "$PROFILES_LIBRARY" ]; then
        PROFILE_COUNT=$(find "$PROFILES_LIBRARY" -name "*.mobileprovision" | wc -l)
        echo "📱 Found $PROFILE_COUNT provisioning profile(s) installed"
        
        if [ $PROFILE_COUNT -gt 0 ]; then
            echo ""
            echo "📋 Profile details:"
            find "$PROFILES_LIBRARY" -name "*.mobileprovision" | while read -r profile; do
                echo "   Profile: $(basename "$profile")"
                security cms -D -i "$profile" 2>/dev/null | grep -E "Name|UUID|TeamName" | head -3 | sed 's/^/     /'
                echo ""
            done
        fi
    else
        echo "❌ Provisioning Profiles directory not found"
    fi
}

# Function to update Xcode project settings
update_xcode_project() {
    echo ""
    echo "🔧 Updating Xcode Project Settings"
    echo "================================="
    
    PROJECT_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
    PBXPROJ_FILE="$PROJECT_PATH/ios/Runner.xcodeproj/project.pbxproj"
    
    if [ -f "$PBXPROJ_FILE" ]; then
        echo "✅ Found Xcode project file"
        echo ""
        echo "📋 Current configuration:"
        grep -E "DEVELOPMENT_TEAM|PRODUCT_BUNDLE_IDENTIFIER" "$PBXPROJ_FILE" | head -5
        echo ""
        echo "⚠️  To update Team ID or Bundle ID:"
        echo "1. Open Xcode: open $PROJECT_PATH/ios/Runner.xcworkspace"
        echo "2. Select Runner target"
        echo "3. Go to Signing & Capabilities tab"
        echo "4. Update Team and Bundle Identifier as needed"
        echo "5. Enable 'Automatically manage signing'"
    else
        echo "❌ Xcode project file not found!"
    fi
}

# Function to clean and reset certificates
clean_certificates() {
    echo ""
    echo "🧹 Certificate Cleanup Options"
    echo "============================="
    echo ""
    echo "⚠️  This will remove certificates and profiles. Continue?"
    read -p "Type 'yes' to continue: " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo ""
        echo "🗑️  Removing old provisioning profiles..."
        rm -rf "$HOME/Library/MobileDevice/Provisioning Profiles"/*.mobileprovision
        
        echo "✅ Cleanup completed"
        echo "📋 You'll need to reinstall certificates and profiles"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Main menu
echo ""
echo "🎯 What would you like to do?"
echo ""
echo "1) Install development certificate (.p12)"
echo "2) Install provisioning profile (.mobileprovision)"
echo "3) Install both certificate and profile"
echo "4) Verify installed certificates"
echo "5) Verify installed provisioning profiles"
echo "6) Update Xcode project settings"
echo "7) Clean old certificates and profiles"
echo "8) Full verification (certificates + profiles)"
echo ""
read -p "Choose option (1-8): " choice

case $choice in
    1)
        install_certificate
        ;;
    2)
        install_provisioning_profile
        ;;
    3)
        install_certificate
        install_provisioning_profile
        ;;
    4)
        verify_certificates
        ;;
    5)
        verify_profiles
        ;;
    6)
        update_xcode_project
        ;;
    7)
        clean_certificates
        ;;
    8)
        verify_certificates
        verify_profiles
        update_xcode_project
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "✅ Certificate management completed!"
echo ""
echo "📋 Next steps:"
echo "1. Verify certificates are properly installed"
echo "2. Open Xcode and check signing configuration"
echo "3. Run the deployment script: ./deploy_to_iphone.sh"
