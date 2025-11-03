"""
Render all sample diagram files to SVG using the provider system

This script renders each sample diagram file using the appropriate provider
and saves the SVG output alongside the original file.

Files processed:
- *.d2 files → rendered with d2v1 provider
- *.mmd files → rendered with mermaidv1 provider
- *.puml files → rendered with krokiplantuml provider
- *.dsl files → rendered with krokistructurizr provider
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from provider_test_helper import ProviderTestHelper


def render_samples():
    """Render all sample diagram files to SVG"""

    samples_dir = Path(__file__).parent / "samplediagrams"

    if not samples_dir.exists():
        print(f"Error: Sample directory not found: {samples_dir}")
        return

    helper = ProviderTestHelper()

    # Diagram type to provider mapping
    mappings = {
        '.d2': ('d2v1', 'd2'),
        '.mmd': ('mermaidv1', 'mermaid'),
        '.puml': ('krokiplantuml', 'plantuml'),
        '.dsl': ('krokistructurizr', 'structurizr')
    }

    print("\n" + "="*80)
    print("RENDERING SAMPLE DIAGRAMS TO SVG")
    print("="*80 + "\n")

    results = {
        'd2': {'total': 0, 'success': 0, 'failed': 0},
        'mermaid': {'total': 0, 'success': 0, 'failed': 0},
        'plantuml': {'total': 0, 'success': 0, 'failed': 0},
        'structurizr': {'total': 0, 'success': 0, 'failed': 0}
    }

    # Process each file type
    for ext, (provider_id, diagram_type) in mappings.items():
        print(f"\nProcessing {ext} files ({provider_id} provider):")
        print("-" * 80)

        files = sorted(samples_dir.glob(f"*{ext}"))

        if not files:
            print(f"  No files found with extension {ext}")
            continue

        for file_path in files:
            try:
                # Read diagram code
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read().strip()

                if not code:
                    print(f"  {file_path.name:40} [SKIP] Empty file")
                    continue

                print(f"  {file_path.name:40}", end=" ")

                # Render diagram
                success, content, metadata = helper.render_with_provider(
                    code=code,
                    diagram_type=diagram_type,
                    provider_id=provider_id,
                    output_format='svg'
                )

                if success:
                    # Save SVG file with same name
                    svg_path = file_path.with_suffix(file_path.suffix + '.svg')

                    with open(svg_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"[OK] ({len(content)} bytes)")
                    results[diagram_type]['success'] += 1
                else:
                    print(f"[FAIL] {content}")
                    results[diagram_type]['failed'] += 1

                results[diagram_type]['total'] += 1

            except Exception as e:
                print(f"  {file_path.name:40} [ERROR] {str(e)}")
                results[diagram_type]['failed'] += 1
                results[diagram_type]['total'] += 1

    # Summary
    print("\n" + "="*80)
    print("RENDERING SUMMARY")
    print("="*80)

    total_files = sum(r['total'] for r in results.values())
    total_success = sum(r['success'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())

    for diagram_type, result in results.items():
        if result['total'] > 0:
            rate = (result['success'] / result['total'] * 100)
            status = "OK" if rate == 100 else "PARTIAL" if rate > 0 else "FAIL"
            print(f"  {diagram_type:15}: {result['success']:2}/{result['total']:2} ({rate:5.1f}%) [{status}]")

    print("-" * 80)
    if total_files > 0:
        overall_rate = (total_success / total_files * 100)
        print(f"  {'TOTAL':15}: {total_success:2}/{total_files:2} ({overall_rate:5.1f}%)")

    print("="*80 + "\n")

    if total_success > 0:
        print(f"Successfully rendered {total_success} diagram(s)")
        print("SVG files saved alongside original files in samplediagrams/")

    if total_failed > 0:
        print(f"Failed to render {total_failed} diagram(s)")


if __name__ == "__main__":
    render_samples()
