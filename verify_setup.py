#!/usr/bin/env python3
"""
Feature.fm API Test Suite - Quick Verification
"""

import sys
import importlib.util


def check_module(module_name: str, display_name: str) -> bool:
    """Check if a module is available."""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f"✓ {display_name} module available")
        return True
    else:
        print(f"✗ {display_name} module not found")
        return False


def main() -> None:
    """Main verification function."""
    print("Verifying Python environment...")

    modules_to_check = [
        ("requests", "requests"),
        ("jwt", "PyJWT"),
        ("colorama", "colorama")
    ]

    all_available = True
    for module_name, display_name in modules_to_check:
        if not check_module(module_name, display_name):
            all_available = False

    if not all_available:
        sys.exit(1)

    print("\n✓ All dependencies verified!")
    print("Ready to run Feature.fm API tests")


if __name__ == "__main__":
    main()
