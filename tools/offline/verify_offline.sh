#!/bin/bash

################################################################################
# Verify Offline Capability of Gazebo Models
#
# This script checks that all models can be loaded without internet connection
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# this script lives in tools/offline/ ; models and worlds are two levels up
MODELS_DIR="$(cd "${SCRIPT_DIR}/../../models" && pwd)"
WORLDS_DIR="$(cd "${SCRIPT_DIR}/../../worlds" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Offline Capability Verification"
echo "=========================================="
echo ""

# Check for Fuel URLs in critical model files (used by baylands and forest worlds)
echo "Checking for online URLs in critical model files..."
echo ""

CRITICAL_MODELS=("baylands" "Coast Water" "grasspatch" "Oak Tree" "Pine Tree")
FOUND_URLS=false

for model in "${CRITICAL_MODELS[@]}"; do
    MODEL_SDF="${MODELS_DIR}/${model}/model.sdf"
    if [ -f "$MODEL_SDF" ]; then
        FUEL_URLS=$(grep "https://fuel\." "$MODEL_SDF" | grep -v "<!--" || true)
        if [ -n "$FUEL_URLS" ]; then
            echo -e "${RED}✗ Found Fuel URLs in ${model}:${NC}"
            echo "$FUEL_URLS"
            FOUND_URLS=true
        fi
    fi
done

if [ "$FOUND_URLS" = true ]; then
    echo ""
    echo -e "${YELLOW}Critical models still have online URLs!${NC}"
    exit 1
else
    echo -e "${GREEN}✓ No Fuel URLs found in critical model files${NC}"
fi

echo ""

# Check for Fuel URLs in world files
echo "Checking for online URLs in world files..."
echo ""

FUEL_URLS_WORLDS=$(grep -r "https://fuel\." "${WORLDS_DIR}" --include="*.sdf" || true)

if [ -n "$FUEL_URLS_WORLDS" ]; then
    echo -e "${RED}✗ Found Fuel URLs in world files:${NC}"
    echo "$FUEL_URLS_WORLDS"
    echo ""
    echo -e "${YELLOW}These worlds will require internet connection!${NC}"
    exit 1
else
    echo -e "${GREEN}✓ No Fuel URLs found in world files${NC}"
fi

echo ""

# Check that required models exist
echo "Checking required models for offline worlds..."
echo ""

REQUIRED_MODELS=("baylands" "Coast Water" "grasspatch" "Oak Tree" "Pine Tree")
ALL_PRESENT=true

for model in "${REQUIRED_MODELS[@]}"; do
    if [ -d "${MODELS_DIR}/${model}" ]; then
        echo -e "${GREEN}✓ ${model}${NC}"
    else
        echo -e "${RED}✗ ${model} - NOT FOUND${NC}"
        ALL_PRESENT=false
    fi
done

echo ""

if [ "$ALL_PRESENT" = false ]; then
    echo -e "${RED}=========================================="
    echo -e "Missing required models!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Run: ./download_external_models.sh"
    exit 1
fi

# Verify model.sdf files use model:// URIs
echo "Verifying models use local paths..."
echo ""

MODELS_TO_CHECK=("baylands" "Coast Water" "grasspatch" "Oak Tree" "Pine Tree")

for model in "${MODELS_TO_CHECK[@]}"; do
    MODEL_SDF="${MODELS_DIR}/${model}/model.sdf"
    if [ -f "$MODEL_SDF" ]; then
        # Check if model uses model:// URIs or relative paths
        if grep -q "model://${model}" "$MODEL_SDF" || ! grep -q "https://" "$MODEL_SDF"; then
            echo -e "${GREEN}✓ ${model} uses local paths${NC}"
        else
            echo -e "${RED}✗ ${model} still has online URLs${NC}"
            ALL_PRESENT=false
        fi
    fi
done

echo ""

if [ "$ALL_PRESENT" = false ]; then
    echo -e "${RED}Some models still reference online resources${NC}"
    exit 1
fi

echo -e "${GREEN}=========================================="
echo -e "All checks passed!"
echo -e "==========================================${NC}"
echo ""
echo "Your Gazebo worlds are ready for offline use!"
echo ""
echo "To use offline, ensure GZ_SIM_RESOURCE_PATH is set:"
echo "  export GZ_SIM_RESOURCE_PATH=\${GZ_SIM_RESOURCE_PATH}:${MODELS_DIR}"
echo ""
echo "Test with:"
echo "  gz sim ${WORLDS_DIR}/baylands.sdf"
echo "  gz sim ${WORLDS_DIR}/forest.sdf"

exit 0

