#!/bin/bash

################################################################################
# Download External Gazebo Models for Offline Use
#
# This script downloads external models from Gazebo Fuel to enable offline
# simulation. Models are stored in the local models directory.
#
# Usage: ./download_external_models.sh
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# this script lives in tools/offline/ ; the models directory is two levels up
MODELS_DIR="$(cd "${SCRIPT_DIR}/../../models" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Gazebo External Models Download Script"
echo "=========================================="
echo ""
echo "Models directory: ${MODELS_DIR}"
echo ""

# Function to download a model from Fuel
download_fuel_model() {
    local owner="$1"
    local model_name="$2"
    local fuel_server="$3"
    
    echo -e "${YELLOW}Downloading: ${model_name} from ${owner}...${NC}"
    
    local target_dir="${MODELS_DIR}/${model_name}"
    
    # Check if model already exists
    if [ -d "${target_dir}" ]; then
        echo -e "${GREEN}✓ Model '${model_name}' already exists, skipping...${NC}"
        return 0
    fi
    
    # Try using gz fuel download command
    if command -v gz &> /dev/null; then
        echo "  Using 'gz fuel download' command..."
        if gz fuel download -u "https://${fuel_server}/1.0/${owner}/models/${model_name}" -v 4; then
            echo -e "${GREEN}✓ Successfully downloaded ${model_name}${NC}"
            
            # Move from fuel cache to models directory
            # Gazebo stores models with lowercase names, so we need to search case-insensitively
            local fuel_cache_base="${HOME}/.gz/fuel/${fuel_server}/${owner}/models"
            local model_name_lower=$(echo "${model_name}" | tr '[:upper:]' '[:lower:]')
            
            # Try exact match first, then lowercase
            local fuel_cache="${fuel_cache_base}/${model_name}"
            if [ ! -d "${fuel_cache}" ]; then
                fuel_cache="${fuel_cache_base}/${model_name_lower}"
            fi
            
            if [ -d "${fuel_cache}" ]; then
                # Get the latest version
                local latest_version=$(ls -1 "${fuel_cache}" | sort -V | tail -n 1)
                if [ -n "${latest_version}" ]; then
                    cp -r "${fuel_cache}/${latest_version}" "${target_dir}"
                    echo -e "${GREEN}✓ Copied to ${target_dir}${NC}"
                fi
            else
                echo -e "${YELLOW}⚠ Downloaded but could not find in cache: ${fuel_cache}${NC}"
            fi
            return 0
        else
            echo -e "${RED}✗ Failed to download ${model_name} using gz command${NC}"
        fi
    fi
    
    # Fallback: Try using wget/curl to download directly
    echo "  Trying direct download..."
    local download_url="https://${fuel_server}/1.0/${owner}/models/${model_name}/tip/files"
    
    if command -v wget &> /dev/null; then
        mkdir -p "${target_dir}"
        if wget -r -np -nH --cut-dirs=6 -R "index.html*" -P "${target_dir}" "${download_url}"; then
            echo -e "${GREEN}✓ Successfully downloaded ${model_name} using wget${NC}"
            return 0
        fi
    elif command -v curl &> /dev/null; then
        mkdir -p "${target_dir}"
        echo -e "${YELLOW}  Note: Manual download may be required for ${model_name}${NC}"
        echo -e "${YELLOW}  URL: ${download_url}${NC}"
    fi
    
    echo -e "${RED}✗ Could not download ${model_name}${NC}"
    echo -e "${YELLOW}  Please download manually from: https://${fuel_server}/1.0/${owner}/models/${model_name}${NC}"
    return 1
}

# Download models for baylands world
echo "=========================================="
echo "Downloading models for 'baylands' world"
echo "=========================================="
download_fuel_model "OpenRobotics" "baylands" "fuel.gazebosim.org"
download_fuel_model "OpenRobotics" "Coast Water" "fuel.gazebosim.org"

echo ""
echo "=========================================="
echo "Downloading models for 'forest' world"
echo "=========================================="
download_fuel_model "hexarotor" "grasspatch" "fuel.ignitionrobotics.org"
download_fuel_model "OpenRobotics" "Oak Tree" "fuel.ignitionrobotics.org"
download_fuel_model "OpenRobotics" "Pine Tree" "fuel.ignitionrobotics.org"

echo ""
echo "=========================================="
echo "Download Summary"
echo "=========================================="
echo ""

# Check which models exist
models_to_check=("baylands" "Coast Water" "grasspatch" "Oak Tree" "Pine Tree")
all_present=true

for model in "${models_to_check[@]}"; do
    if [ -d "${MODELS_DIR}/${model}" ]; then
        echo -e "${GREEN}✓ ${model}${NC}"
    else
        echo -e "${RED}✗ ${model} - NOT FOUND${NC}"
        all_present=false
    fi
done

echo ""
if [ "$all_present" = true ]; then
    echo -e "${GREEN}=========================================="
    echo -e "All models downloaded successfully!"
    echo -e "==========================================${NC}"
    echo ""
    echo "You can now use baylands and forest worlds offline."
    echo ""
    echo "To use these models, ensure GZ_SIM_RESOURCE_PATH includes:"
    echo "  export GZ_SIM_RESOURCE_PATH=\${GZ_SIM_RESOURCE_PATH}:${MODELS_DIR}"
    exit 0
else
    echo -e "${YELLOW}=========================================="
    echo -e "Some models could not be downloaded"
    echo -e "==========================================${NC}"
    echo ""
    echo "Please download missing models manually from:"
    echo "  - https://fuel.gazebosim.org"
    echo "  - https://fuel.ignitionrobotics.org"
    echo ""
    echo "Place them in: ${MODELS_DIR}"
    exit 1
fi

