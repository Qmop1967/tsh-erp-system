#!/bin/bash

echo "🚀 TSH Salesperson App - Xcode Config Fixer"
echo "============================================"

# Navigate to the project's ios/Flutter directory
cd "$(dirname "$0")/ios/Flutter"

# --- Define File Paths ---
DEBUG_CONFIG="Debug.xcconfig"
RELEASE_CONFIG="Release.xcconfig"

# --- Define Required Include Lines ---
DEBUG_INCLUDE='#include "Pods/Target Support Files/Pods-Runner/Pods-Runner.debug.xcconfig"'
RELEASE_INCLUDE='#include "Pods/Target Support Files/Pods-Runner/Pods-Runner.release.xcconfig"'
GENERATED_INCLUDE='#include "Generated.xcconfig"'

# --- Function to Add Include if Missing ---
add_include_if_missing() {
    local file=$1
    local include_line=$2
    
    if [ ! -f "$file" ]; then
        echo "⚠️  Warning: $file does not exist. Creating it."
        touch "$file"
    fi

    if grep -qF -- "$include_line" "$file"; then
        echo "✅ Include already exists in $file."
    else
        echo "🔧 Adding required include to $file..."
        # Add the include at the beginning of the file for clarity
        echo -e "$include_line\n$(cat "$file")" > "$file"
        echo "👍 Successfully added include."
    fi
}

echo ""
echo "Checking and fixing Generated.xcconfig includes..."
add_include_if_missing "$DEBUG_CONFIG" "$GENERATED_INCLUDE"
add_include_if_missing "$RELEASE_CONFIG" "$GENERATED_INCLUDE"

echo ""
echo "Checking and fixing Pods xcconfig includes..."
add_include_if_missing "$DEBUG_CONFIG" "$DEBUG_INCLUDE"
add_include_if_missing "$RELEASE_CONFIG" "$RELEASE_INCLUDE"

echo ""
echo "🎉 Xcode configuration check complete."
echo "The necessary includes should now be present."
echo "Returning to the project root..."

cd ../..
