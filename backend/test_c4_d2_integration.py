#!/usr/bin/env python3
"""
Integration test for C4 to D2 converter with rendering pipeline
Tests the complete flow from C4 input to D2 output
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.c4_to_d2 import convert_c4_to_d2
from mvp_diagram_generator.diagram_validators import is_valid_c4_diagram, is_valid_d2_diagram

def test_c4_to_d2_integration():
    """Test C4 to D2 conversion with validation"""
    print("=" * 60)
    print("Integration Test: C4 to D2 with Rendering Pipeline")
    print("=" * 60)
    
    # Sample C4 diagram
    c4_diagram = """C4Context
title Payment Processing System

Person(customer, "Customer", "Makes payments")
System_Ext(bank, "Bank API", "External banking system")

System_Boundary(payment_system, "Payment System") {
    Container(api, "API Gateway", "REST API", "Spring Boot")
    ContainerDb(db, "Database", "Transaction storage", "PostgreSQL")
}

Rel(customer, api, "Submits payment", "HTTPS")
Rel(api, db, "Stores transaction", "JDBC")
Rel(api, bank, "Validates payment", "HTTPS")
"""
    
    print("1. Validating C4 input...")
    is_valid_c4 = is_valid_c4_diagram(c4_diagram)
    print(f"   C4 validation: {'✅ PASSED' if is_valid_c4 else '❌ FAILED'}")
    
    if not is_valid_c4:
        print("   ERROR: Invalid C4 diagram")
        return False
    
    print("\n2. Converting C4 to D2...")
    d2_diagram = convert_c4_to_d2(c4_diagram)
    print(f"   Conversion completed: {len(d2_diagram)} characters")
    
    print("\n3. Validating D2 output...")
    is_valid_d2 = is_valid_d2_diagram(d2_diagram)
    print(f"   D2 validation: {'✅ PASSED' if is_valid_d2 else '❌ FAILED'}")
    
    print("\n4. Checking conversion quality...")
    
    # Check for key elements
    checks = [
        ("Direction", "direction: down" in d2_diagram),
        ("Title", "# Payment Processing System" in d2_diagram),
        ("Person entity", "customer: {" in d2_diagram),
        ("Person shape", "shape: person" in d2_diagram),
        ("System entity", "bank: {" in d2_diagram),
        ("Boundary", "payment_system: {" in d2_diagram),
        ("Container", "api: {" in d2_diagram),
        ("Database", "db: {" in d2_diagram),
        ("Database shape", "shape: cylinder" in d2_diagram),
        ("Relationship", "customer -> api:" in d2_diagram),
        ("Technology", "[HTTPS]" in d2_diagram),
        ("Tooltip", "tooltip:" in d2_diagram),
        ("Style", "style:" in d2_diagram)
    ]
    
    passed_checks = 0
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if result:
            passed_checks += 1
    
    print(f"\n   Checks passed: {passed_checks}/{len(checks)}")
    
    print("\n5. Generated D2 diagram:")
    print("-" * 40)
    print(d2_diagram)
    
    # Overall result
    all_checks_passed = passed_checks == len(checks) and is_valid_d2
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULT")
    print("=" * 60)
    
    if all_checks_passed:
        print("✅ SUCCESS: C4 to D2 integration works correctly")
        print("   The converter produces valid D2 that can be rendered")
        return True
    else:
        print("❌ FAILURE: C4 to D2 integration has issues")
        print("   Please check the conversion implementation")
        return False

def test_edge_cases():
    """Test edge cases in the integration"""
    print("\n" + "=" * 60)
    print("Edge Case Tests")
    print("=" * 60)
    
    edge_cases = [
        ("Empty input", ""),
        ("Only comments", "# This is a comment\n# Another comment"),
        ("Invalid syntax", "This is not C4 syntax"),
        ("Minimal C4", "C4Context\nPerson(u, \"User\")\nSystem(s, \"System\")\nRel(u, s, \"Uses\")")
    ]
    
    passed = 0
    for name, c4_code in edge_cases:
        print(f"\nTesting: {name}")
        try:
            d2_code = convert_c4_to_d2(c4_code)
            print(f"   Result: {len(d2_code)} characters")
            
            # Validate D2 if not empty
            if d2_code:
                is_valid = is_valid_d2_diagram(d2_code)
                print(f"   Valid D2: {'✅' if is_valid else '❌'}")
            else:
                print("   Empty output (expected for some cases)")
            
            passed += 1
            print("   ✅ Handled without errors")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\nEdge cases passed: {passed}/{len(edge_cases)}")
    return passed == len(edge_cases)

def main():
    """Run all integration tests"""
    print("🔗 Running C4 to D2 Integration Tests")
    print("=" * 60)
    
    tests = [
        test_c4_to_d2_integration,
        test_edge_cases
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("The C4 to D2 converter is ready for production use.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())