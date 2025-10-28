#!/usr/bin/env python3
"""
Test runner script for the FastAPI application.
Provides various testing options and configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n🔍 {description}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run FastAPI tests")
    parser.add_argument("--coverage", action="store_true", 
                       help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--fast", action="store_true",
                       help="Skip slow tests")
    parser.add_argument("--file", "-f", type=str,
                       help="Run specific test file")
    parser.add_argument("--test", "-t", type=str,
                       help="Run specific test function")
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.extend(["-v", "-s"])
    
    # Skip slow tests if requested
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    # Specific file or test
    if args.file:
        pytest_cmd.append(f"tests/{args.file}")
    elif args.test:
        pytest_cmd.extend(["-k", args.test])
    
    # Coverage options
    if args.coverage:
        # Install coverage if not present
        print("📦 Installing coverage dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-cov"], 
                      capture_output=True)
        
        pytest_cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Run the tests
    success = run_command(pytest_cmd, "Running FastAPI tests")
    
    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())