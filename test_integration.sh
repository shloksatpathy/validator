#!/bin/bash

# Frontend-Backend Integration Test Script
# Tests all API endpoints to verify proper integration

BASE_URL="http://localhost:5000"

echo "🧪 Academic Validator - Integration Tests"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4

    echo -n "Testing $name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -X DELETE -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    fi

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $response)"
        ((FAILED++))
    fi
}

# Test 1: Health Check
test_endpoint "Health Check" "GET" "/health" "200"

# Test 2: Index Page
test_endpoint "Index Page (Upload)" "GET" "/" "200"

# Test 3: Submissions Page
test_endpoint "Submissions Page" "GET" "/submissions" "200"

# Test 4: List Submissions API
test_endpoint "List Submissions API" "GET" "/list" "200"

# Test 5: Get Status of a File
test_endpoint "Get File Status" "GET" "/status/3rd_Year_-_CSIT.pdf" "200"

# Test 6: Download File
test_endpoint "Download File" "GET" "/download/3rd_Year_-_CSIT.pdf" "200"

# Test 7: Delete Non-existent File (should be 404)
test_endpoint "Delete Non-existent File" "DELETE" "/delete/nonexistent.pdf" "404"

echo ""
echo "=========================================="
echo "Test Results:"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
