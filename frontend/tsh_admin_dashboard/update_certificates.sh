#!/bin/bash

echo "🍎 TSH Admin App - iOS Certificate & Profile Update Script"
echo "=========================================================="

# Set project paths
ADMIN_APP_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
CERTIFICATES_DIR="$ADMIN_APP_PATH/ios/certificates"
PROFILES_DIR="$ADMIN_APP_PATH/ios/profiles"

# Create directories for certificates and profiles
mkdir -p "$CERTIFICATES_DIR"
mkdir -p "$PROFILES_DIR"

echo ""
echo "📁 Created certificate directories:"
echo "   • Certificates: $CERTIFICATES_DIR"
echo "   • Profiles: $PROFILES_DIR"
echo ""

# Function to update certificate and profile information
update_certificates() {
    echo "🔐 Certificate Update Process"
    echo "=============================="
    echo ""
    echo "Please place your new certificate and profile files in the following locations:"
    echo ""
    echo "📱 iOS Development Certificate (.p12 file):"
    echo "   → $CERTIFICATES_DIR/ios_development.p12"
    echo ""
    echo "📋 Provisioning Profile (.mobileprovision file):"
    echo "   → $PROFILES_DIR/TSH_Admin_Development.mobileprovision"
    echo ""
    echo "🆔 If you have a new Team ID, please update it in the script below"
    echo ""
}

# Function to update Xcode project with new certificates
update_xcode_project() {
    echo "🔧 Updating Xcode Project Configuration"
    echo "======================================="
    
    # Update project.pbxproj with new team ID and certificate settings
    PBXPROJ_PATH="$ADMIN_APP_PATH/ios/Runner.xcodeproj/project.pbxproj"
    
    if [ -f "$PBXPROJ_PATH" ]; then
        echo "✅ Found Xcode project file"
        echo "   → Updating development team configuration..."
        
        # Backup original file
        cp "$PBXPROJ_PATH" "$PBXPROJ_PATH.backup"
        
        # Note: You'll need to replace YOUR_NEW_TEAM_ID with your actual team ID
        echo "⚠️  Please manually update your Team ID in Xcode after running this script"
    else
        echo "❌ Xcode project file not found!"
    fi
}

# Function to setup wireless debugging
setup_wireless_debugging() {
    echo "📲 Setting up Wireless Debugging for iPhone 15 Pro Max"
    echo "======================================================"
    echo ""
    echo "To enable wireless deployment to your iPhone:"
    echo ""
    echo "1️⃣  Connect iPhone via USB cable first"
    echo "2️⃣  Open Xcode → Window → Devices and Simulators"
    echo "3️⃣  Select your iPhone 15 Pro Max"
    echo "4️⃣  Check ✅ 'Connect via network'"
    echo "5️⃣  Wait for network icon to appear next to device"
    echo "6️⃣  Disconnect USB cable - wireless connection active!"
    echo ""
}

# Function to get Mac IP address for network configuration
get_mac_ip() {
    # Get the Mac's local IP address
    MAC_IP=$(ifconfig | grep -E "inet.*broadcast" | grep -v "127.0.0.1" | awk '{print $2}' | head -1)
    echo "$MAC_IP"
}

# Function to update network configuration
update_network_config() {
    echo "🌐 Updating Network Configuration"
    echo "================================="
    echo ""
    
    MAC_IP=$(get_mac_ip)
    
    if [ -n "$MAC_IP" ]; then
        echo "📡 Found Mac IP address: $MAC_IP"
        echo ""
        
        # Create environment configuration file
        ENV_CONFIG_PATH="$ADMIN_APP_PATH/lib/config/environment.dart"
        mkdir -p "$ADMIN_APP_PATH/lib/config"
        
        cat > "$ENV_CONFIG_PATH" << EOF
class Environment {
  static const String apiBaseUrl = 'http://$MAC_IP:8000';
  
  static const Map<String, String> endpoints = {
    'dashboard': '/api/admin/dashboard',
    'users': '/api/admin/users',
    'analytics': '/api/admin/analytics',
    'settings': '/api/admin/settings',
  };
  
  static String getFullUrl(String endpoint) {
    return '\$apiBaseUrl\${endpoints[endpoint] ?? endpoint}';
  }
}
EOF
        
        echo "✅ Created environment configuration with IP: $MAC_IP"
        echo "📁 Config file: $ENV_CONFIG_PATH"
        
        # Update main.dart to use the new configuration
        update_main_dart_networking
        
    else
        echo "❌ Could not detect Mac IP address"
        echo "💡 Please manually check your IP with: ifconfig | grep inet"
    fi
    echo ""
}

