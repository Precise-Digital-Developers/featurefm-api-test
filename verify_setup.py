#!/usr/bin/env python3
"""
Feature.fm API Test Suite - Quick Verification
"""

import sys
print("Verifying Python environment...")

try:
    import requests
    print("✓ requests module available")
except ImportError:
    print("✗ requests module not found")
    sys.exit(1)

try:
    import jwt
    print("✓ PyJWT module available")
except ImportError:
    print("✗ PyJWT module not found")
    sys.exit(1)

try:
    import colorama
    print("✓ colorama module available")
except ImportError:
    print("✗ colorama module not found")
    sys.exit(1)

print("\n✓ All dependencies verified!")
print("Ready to run Feature.fm API tests")
