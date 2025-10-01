#!/bin/bash

# Test Runner for User Management All Users Button Tests
# This script runs comprehensive tests for the User Management dropdown functionality

echo "🚀 Starting User Management All Users Button Tests"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if required services are running
check_services() {
    print_status $BLUE "🔍 Checking required services..."
    
    # Check if frontend is running (port 5173)
    if curl -s http://localhost:5173 > /dev/null; then
        print_status $GREEN "✅ Frontend server is running on port 5173"
    else
        print_status $YELLOW "⚠️  Frontend server not detected on port 5173"
        print_status $YELLOW "   Starting frontend server..."
        cd ../frontend && npm run dev &
        FRONTEND_PID=$!
        sleep 10
    fi
    
    # Check if backend is running (port 8000)
    if curl -s http://localhost:8000/docs > /dev/null; then
        print_status $GREEN "✅ Backend server is running on port 8000"
    else
        print_status $YELLOW "⚠️  Backend server not detected on port 8000"
        print_status $YELLOW "   Please start the backend server manually:"
        print_status $YELLOW "   cd ../app && uvicorn main:app --reload --port 8000"
    fi
}

# Run the tests
run_tests() {
    print_status $BLUE "🧪 Running User Management Dropdown Tests..."
    
    # Run the focused dropdown flow test
    print_status $YELLOW "📋 Test 1: User Management Dropdown Flow"
    npx playwright test user-management-dropdown-flow.spec.ts --reporter=line
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Dropdown flow tests passed!"
    else
        print_status $RED "❌ Dropdown flow tests failed!"
    fi
    
    echo ""
    
    # Run the comprehensive tests
    print_status $YELLOW "📋 Test 2: Comprehensive All Users Button Tests"
    npx playwright test all-users-button-comprehensive.spec.ts --reporter=line
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Comprehensive tests passed!"
    else
        print_status $RED "❌ Comprehensive tests failed!"
    fi
}

# Generate test report
generate_report() {
    print_status $BLUE "📊 Generating test report..."
    
    # Run tests with HTML reporter
    npx playwright test user-management-dropdown-flow.spec.ts all-users-button-comprehensive.spec.ts --reporter=html
    
    if [ -d "playwright-report" ]; then
        print_status $GREEN "✅ Test report generated in playwright-report/"
        print_status $BLUE "🌐 Open playwright-report/index.html to view detailed results"
    fi
}

# Main execution
main() {
    echo "Starting test execution at $(date)"
    echo ""
    
    # Change to test directory
    cd "$(dirname "$0")"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status $YELLOW "📦 Installing test dependencies..."
        npm install
    fi
    
    # Check services
    check_services
    echo ""
    
    # Run tests
    run_tests
    echo ""
    
    # Generate report
    generate_report
    echo ""
    
    print_status $BLUE "🏁 Test execution completed at $(date)"
    print_status $BLUE "=================================================="
}

# Run main function
main "$@"
