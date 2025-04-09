#!/bin/bash

# Define input and output directories
INPUT_DIR="voxglitch/res"
OUTPUT_DIR="assets"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to process a directory recursively
process_directory() {
    local current_dir="$1"
    local rel_path="${current_dir#$INPUT_DIR/}"
    
    # Create corresponding output directory
    if [ "$current_dir" != "$INPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR/$rel_path"
    fi
    
    # Process files in the current directory
    find "$current_dir" -maxdepth 1 -type f | while read -r file; do
        filename=$(basename "$file")
        
        if [ "$current_dir" = "$INPUT_DIR" ]; then
            # Files in the root input directory
            target_dir="$OUTPUT_DIR"
        else
            # Files in subdirectories
            target_dir="$OUTPUT_DIR/$rel_path"
        fi
        
        # Check if file is SVG - SVGs will be converted by SvgToPng.py
        if [[ "$filename" == *.svg ]]; then
            echo "SVG file will be handled by SvgToPng.py: $file"
        else
            # Copy non-SVG files directly
            echo "Copying non-SVG file: $file to $target_dir/$filename"
            cp "$file" "$target_dir/$filename"
        fi
    done
    
    # # Run SVG to PNG conversion for this directory
    # if find "$current_dir" -maxdepth 1 -name "*.svg" | grep -q .; then
    #     echo "Converting SVGs to PNGs in: $current_dir"
    #     if [ "$current_dir" = "$INPUT_DIR" ]; then
    #         # Process root directory
    #         python ../metamodule-plugin-sdk/scripts/SvgToPng.py --input "$current_dir" --output "$OUTPUT_DIR"
    #     else
    #         # Process subdirectory
    #         local output_subdir="$OUTPUT_DIR/$rel_path"
    #         python ../metamodule-plugin-sdk/scripts/SvgToPng.py --input "$current_dir" --output "$output_subdir"
    #     fi
    # fi
    
    # Process subdirectories
    find "$current_dir" -maxdepth 1 -type d | grep -v "^$current_dir$" | while read -r dir; do
        process_directory "$dir"
    done
}

# Start processing from the input directory
process_directory "$INPUT_DIR"

echo "Processing complete!" 