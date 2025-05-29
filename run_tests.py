#!/usr/bin/env python3
"""
Test runner for GitHub MCP Agent

Run all tests with proper setup and cleanup.
"""
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests"""
    
    print("🧪 Running GitHub MCP Agent Tests")
    print("=" * 50)
    
    tests_dir = Path(__file__).parent / "tests"
    
    try:
        # Run tests using uv run to ensure proper environment
        result = subprocess.run([
            "uv", "run", "python", "-m", "pytest",
            str(tests_dir),
            "-v",
            "--tb=short"
        ], check=False)
        
        exit_code = result.returncode
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {exit_code})")
        
        return exit_code == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
