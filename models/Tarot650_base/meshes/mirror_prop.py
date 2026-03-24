#!/usr/bin/env python3
"""
Create mirrored version of prop_15x5.dae -> prop_15x5_ccw.dae
Mirrors along Y-axis to create counter-clockwise version
"""

import xml.etree.ElementTree as ET
import os
import re

# Namespace
NS = {'collada': 'http://www.collada.org/2005/11/COLLADASchema'}
ET.register_namespace('', 'http://www.collada.org/2005/11/COLLADASchema')

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, 'prop_15x5.dae')
output_file = os.path.join(script_dir, 'prop_15x5_ccw.dae')

print(f"=== Creating Mirrored Propeller ===")
print(f"Input: {input_file}")
print(f"Output: {output_file}")
print(f"Mirror axis: Y-axis (Y values will be negated)")

if not os.path.exists(input_file):
    print(f"\n✗ ERROR: {input_file} not found!")
    print("Please run extract_prop.py first to create prop_15x5.dae")
    exit(1)

# Parse input file
print("\nParsing input file...")
tree = ET.parse(input_file)
root = tree.getroot()

# Find all float_array elements (contain vertex positions)
print("\nMirroring vertex positions...")
float_arrays = root.findall('.//collada:float_array', NS)

vertices_mirrored = 0
for float_array in float_arrays:
    # Check if this is a position array (usually has 'Position' in id)
    array_id = float_array.get('id', '')
    if 'Position' in array_id or 'position' in array_id.lower():
        print(f"  Processing: {array_id}")

        # Get the float values
        text = float_array.text.strip()
        values = [float(v) for v in text.split()]

        # Values are in triplets: x y z x y z x y z ...
        # Mirror Y-axis: negate every second value (index 1, 4, 7, ...)
        for i in range(1, len(values), 3):
            values[i] = -values[i]
            vertices_mirrored += 1

        # Convert back to string
        float_array.text = ' '.join(str(v) for v in values)
        print(f"    Mirrored {vertices_mirrored} vertices")

# Find all matrix elements and mirror their Y-axis transforms
print("\nMirroring transformation matrices...")
matrices = root.findall('.//collada:matrix', NS)
for matrix in matrices:
    text = matrix.text.strip()
    values = [float(v) for v in text.split()]

    if len(values) == 16:  # 4x4 transformation matrix
        # Mirror Y-axis: negate row 2 (indices 4-7) and column 2 (indices 1, 5, 9, 13)
        # But for simple mirroring, we can use scale transform
        # Format: m00 m01 m02 m03 m10 m11 m12 m13 m20 m21 m22 m23 m30 m31 m32 m33
        # We'll negate the Y-scale component (m11) and Y-translation (m31)
        values[5] = -values[5]   # m11 (Y-scale)
        values[13] = -values[13] # m31 (Y-translation)

        matrix.text = ' '.join(str(v) for v in values)
        print(f"  Mirrored matrix transform")

# Update IDs and names to indicate this is CCW version
print("\nUpdating IDs and names...")
# Update geometry IDs
for geom in root.findall('.//collada:geometry', NS):
    old_id = geom.get('id')
    if old_id:
        new_id = old_id.replace('geo_', 'geo_ccw_')
        geom.set('id', new_id)
        old_name = geom.get('name', '')
        if old_name:
            geom.set('name', old_name + '_ccw')
        print(f"  Renamed: {old_id} -> {new_id}")

# Update source IDs in geometries
for source in root.findall('.//collada:source', NS):
    old_id = source.get('id')
    if old_id and 'geo_' in old_id:
        new_id = old_id.replace('geo_', 'geo_ccw_')
        source.set('id', new_id)

# Update float_array IDs
for arr in root.findall('.//collada:float_array', NS):
    old_id = arr.get('id')
    if old_id and 'geo_' in old_id:
        new_id = old_id.replace('geo_', 'geo_ccw_')
        arr.set('id', new_id)

# Update all URL references
for elem in root.iter():
    for attr in ['url', 'source']:
        if attr in elem.attrib:
            old_val = elem.attrib[attr]
            if '#geo_' in old_val:
                elem.attrib[attr] = old_val.replace('#geo_', '#geo_ccw_')

# Update node names
for node in root.findall('.//collada:node', NS):
    old_name = node.get('name')
    if old_name and 'propeller' in old_name.lower():
        node.set('name', old_name + '_ccw')
        print(f"  Renamed node: {old_name} -> {old_name}_ccw")

# Write output
print(f"\nWriting to {output_file}...")
tree_out = ET.ElementTree(root)

with open(output_file, 'wb') as f:
    f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
    tree_out.write(f, encoding='utf-8', xml_declaration=False)

print(f"\n✓ Successfully created prop_15x5_ccw.dae")
print(f"  Output size: {os.path.getsize(output_file)} bytes")
print(f"  Mirrored: {vertices_mirrored} vertices")
print(f"\nUsage:")
print(f"  CW:  prop_15x5.dae     (original)")
print(f"  CCW: prop_15x5_ccw.dae (mirrored along Y-axis)")