# Function to update main.dart for proper networking
update_main_dart_networking() {
    echo "🔧 Updating main.dart for network access..."
    
    MAIN_DART_PATH="$ADMIN_APP_PATH/lib/main.dart"
    
    if [ -f "$MAIN_DART_PATH" ]; then
        # Backup original file
        cp "$MAIN_DART_PATH" "$MAIN_DART_PATH.backup"
        
        # Replace localhost with environment configuration
        sed -i '' "s|http://localhost:8000|Environment.apiBaseUrl|g" "$MAIN_DART_PATH"
        
        # Add environment import if not exists
        if ! grep -q "import.*environment.dart" "$MAIN_DART_PATH"; then
            sed -i '' "1i\\
import 'config/environment.dart';" "$MAIN_DART_PATH"
        fi
        
        echo "✅ Updated main.dart for network access"
    else
        echo "❌ main.dart not found!"
    fi
}

# Function to check flutter devices
check_flutter_devices() {
    echo "🔍 Checking Connected Devices"
    echo "============================="
    echo ""
    cd "$ADMIN_APP_PATH"
    flutter devices
    echo ""
}

# Function to fix app accessibility and network issues
fix_app_accessibility() {
    echo "🔧 Fixing App Accessibility Issues"
    echo "=================================="
    echo ""
    
    MAC_IP=$(get_mac_ip)
    
    echo "🔍 Diagnosing connectivity issues..."
    echo ""
    echo "📱 Current app status: Installed but not reachable"
    echo "💡 Common issues and fixes:"
    echo ""
    echo "1️⃣  NETWORK CONFIGURATION:"
    echo "   • App is configured for localhost (127.0.0.1)"
    echo "   • iPhone needs Mac's actual IP address: $MAC_IP"
    echo "   • Updating configuration..."
    echo ""
    
    update_network_config
    
    echo "2️⃣  FIREWALL & SECURITY:"
    echo "   • Checking if Mac firewall is blocking connections..."
    
    # Check if backend is running
    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "   ✅ Backend server is running on localhost:8000"
    else
        echo "   ⚠️  Backend server may not be running"
        echo "   📋 To start backend: cd to project root and run: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    fi
    echo ""
    
    echo "3️⃣  iOS PERMISSIONS:"
    echo "   • Checking App Transport Security (ATS) settings..."
    
    # Update Info.plist for HTTP access
    update_info_plist_networking
    
    echo ""
    echo "4️⃣  CERTIFICATE & TRUST:"
    echo "   • Ensure app is trusted in iPhone Settings"
    echo "   • Go to: Settings → General → VPN & Device Management"
    echo "   • Trust the developer certificate"
    echo ""
}

# Function to update Info.plist for network access
update_info_plist_networking() {
    INFO_PLIST_PATH="$ADMIN_APP_PATH/ios/Runner/Info.plist"
    
    if [ -f "$INFO_PLIST_PATH" ]; then
        echo "   🔧 Updating Info.plist for HTTP access..."
        
        # Backup original file
        cp "$INFO_PLIST_PATH" "$INFO_PLIST_PATH.backup"
        
        # Check if NSAppTransportSecurity already exists
        if ! grep -q "NSAppTransportSecurity" "$INFO_PLIST_PATH"; then
            # Add ATS exception before closing dict
            sed -i '' 's|</dict>|	<key>NSAppTransportSecurity</key>\
	<dict>\
		<key>NSAllowsArbitraryLoads</key>\
		<true/>\
		<key>NSExceptionDomains</key>\
		<dict>\
			<key>localhost</key>\
			<dict>\
				<key>NSExceptionAllowsInsecureHTTPLoads</key>\
				<true/>\
			</dict>\
		</dict>\
	</dict>\
</dict>|' "$INFO_PLIST_PATH"
            
            echo "   ✅ Added App Transport Security exceptions"
        else
            echo "   ✅ App Transport Security already configured"
        fi
    else
        echo "   ❌ Info.plist not found!"
    fi
}

