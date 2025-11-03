"""
Test providers with sample diagram files to diagnose issues

This script tests each provider using pre-existing sample diagram files
from the samplediagrams folder. This helps isolate whether failures are due to:
1. LLM generation issues
2. Provider rendering issues
3. Test data format problems
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from provider_test_helper import ProviderTestHelper


def load_sample_files():
    """Load all sample diagram files"""
    samples_dir = Path(__file__).parent / "samplediagrams"
    samples = {
        'd2': [],
        'mermaid': [],
        'c4': [],
        'plantuml': []
    }

    if not samples_dir.exists():
        print(f"Sample directory not found: {samples_dir}")
        return samples

    for file in samples_dir.glob("*.d2"):
        with open(file, 'r') as f:
            samples['d2'].append({
                'name': file.stem,
                'code': f.read().strip()
            })

    for file in samples_dir.glob("*.mmd"):
        with open(file, 'r') as f:
            samples['mermaid'].append({
                'name': file.stem,
                'code': f.read().strip()
            })

    for file in samples_dir.glob("*.puml"):
        with open(file, 'r') as f:
            samples['c4'].append({
                'name': file.stem,
                'code': f.read().strip()
            })

    return samples


def test_provider_with_samples(provider_id, diagram_type, samples):
    """Test a provider with sample diagrams"""

    print(f"\n{'='*80}")
    print(f"Testing {provider_id} with {len(samples)} sample {diagram_type} diagrams")
    print(f"{'='*80}\n")

    helper = ProviderTestHelper()
    passed = 0
    failed = 0
    results = []

    for sample in samples:
        print(f"Testing {sample['name']}...", end=" ")

        success, content, metadata = helper.render_with_provider(
            code=sample['code'],
            diagram_type=diagram_type,
            provider_id=provider_id,
            output_format='svg'
        )

        if success:
            passed += 1
            print("[PASS]")
            results.append({
                'name': sample['name'],
                'success': True,
                'content_length': len(content)
            })
        else:
            failed += 1
            print("[FAIL]")
            results.append({
                'name': sample['name'],
                'success': False,
                'error': content
            })

    total = len(samples)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n{'='*80}")
    print(f"Summary: {passed}/{total} passed ({success_rate:.1f}%)")
    print(f"{'='*80}\n")

    return {
        'provider_id': provider_id,
        'diagram_type': diagram_type,
        'total': total,
        'passed': passed,
        'failed': failed,
        'success_rate': success_rate,
        'results': results
    }


def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("PROVIDER DIAGNOSTICS - Testing with Sample Files")
    print("="*80)

    # Load samples
    samples = load_sample_files()

    print(f"\nLoaded samples:")
    print(f"  D2 samples: {len(samples['d2'])}")
    print(f"  Mermaid samples: {len(samples['mermaid'])}")
    print(f"  C4 samples: {len(samples['c4'])}")

    all_results = []

    # Test D2 providers
    if samples['d2']:
        all_results.append(test_provider_with_samples("d2v1", "d2", samples['d2']))
        all_results.append(test_provider_with_samples("krokid2", "d2", samples['d2']))

    # Test Mermaid providers
    if samples['mermaid']:
        all_results.append(test_provider_with_samples("mermaidv1", "mermaid", samples['mermaid']))
        all_results.append(test_provider_with_samples("krokimermaid", "mermaid", samples['mermaid']))

    # Test C4 provider (critical for investigation)
    if samples['c4']:
        result = test_provider_with_samples("krokic4", "c4", samples['c4'])
        all_results.append(result)

        # If C4 failed, try with PlantUML
        if result['success_rate'] == 0:
            print("\n⚠️  C4 PROVIDER FAILED - Trying PlantUML format...")
            # Note: C4 diagrams are in PlantUML format
            result_puml = test_provider_with_samples("krokiplantuml", "plantuml", samples['c4'])
            all_results.append(result_puml)

    # Save results
    summary_file = Path(__file__).parent / "sample_test_results.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'results': all_results
        }, f, indent=2)

    print(f"\nResults saved to: {summary_file}")

    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)

    for result in all_results:
        if result['success_rate'] == 100:
            status = "[OK]"
        elif result['success_rate'] > 0:
            status = "[PARTIAL]"
        else:
            status = "[FAIL]"
        print(f"{status} {result['provider_id']:20} ({result['diagram_type']:10}): {result['success_rate']:.1f}%")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
