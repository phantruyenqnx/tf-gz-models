#!/usr/bin/env python3
"""
Extract motor bell from x650.dae to motor_3508_bell.dae
Uses bell.stp.STEP-2 as the source
"""

import xml.etree.ElementTree as ET
import os

# Namespace
NS = {'collada': 'http://www.collada.org/2005/11/COLLADASchema'}
ET.register_namespace('', 'http://www.collada.org/2005/11/COLLADASchema')

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, 'x650.dae')
output_file = os.path.join(script_dir, 'motor_3508_bell.dae')

print(f"=== Extracting Motor Bell ===")
print(f"Input: {input_file}")
print(f"Output: {output_file}")

# Parse input file
print("\nParsing input file...")
tree = ET.parse(input_file)
root = tree.getroot()

# Find bell.stp.STEP-2 node and collect all referenced IDs
print("Finding bell.stp.STEP-2 node...")
bell_node = None
for node in root.findall('.//collada:node[@name="bell.stp.STEP-2"]', NS):
    bell_node = node
    print(f"✓ Found: {node.get('id')} - {node.get('name')}")
    break

if not bell_node:
    print("✗ ERROR: bell.stp.STEP-2 not found!")
    exit(1)

# Collect all geometry, material, effect, and image IDs
geometry_ids = set()
material_ids = set()
effect_ids = set()
image_ids = set()

print("\nCollecting references...")
for geom in bell_node.findall('.//collada:instance_geometry', NS):
    geom_id = geom.get('url', '').replace('#', '')
    if geom_id:
        geometry_ids.add(geom_id)
        print(f"  Geometry: {geom_id}")

    for mat in geom.findall('.//collada:instance_material', NS):
        mat_id = mat.get('target', '').replace('#', '')
        if mat_id:
            material_ids.add(mat_id)
            print(f"  Material: {mat_id}")

# Get effects from materials
library_materials = root.find('collada:library_materials', NS)
if library_materials:
    for material in library_materials.findall('collada:material', NS):
        if material.get('id') in material_ids:
            effect = material.find('collada:instance_effect', NS)
            if effect is not None:
                eff_id = effect.get('url', '').replace('#', '')
                if eff_id:
                    effect_ids.add(eff_id)
                    print(f"  Effect: {eff_id}")

# Get images from effects
library_effects = root.find('collada:library_effects', NS)
if library_effects:
    for effect in library_effects.findall('collada:effect', NS):
        if effect.get('id') in effect_ids:
            for init_from in effect.findall('.//collada:init_from', NS):
                img_id = init_from.text
                if img_id:
                    image_ids.add(img_id)
                    print(f"  Image: {img_id}")

print(f"\nSummary:")
print(f"  - {len(geometry_ids)} geometries")
print(f"  - {len(material_ids)} materials")
print(f"  - {len(effect_ids)} effects")
print(f"  - {len(image_ids)} images")

# Create new COLLADA document
print("\nBuilding output document...")
new_root = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}COLLADA')
new_root.set('version', '1.4.0')

# Copy asset
asset = root.find('collada:asset', NS)
if asset is not None:
    new_root.append(asset)

# Copy images
if image_ids:
    library_images = root.find('collada:library_images', NS)
    if library_images is not None:
        new_images = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}library_images')
        for image in library_images.findall('collada:image', NS):
            if image.get('id') in image_ids:
                new_images.append(image)
        if len(new_images):
            new_root.append(new_images)

# Copy effects
if effect_ids:
    library_effects = root.find('collada:library_effects', NS)
    if library_effects is not None:
        new_effects = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}library_effects')
        for effect in library_effects.findall('collada:effect', NS):
            if effect.get('id') in effect_ids:
                new_effects.append(effect)
        if len(new_effects):
            new_root.append(new_effects)

# Copy materials
if material_ids:
    library_materials = root.find('collada:library_materials', NS)
    if library_materials is not None:
        new_materials = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}library_materials')
        for material in library_materials.findall('collada:material', NS):
            if material.get('id') in material_ids:
                new_materials.append(material)
        if len(new_materials):
            new_root.append(new_materials)

# Copy geometries
if geometry_ids:
    library_geometries = root.find('collada:library_geometries', NS)
    if library_geometries is not None:
        new_geometries = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}library_geometries')
        for geometry in library_geometries.findall('collada:geometry', NS):
            if geometry.get('id') in geometry_ids:
                new_geometries.append(geometry)
        if len(new_geometries):
            new_root.append(new_geometries)

# Create visual scene with bell node
new_visual_scenes = ET.Element('{http://www.collada.org/2005/11/COLLADASchema}library_visual_scenes')
new_scene = ET.SubElement(new_visual_scenes, '{http://www.collada.org/2005/11/COLLADASchema}visual_scene')
new_scene.set('id', 'Scene')
new_scene.set('name', 'Scene')

# Add root node with identity matrix
root_node = ET.SubElement(new_scene, '{http://www.collada.org/2005/11/COLLADASchema}node')
matrix = ET.SubElement(root_node, '{http://www.collada.org/2005/11/COLLADASchema}matrix')
matrix.text = '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'

# Copy bell node (with identity matrix to center it at origin)
bell_copy = ET.SubElement(root_node, '{http://www.collada.org/2005/11/COLLADASchema}node')
bell_copy.set('id', 'motor_bell')
bell_copy.set('name', 'motor_bell')

# Add identity matrix instead of original transform
bell_matrix = ET.SubElement(bell_copy, '{http://www.collada.org/2005/11/COLLADASchema}matrix')
bell_matrix.text = '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'

# Copy all child nodes from original bell
for child in bell_node:
    if child.tag != '{http://www.collada.org/2005/11/COLLADASchema}matrix':
        bell_copy.append(child)

new_root.append(new_visual_scenes)

# Add scene reference
scene_elem = ET.SubElement(new_root, '{http://www.collada.org/2005/11/COLLADASchema}scene')
inst_scene = ET.SubElement(scene_elem, '{http://www.collada.org/2005/11/COLLADASchema}instance_visual_scene')
inst_scene.set('url', '#Scene')

# Write output
print(f"\nWriting to {output_file}...")
tree_out = ET.ElementTree(new_root)

with open(output_file, 'wb') as f:
    f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
    tree_out.write(f, encoding='utf-8', xml_declaration=False)

print(f"\n✓ Successfully created motor_3508_bell.dae")
print(f"  Output size: {os.path.getsize(output_file)} bytes")