# Function to start backend server with proper network binding
start_backend_server() {
    echo "🚀 Starting Backend Server for Network Access"
    echo "============================================="
    echo ""
    
    BACKEND_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System"
    
    echo "📡 Starting FastAPI server accessible from iPhone..."
    echo "   • Binding to 0.0.0.0:8000 (accessible from network)"
    echo "   • Mac IP: $(get_mac_ip)"
    echo ""
    
    cd "$BACKEND_PATH"
    
    # Check if virtual environment exists
    if [ -d "venv" ] || [ -d ".venv" ]; then
        echo "🐍 Activating Python virtual environment..."
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            source .venv/bin/activate
        fi
    fi
    
    echo "🔄 Installing/updating requirements..."
    pip install -r config/requirements.txt
    
    echo ""
    echo "🚀 Starting server..."
    echo "   → Access from Mac: http://localhost:8000"
    echo "   → Access from iPhone: http://$(get_mac_ip):8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to deploy to iPhone
deploy_to_iphone() {
    echo "🚀 Deploying TSH Admin App to iPhone 15 Pro Max"
    echo "==============================================="
    echo ""
    cd "$ADMIN_APP_PATH"
    
    echo "🔨 Building Flutter app for iOS..."
    flutter clean
    flutter pub get
    
    # Check for connected iPhone
    IPHONE_DEVICE=$(flutter devices | grep -i "iphone\|ios" | grep -v "simulator" | head -1)
    
    if [ -n "$IPHONE_DEVICE" ]; then
        # Extract device ID
        DEVICE_ID=$(echo "$IPHONE_DEVICE" | grep -o '[A-Fa-f0-9\-]\{36\}' | head -1)
        
        if [ -n "$DEVICE_ID" ]; then
            echo "📱 Found iPhone: $IPHONE_DEVICE"
            echo "🔄 Launching app on device ID: $DEVICE_ID"
            
            # Launch the app
            flutter run -d "$DEVICE_ID" --flavor development
        else
            echo "❌ Could not extract device ID"
            echo "🔄 Trying alternative deployment method..."
            flutter run --device-id ios
        fi
    else
        echo "❌ No iPhone detected!"
        echo "📋 Available devices:"
        flutter devices
        echo ""
        echo "💡 Please ensure your iPhone 15 Pro Max is:"
        echo "   • Connected via USB or WiFi"
        echo "   • Unlocked and trusted this computer"
        echo "   • In Developer Mode (Settings → Privacy & Security → Developer Mode)"
    fi
}

# Main menu
echo "🎯 What would you like to do?"
echo ""
echo "1) Update certificates and profiles"
echo "2) Fix app accessibility (RECOMMENDED)"
echo "3) Update network configuration"
echo "4) Start backend server for iPhone access"
echo "5) Setup wireless debugging"
echo "6) Check connected devices"
echo "7) Deploy to iPhone"
echo "8) Full setup (all steps)"
echo ""
read -p "Choose option (1-8): " choice

case $choice in
    1)
        update_certificates
        update_xcode_project
        ;;
    2)
        fix_app_accessibility
        ;;
    3)
        update_network_config
        ;;
    4)
        start_backend_server
        ;;
    5)
        setup_wireless_debugging
        ;;
    6)
        check_flutter_devices
        ;;
    7)
        deploy_to_iphone
        ;;
    8)
        update_certificates
        update_xcode_project
        fix_app_accessibility
        setup_wireless_debugging
        check_flutter_devices
        deploy_to_iphone
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "✅ Script completed!"
echo ""
echo "📝 Next Steps:"
echo "   1. Place your new certificates in the certificates/ directory"
echo "   2. Open Xcode and update signing settings"
echo "   3. Set up wireless debugging if needed"
echo "   4. Run the app deployment option"
echo ""
