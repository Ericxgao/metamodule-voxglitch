import xml.etree.ElementTree as ET
import json
import sys
import os
import re

def parse_transform(transform_str):
    """
    Parse transform string to extract translation values.
    Returns (translate_x, translate_y) tuple.
    """
    if not transform_str:
        return (0, 0)
    
    # Extract translate values using regex
    translate_match = re.search(r'translate\(([-\d.]+),([-\d.]+)\)', transform_str)
    if translate_match:
        return (float(translate_match.group(1)), float(translate_match.group(2)))
    return (0, 0)

def get_accumulated_transform(elem, root):
    """
    Get accumulated transform from element and all its parents.
    """
    translate_x = 0
    translate_y = 0
    
    # Get all ancestors of the element
    ancestors = []
    current = elem
    while current is not None and current != root:
        ancestors.append(current)
        # Find parent by searching through all elements
        for parent in root.iter():
            if current in list(parent):
                current = parent
                break
        else:
            current = None
    
    # Process transforms from root to element
    for ancestor in reversed(ancestors):
        transform = ancestor.get("transform", "")
        tx, ty = parse_transform(transform)
        translate_x += tx
        translate_y += ty
    
    return (translate_x, translate_y)

def extract_positions(svg_file):
    """
    Extract positions from SVG file and return them as a dictionary.
    
    Args:
        svg_file (str): Path to the SVG file
    
    Returns:
        dict: Dictionary of positions keyed by element ID
    """
    # Parse the SVG
    tree = ET.parse(svg_file)
    root = tree.getroot()

    scale_x = 1.04
    scale_y = 1.04

    if "ghosts" in svg_file or "samplerx8" in svg_file:
        scale_x = 2.96
        scale_y = 2.96

    # Find all elements with IDs
    positions = {}
    for elem in root.findall(".//*[@id]"):
        id = elem.get("id")
        
        # Get accumulated transform
        translate_x, translate_y = get_accumulated_transform(elem, root)
        
        # For circles, use the center
        if elem.tag.endswith("circle"):
            x = float(elem.get("cx", "0")) + translate_x
            y = float(elem.get("cy", "0")) + translate_y
            positions[id] = {"x": x * scale_x, "y": y * scale_y}
        
        # For rectangles, use the center
        elif elem.tag.endswith("rect"):
            x = float(elem.get("x", "0")) + float(elem.get("width", "0")) / 2 + translate_x
            y = float(elem.get("y", "0")) + float(elem.get("height", "0")) / 2 + translate_y
            positions[id] = {"x": x * scale_x, "y": y * scale_y}
            
        # For ellipses, use the center
        elif elem.tag.endswith("ellipse"):
            x = float(elem.get("cx", "0")) + translate_x
            y = float(elem.get("cy", "0")) + translate_y
            positions[id] = {"x": x * scale_x, "y": y * scale_y}
    
    return positions

def write_output(all_positions, output_file, format_type="hpp"):
    """
    Write the collected positions to a file in the specified format.
    
    Args:
        all_positions (dict): Dictionary of module positions
        output_file (str): Path to the output file
        format_type (str): "json" or "hpp" for JSON or C++ header output
    """
    # Flatten the positions dictionary
    flattened_positions = {}
    for module_name, positions in all_positions.items():
        for element_id, pos in positions.items():
            flattened_positions[element_id] = pos

    if format_type.lower() == "json":
        with open(output_file, "w") as f:
            json.dump({"modules": flattened_positions}, f, indent=2)
    else:  # hpp format
        # Write to C++ header file
        with open(output_file, "w") as f:
            f.write("#pragma once\n\n")
            f.write("#include <map>\n")
            f.write("#include <string>\n")
            f.write("#include <rack.hpp>\n\n")
            
            f.write("struct VoxglitchPositions {\n")
            f.write("    inline static std::map<std::string, rack::Vec> modules = {\n")
            
            # Write each position entry
            position_items = list(flattened_positions.items())
            for i, (element_id, pos) in enumerate(position_items):
                if i == len(position_items) - 1:
                    # Last item doesn't need a comma
                    f.write(f'        {{"{element_id}", rack::Vec({pos["x"]:.3f}f, {pos["y"]:.3f}f)}}\n')
                else:
                    f.write(f'        {{"{element_id}", rack::Vec({pos["x"]:.3f}f, {pos["y"]:.3f}f)}},\n')
            
            f.write("    };\n")
            f.write("};\n")

def process_directory(directory, format_type="hpp"):
    """
    Recursively process a directory to find SVG files and extract positions.
    
    Args:
        directory (str): Directory path to scan
        format_type (str): "json" or "hpp" for output format
    
    Returns:
        dict: Dictionary of all positions by module name
    """
    all_positions = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".svg"):
                svg_file = os.path.join(root, file)
                module_name = os.path.basename(os.path.dirname(svg_file))
                
                try:
                    positions = extract_positions(svg_file)
                    if positions:
                        # Use the module name (directory name) as the key
                        all_positions[module_name] = all_positions.get(module_name, {})
                        
                        # Add a prefix with the filename to avoid ID collisions
                        file_base = os.path.splitext(os.path.basename(svg_file))[0]
                        for id, pos in positions.items():
                            all_positions[module_name][f"{file_base}_{id}"] = pos
                        
                        print(f"Processed {svg_file}")
                except Exception as e:
                    print(f"Error processing {svg_file}: {e}")
    
    return all_positions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_positions.py <directory> [output_file] [format=hpp|json]")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # Default output file
    output_file = "voxglitch_positions"
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    # Default format
    format_type = "hpp"
    if len(sys.argv) >= 4:
        format_type = sys.argv[3]
    
    # Add extension if not specified
    if not output_file.endswith(".hpp") and not output_file.endswith(".json"):
        if format_type.lower() == "json":
            output_file += ".json"
        else:
            output_file += ".hpp"
    
    # Process directory and write output
    all_positions = process_directory(directory, format_type)
    write_output(all_positions, output_file, format_type)
    print(f"Created flattened position lookup table in {output_file}")
    print(f"Processed {len(all_positions)} modules with {sum(len(pos) for pos in all_positions.values())} elements")