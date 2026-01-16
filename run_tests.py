#!/usr/bin/env python
"""
Simple test runner script for the Health App.
Run this script to execute all tests.
"""
import sys
import subprocess

def main():
    """Run pytest with appropriate arguments."""
    # Run pytest with verbose output
    result = subprocess.run(
        ["pytest", "-v", "--tb=short"] + sys.argv[1:],
        cwd="."
    )
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
