"""
Script to generate SVG files for all D2 files in the SampleD2 folder
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.d2_render_service import get_d2_service


def generate_svgs_for_sample_d2():
    """Generate SVG files for all D2 files in the SampleD2 folder"""
    
    # Get the D2 service
    d2_service = get_d2_service()
    
    # Define the source directory with D2 files
    source_dir = Path("backend/tests/Diagrams/SampleD2")
    
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return
    
    # Get all D2 files in the directory
    d2_files = list(source_dir.glob("*.d2"))
    
    if not d2_files:
        print(f"No D2 files found in {source_dir}")
        return
    
    print(f"Found {len(d2_files)} D2 files to process")
    
    success_count = 0
    error_count = 0
    
    # Process each D2 file
    for d2_file in d2_files:
        print(f"\nProcessing: {d2_file.name}")
        
        try:
            # Read the D2 code
            with open(d2_file, 'r', encoding='utf-8') as f:
                d2_code = f.read()
            
            # Generate SVG path (same directory, same name but .svg extension)
            svg_path = d2_file.with_suffix('.svg')
            
            # Render the D2 code to SVG
            success, error_msg, svg_content = d2_service.render_d2_to_svg(
                d2_code, 
                output_dir=str(d2_file.parent)
            )
            
            if success and svg_content:
                # Save the SVG content to file
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                print(f"[SUCCESS] Generated: {svg_path.name}")
                success_count += 1
            else:
                print(f"[FAILED] Render {d2_file.name}: {error_msg}")
                error_count += 1
                
        except Exception as e:
            print(f"[ERROR] Processing {d2_file.name}: {str(e)}")
            error_count += 1
    
    print("\nSummary:")
    print(f"Successfully processed: {success_count} files")
    print(f"Failed: {error_count} files")
    print(f"Total: {len(d2_files)} files")


if __name__ == "__main__":
    generate_svgs_for_sample_d2()