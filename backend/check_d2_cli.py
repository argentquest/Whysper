"""
Check if D2 CLI is installed and provide installation instructions
"""

import subprocess
import sys
import os

def check_d2_cli():
    """Check if D2 CLI is available"""
    try:
        result = subprocess.run(
            ['d2', '--version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        print("✅ D2 CLI is installed!")
        print(f"Version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ D2 CLI is NOT installed")
        return False

def main():
    """Main check function"""
    print("D2 CLI Installation Check")
    print("=" * 40)
    
    if not check_d2_cli():
        print("\n" + "=" * 40)
        print("INSTALLATION INSTRUCTIONS")
        print("=" * 40)
        
        print("\n📥 To install D2 CLI, choose one of the following methods:")
        
        print("\n1️⃣  Download from official website:")
        print("   https://d2lang.com/")
        
        print("\n2️⃣  Using package managers:")
        print("   • macOS: brew install d2")
        print("   • Windows: scoop install d2")
        print("   • Linux: See installation guide at d2lang.com")
        
        print("\n3️⃣  Using Go (if you have Go installed):")
        print("   go install oss.terrastruct.com/d2@latest")
        
        print("\n4️⃣  Using Docker:")
        print("   docker run --rm -it -v $(pwd):/data terrastruct/d2:latest /data/diagram.d2")
        
        print("\n" + "=" * 40)
        print("WHY INSTALL D2 CLI?")
        print("=" * 40)
        print("\nInstalling D2 CLI provides:")
        print("• 100% accurate D2 syntax validation")
        print("• Automatic fixing of syntax errors")
        print("• SVG/PNG diagram generation")
        print("• Better error messages for debugging")
        
        print("\nWithout D2 CLI, the system will:")
        print("• Use pattern-based validation (less accurate)")
        print("• Attempt to fix common syntax issues")
        print("• Have limited error reporting")
        
        print("\n" + "=" * 40)
        return False
    else:
        print("\n✅ You can run all 25 D2 tests with full validation!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
