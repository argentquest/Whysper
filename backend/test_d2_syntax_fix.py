"""
Test script to verify D2 syntax fixes work correctly
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.renderer_v2 import render_diagram

# Test the problematic D2 code from the history file
PROBLEMATIC_D2_CODE = """direction: right

// Define the components (Numbers and Operators)
One_A: {
    shape: circle
    label: "1"
    style: {
        fill: "#a8dadc"
    }
}

Plus: {
    shape: diamond
    label: "+"
    style: {
        fill: "#457b9d"
        font-color: white
    }
}

One_B: {
    shape: circle
    label: "1"
    style: {
        fill: "#a8dadc"
    }
}

Equals: {
    shape: octagon
    label: "="
    style: {
        fill: "#e63946"
        font-color: white
    }
}

Two: {
    shape: double_circle
    label: "2"
    style: {
        fill: "#f1faee"
        stroke: "#e63946"
        stroke-width: 2
    }
}

// Define the flow of the calculation
One_A -> Plus: Input
One_B -> Plus: Input

Plus -> Equals: Result (2)

Equals -> Two: Final Output"""

# Test the corrected D2 code
CORRECTED_D2_CODE = """direction: right

# Define the components (Numbers and Operators)
One_A: "1" {
  shape: circle
  style.fill: "#a8dadc"
}

Plus: "+" {
  shape: diamond
  style.fill: "#457b9d"
}

One_B: "1" {
  shape: circle
  style.fill: "#a8dadc"
}

Equals: "=" {
  shape: octagon
  style.fill: "#e63946"
}

Two: "2" {
  shape: rectangle
  style.fill: "#f1faee"
  style.stroke: "#e63946"
  style.stroke-width: 2
}

# Define the flow of the calculation
One_A -> Plus: "Input"
One_B -> Plus: "Input"
Plus -> Equals: "Result (2)"
Equals -> Two: "Final Output"
"""

async def test_d2_rendering():
    """Test both problematic and corrected D2 code"""
    
    print("🧪 Testing D2 Diagram Rendering Fixes")
    print("=" * 50)
    
    # Test 1: Problematic code (should fail or be corrected)
    print("\n1️⃣ Testing problematic D2 code...")
    try:
        result1 = await render_diagram(PROBLEMATIC_D2_CODE, "d2", "svg")
        print("✅ Problematic code rendered successfully!")
        print(f"   SVG length: {len(result1)} characters")
    except Exception as e:
        print(f"❌ Problematic code failed: {e}")
    
    # Test 2: Corrected code (should work)
    print("\n2️⃣ Testing corrected D2 code...")
    try:
        result2 = await render_diagram(CORRECTED_D2_CODE, "d2", "svg")
        print("✅ Corrected code rendered successfully!")
        print(f"   SVG length: {len(result2)} characters")
        
        # Save the successful result to a file for verification
        with open("test_d2_output.svg", "w") as f:
            f.write(result2)
        print("   📄 Saved output to test_d2_output.svg")
        
    except Exception as e:
        print(f"❌ Corrected code failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_d2_rendering())