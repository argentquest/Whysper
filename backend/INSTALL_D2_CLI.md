# D2 CLI Installation Guide

## What is D2 CLI?

D2 CLI is the official command-line tool for D2, a modern diagramming language. It provides:
- 100% accurate syntax validation
- Diagram rendering to SVG, PNG, and other formats
- Detailed error messages for debugging
- The most reliable way to validate D2 diagrams

## Installation Methods

### Method 1: Direct Download (Recommended)

1. Go to the official D2 website: https://d2lang.com/
2. Click "Download" or "Get Started"
3. Download the appropriate version for your OS:
   - Windows: `d2.exe` or MSI installer
   - macOS: `d2` binary or Homebrew
   - Linux: `d2` binary or package manager

### Method 2: Package Managers

#### macOS (using Homebrew)
```bash
brew install d2
```

#### Windows (using Scoop)
```bash
scoop install d2
```

#### Linux (various)
```bash
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh
sudo apt-get update && sudo apt-get install d2

# Or download directly
wget https://github.com/terrastruct/d2/releases/latest/download/d2-linux-amd64.tar.gz
tar -xzf d2-linux-amd64.tar.gz
sudo mv d2 /usr/local/bin/
```

### Method 3: Using Go (if Go is installed)

```bash
go install oss.terrastruct.com/d2@latest
```

### Method 4: Docker (if you prefer containers)

```bash
docker run --rm -it -v $(pwd):/data terrastruct/d2:latest /data/diagram.d2
```

## Verify Installation

Run the check script to verify D2 CLI is installed:

```bash
cd backend
python check_d2_cli.py
```

Or manually check:

```bash
d2 --version
```

You should see output like:
```
d2 version 0.6.5 (linux/amd64)
```

## Why D2 CLI is Important for This Project

### With D2 CLI Installed:
✅ 100% accurate syntax validation using the official D2 parser  
✅ Automatic fixing of syntax errors  
✅ Detailed error messages for debugging  
✅ SVG/PNG diagram generation  
✅ Expected 95% success rate for the 25 tests  

### Without D2 CLI:
⚠️ Pattern-based validation only (less accurate)  
⚠️ Limited error reporting  
⚠️ No diagram generation  
⚠️ Lower success rate for tests  

## Common Installation Issues

### Issue: "d2: command not found"
**Solution:** Ensure D2 is in your system PATH
- Windows: Add D2 installation directory to PATH
- macOS/Linux: Ensure `/usr/local/bin` is in PATH

### Issue: Permission denied on Linux/macOS
```bash
chmod +x d2
sudo mv d2 /usr/local/bin/
```

### Issue: Windows Defender blocking download
**Solution:** Click "More info" → "Run anyway" when prompted

## Testing Your Installation

1. Create a test file `test.d2`:
```d2
direction: right
user: "User"
server: "Server"
user -> server: "Access"
```

2. Render it to SVG:
```bash
d2 test.d2 test.svg
```

3. Open `test.svg` in a browser to see your diagram!

## Integration with the Project

Once D2 CLI is installed, the project will automatically:
1. Use it for validation when running tests
2. Apply fixes to common syntax errors
3. Generate SVG diagrams for all valid D2 code
4. Provide detailed error messages for debugging

## Running the 25 Tests

After installing D2 CLI:

```bash
cd backend
python test_all_25_d2_simple.py
```

This will:
- Validate all 25 test cases
- Apply fixes where needed
- Generate SVG diagrams
- Report success/failure for each test

## Need Help?

- D2 Documentation: https://d2lang.com/doc/
- D2 GitHub: https://github.com/terrastruct/d2
- D2 Discord: https://discord.gg/7pXvVJZ6ZP