"""
Script to generate SVG files for all D2 files in the SampleD2 folder
"""

from app.services.d2_render_service import get_d2_service
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def generate_svgs_for_sample_d2():
    # Initialize D2 rendering service for converting D2 files to SVG
    d2_service = get_d2_service()

    # Define the source directory containing D2 diagram files
    source_dir = Path("backend/tests/Diagrams/SampleD2")

    # Validate that the source directory exists
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return

    # Find all D2 files in the directory using file extension matching
    d2_files = list(source_dir.glob("*.d2"))

    # Check if any D2 files were found to process
    if not d2_files:
        print(f"No D2 files found in {source_dir}")
        return

    # Log the number of files that will be processed
    print(f"Found {len(d2_files)} D2 files to process")

    # Initialize counters for tracking processing results
    success_count = 0
    error_count = 0

    # Iterate through each D2 file to convert to SVG
    for d2_file in d2_files:
        print(f"\nProcessing: {d2_file.name}")

        try:
            # Read the contents of the D2 file
            with open(d2_file, "r", encoding="utf-8") as f:
                d2_code = f.read()

            # Generate the output SVG path with the same filename
            svg_path = d2_file.with_suffix(".svg")

            # Use D2 service to render the diagram code to SVG
            success, error_msg, svg_content = d2_service.render_d2_to_svg(d2_code, output_dir=str(d2_file.parent))

            # Check if SVG was successfully generated
            if success and svg_content:
                # Write the SVG content to a file
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)

                # Log successful conversion and increment success counter
                print(f"[SUCCESS] Generated: {svg_path.name}")
                success_count += 1
            else:
                # Log rendering failure and increment error counter
                print(f"[FAILED] Render {d2_file.name}: {error_msg}")
                error_count += 1

        except Exception as e:
            # Catch and log any unexpected errors during processing
            print(f"[ERROR] Processing {d2_file.name}: {str(e)}")
            error_count += 1

    # Print summary of processing results
    print("\nSummary:")
    print(f"Successfully processed: {success_count} files")
    print(f"Failed: {error_count} files")
    print(f"Total: {len(d2_files)} files")


if __name__ == "__main__":
    generate_svgs_for_sample_d2()
