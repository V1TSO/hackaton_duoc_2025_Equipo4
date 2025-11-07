#!/bin/bash

# Test script for ML API endpoints
# This script tests the backend API to verify the local model is being used

API_URL="${1:-http://localhost:8000}"
echo "Testing API at: $API_URL"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Test 1: Health Check${NC}"
echo "GET $API_URL/health"
curl -s "$API_URL/health" | python3 -m json.tool
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi

echo -e "\n${BLUE}Test 2: Predict Endpoint (without auth)${NC}"
echo "POST $API_URL/api/health/predict"
RESPONSE=$(curl -s -X POST "$API_URL/api/health/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "edad": 45,
    "genero": "M",
    "imc": 31.0,
    "circunferencia_cintura": 105,
    "horas_sueno": 6.0,
    "tabaquismo": true,
    "actividad_fisica": "sedentario"
  }')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null

if echo "$RESPONSE" | grep -q "score"; then
    echo -e "${GREEN}✓ Prediction endpoint working${NC}"
    SCORE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('score', 'N/A'))")
    echo -e "   Risk Score: $SCORE"
else
    echo -e "${RED}✗ Prediction endpoint failed or requires auth${NC}"
    echo "   Try running with: export SUPABASE_TOKEN=your_token"
fi

echo -e "\n${BLUE}Test 3: Check Backend Logs${NC}"
echo "Look for these messages in your backend console:"
echo "  - 'Model loaded successfully'"
echo "  - 'USING LOCAL ML MODEL' (if you added the logging)"
echo "  - NO messages about 'Colab' or external API calls"

echo -e "\n${BLUE}Test 4: Verify Model Files${NC}"
MODEL_DIR="app/ml/models"
if [ -f "$MODEL_DIR/model_xgb_calibrated.pkl" ]; then
    echo -e "${GREEN}✓ model_xgb_calibrated.pkl found${NC}"
    ls -lh "$MODEL_DIR/model_xgb_calibrated.pkl"
else
    echo -e "${RED}✗ model_xgb_calibrated.pkl not found${NC}"
fi

if [ -f "$MODEL_DIR/imputer.pkl" ]; then
    echo -e "${GREEN}✓ imputer.pkl found${NC}"
else
    echo -e "${RED}✗ imputer.pkl not found${NC}"
fi

if [ -f "$MODEL_DIR/feature_names.pkl" ]; then
    echo -e "${GREEN}✓ feature_names.pkl found${NC}"
else
    echo -e "${RED}✗ feature_names.pkl not found${NC}"
fi

echo -e "\n${BLUE}Test 5: Check Knowledge Base${NC}"
KB_DIR="../kb"
if [ -d "$KB_DIR" ]; then
    echo -e "${GREEN}✓ Knowledge base directory found${NC}"
    echo "   Files:"
    ls -1 "$KB_DIR" | head -5
    MD_COUNT=$(ls -1 "$KB_DIR"/*.md 2>/dev/null | wc -l)
    echo "   Markdown files: $MD_COUNT"
else
    echo -e "${RED}✗ Knowledge base directory not found${NC}"
fi

echo -e "\n=================================="
echo -e "${BLUE}Testing Complete!${NC}"
echo ""
echo "Next Steps:"
echo "1. If prediction test failed due to auth, update your .env with valid Supabase credentials"
echo "2. Check backend console for 'Model loaded successfully' message"
echo "3. Test from frontend at http://localhost:3000/assess"
echo ""

