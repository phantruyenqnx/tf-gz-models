#!/bin/bash

# Verify Improvements Script
# Date: 2026-01-17
# Purpose: Quick check of model parameter improvements

set -e

echo "=========================================="
echo "🔍 Verifying Model Improvements"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check parameter
check_param() {
    local file=$1
    local pattern=$2
    local expected=$3
    local description=$4
    
    if grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} $description: ${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} $description: ${RED}NOT FOUND${NC}"
        return 1
    fi
}

# Function to count occurrences
count_param() {
    local file=$1
    local pattern=$2
    local expected=$3
    local description=$4
    
    count=$(grep -c "$pattern" "$file" || true)
    
    if [ "$count" -ge "$expected" ]; then
        echo -e "${GREEN}✓${NC} $description: ${GREEN}$count occurrences${NC} (expected ≥$expected)"
        return 0
    else
        echo -e "${RED}✗${NC} $description: ${RED}$count occurrences${NC} (expected ≥$expected)"
        return 1
    fi
}

echo "📋 Checking Tether Cable (models/tether_cable/model.sdf)..."
echo ""

TETHER_FILE="models/tether_cable/model.sdf"

# Check mass increases
check_param "$TETHER_FILE" "<mass>0.004</mass>" "0.004" "Link attachment mass = 0.004 kg"
count_param "$TETHER_FILE" "<mass>0.005</mass>" 24 "Cable segments mass = 0.005 kg"

# Check spring stiffness = 0
count_param "$TETHER_FILE" "<spring_stiffness>0</spring_stiffness>" 24 "Spring stiffness = 0"

# Check damping = 0.02
count_param "$TETHER_FILE" "<damping>0.02</damping>" 24 "Damping = 0.02"

# Check unified contact params
count_param "$TETHER_FILE" "<kp>5e5</kp>" 25 "Contact kp = 5e5"
count_param "$TETHER_FILE" "<kd>500</kd>" 25 "Contact kd = 500"
count_param "$TETHER_FILE" "<max_vel>10.0</max_vel>" 25 "Contact max_vel = 10.0"

echo ""
echo "📦 Checking Payload (models/payload/model.sdf)..."
echo ""

PAYLOAD_FILE="models/payload/model.sdf"

# Check velocity decay
check_param "$PAYLOAD_FILE" "<linear>0.05</linear>" "0.05" "Linear velocity decay = 0.05"
check_param "$PAYLOAD_FILE" "<angular>0.05</angular>" "0.05" "Angular velocity decay = 0.05"

# Check contact params match
check_param "$PAYLOAD_FILE" "<kp>5e5</kp>" "5e5" "Payload contact kp = 5e5"
check_param "$PAYLOAD_FILE" "<kd>500</kd>" "500" "Payload contact kd = 500"

echo ""
echo "🌍 Checking World (worlds/default_bullet.sdf)..."
echo ""

WORLD_FILE="worlds/default_bullet.sdf"

# Check ground plane params match
check_param "$WORLD_FILE" "<kp>5e5</kp>" "5e5" "Ground contact kp = 5e5"
check_param "$WORLD_FILE" "<kd>500</kd>" "500" "Ground contact kd = 500"

echo ""
echo "=========================================="
echo "📊 Summary"
echo "=========================================="
echo ""

# Calculate total cable mass
CABLE_MASS=$(echo "0.004 + 24 * 0.005" | bc)
echo -e "Cable total mass: ${GREEN}${CABLE_MASS} kg${NC} (was 0.061 kg)"
echo -e "Cable mass/length: ${GREEN}~41 g/m${NC} (was ~20 g/m)"
echo ""

echo -e "${GREEN}All improvements verified!${NC}"
echo ""
echo "Next steps:"
echo "1. Test spawn: gz model --spawn-file=models/x500_slung_payload/model.sdf -x 0 -y 0 -z 2"
echo "2. Run oscillation test"
echo "3. Validate in flight simulation"
echo ""
echo "See IMPROVEMENTS_2026-01-17.md for details."
