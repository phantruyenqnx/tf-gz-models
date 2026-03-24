#!/usr/bin/env python3
"""
Generate convex decomposition collision meshes using CoACD

All collision meshes are saved to the 'collisions' subdirectory.
"""

import coacd
import trimesh
import numpy as np
from pathlib import Path


def generate_collision_mesh(input_file: str, output_name: str, output_dir: Path, threshold: float = 0.05):
    """
    Generate convex decomposition collision meshes from a DAE file
    
    Args:
        input_file: Path to input mesh (DAE, STL, OBJ, etc.)
        output_name: Base name for output collision files (e.g., 'obstacle-1m7')
        output_dir: Directory to save collision files
        threshold: CoACD threshold (lower = more parts, higher accuracy)
    
    Returns:
        List of collision file names (relative to output_dir)
    """
    print(f"Loading mesh: {input_file}")
    mesh = trimesh.load(input_file, force='mesh')
    
    # Convert to format CoACD expects
    vertices = np.array(mesh.vertices, dtype=np.float64)
    faces = np.array(mesh.faces, dtype=np.int32)
    
    print(f"Mesh has {len(vertices)} vertices and {len(faces)} faces")
    
    # Run CoACD convex decomposition
    print(f"Running CoACD with threshold={threshold}...")
    
    # Create mesh object for coacd
    coacd_mesh = coacd.Mesh(vertices, faces)
    parts = coacd.run_coacd(
        coacd_mesh,
        threshold=threshold,
        max_convex_hull=32,  # Max number of convex parts
        preprocess_mode="auto",
        resolution=2000,
    )
    
    print(f"Generated {len(parts)} convex parts")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save each convex part as separate STL
    collision_files = []
    for i, (part_verts, part_faces) in enumerate(parts):
        part_mesh = trimesh.Trimesh(vertices=part_verts, faces=part_faces)
        filename = f"{output_name}_collision_{i}.stl"
        output_file = output_dir / filename
        part_mesh.export(str(output_file))
        collision_files.append(filename)
        print(f"  Saved: {filename}")
    
    return collision_files


def main():
    meshes_dir = Path(__file__).parent
    collisions_dir = meshes_dir / "collisions"
    
    # Process obstacle-1m7.dae
    print("\n" + "="*60)
    print("Processing obstacle-1m7.dae")
    print("="*60)
    collision_1m7 = generate_collision_mesh(
        str(meshes_dir / "obstacle-1m7.dae"),
        "obstacle-1m7",
        collisions_dir,
        threshold=0.05
    )
    
    # Process obstacle-2m2.dae
    print("\n" + "="*60)
    print("Processing obstacle-2m2.dae")
    print("="*60)
    collision_2m2 = generate_collision_mesh(
        str(meshes_dir / "obstacle-2m2.dae"),
        "obstacle-2m2",
        collisions_dir,
        threshold=0.05
    )
    
    # Process rescued.dae
    print("\n" + "="*60)
    print("Processing rescued.dae")
    print("="*60)
    collision_rescued = generate_collision_mesh(
        str(meshes_dir / "rescued.dae"),
        "rescued",
        collisions_dir,
        threshold=0.05
    )
    
    # Print SDF snippet for collision
    print("\n" + "="*60)
    print("SDF Collision Snippets:")
    print("="*60)
    
    print("\n<!-- For TZ1/TZ3 (obstacle-1m7) -->")
    for i, f in enumerate(collision_1m7):
        print(f'<collision name="collision_{i}">')
        print(f'  <geometry><mesh><uri>model://uav_contest_2026/meshes/collisions/{f}</uri></mesh></geometry>')
        print('</collision>')
    
    print("\n<!-- For TZ2/TZ4 (obstacle-2m2) -->")
    for i, f in enumerate(collision_2m2):
        print(f'<collision name="collision_{i}">')
        print(f'  <geometry><mesh><uri>model://uav_contest_2026/meshes/collisions/{f}</uri></mesh></geometry>')
        print('</collision>')
    
    print("\n<!-- For rescued models -->")
    for i, f in enumerate(collision_rescued):
        print(f'<collision name="collision_{i}">')
        print(f'  <geometry><mesh><uri>model://uav_contest_2026/meshes/collisions/{f}</uri></mesh></geometry>')
        print('</collision>')


if __name__ == "__main__":
    main()
