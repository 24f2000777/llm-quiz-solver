#!/usr/bin/env python3
"""
Quick test script to verify the quiz solver setup.
Run this after setup to ensure everything works.
"""
import sys
import subprocess
import requests
import time
from pathlib import Path

def check_python_version():
    """Check if Python 3.12+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print(f"❌ Python 3.12+ required (found {version.major}.{version.minor})")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    with open(env_file) as f:
        content = f.read()
    
    required = ["EMAIL=", "SECRET=", "GOOGLE_API_KEY="]
    missing = [var for var in required if var not in content or content.count(var + "your") > 0]
    
    if missing:
        print(f"❌ .env file missing or has default values for: {missing}")
        return False
    
    print("✅ .env file configured")
    return True

def check_dependencies():
    """Check if key dependencies are installed."""
    try:
        import fastapi
        import langchain
        import langgraph
        import playwright
        print("✅ Dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -e .")
        return False

def check_playwright():
    """Check if Playwright browsers are installed."""
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True
        )
        if "is already installed" in result.stdout or result.returncode == 0:
            print("✅ Playwright chromium installed")
            return True
        else:
            print("❌ Playwright chromium not installed")
            print("   Run: playwright install chromium")
            return False
    except FileNotFoundError:
        print("❌ Playwright not found")
        print("   Run: pip install playwright")
        return False

def test_server_start():
    """Test if server can start."""
    print("\n🧪 Starting server for 5 seconds...")
    try:
        # Start server in background
        proc = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:7860/healthz", timeout=2)
            if response.status_code == 200:
                print("✅ Server started successfully")
                data = response.json()
                print(f"   Uptime: {data['uptime_seconds']}s")
                result = True
            else:
                print(f"❌ Server returned {response.status_code}")
                result = False
        except requests.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            result = False
        
        # Cleanup
        proc.terminate()
        proc.wait(timeout=5)
        
        return result
        
    except Exception as e:
        print(f"❌ Server start failed: {e}")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("🔍 LLM Quiz Solver - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Playwright", check_playwright),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...")
        result = check_func()
        results.append(result)
        print()
    
    # Optional server test
    if all(results):
        print("All basic checks passed! Testing server...")
        server_ok = test_server_start()
        results.append(server_ok)
    
    print("=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED")
        print()
        print("Next steps:")
        print("1. Start server: python main.py")
        print("2. Test endpoint: See QUICKSTART.md for curl command")
        print("3. Deploy to HuggingFace Spaces")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Fix the issues above and run this script again.")
    print("=" * 60)

if __name__ == "__main__":
    main()
