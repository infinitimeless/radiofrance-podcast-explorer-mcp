#!/usr/bin/env python3
"""
Test runner for Radio France MCP Server
Executes all tests in the tests directory
"""

import os
import sys
import importlib
import asyncio

def run_test_modules():
    """Find and run all test modules in the tests directory"""
    
    print("Radio France MCP Server - Test Runner")
    print("=" * 50)
    
    # Get the tests directory
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Get a list of all Python files in the tests directory
    test_files = [f[:-3] for f in os.listdir(tests_dir) 
                 if f.endswith('.py') and f != '__init__.py']
    
    if not test_files:
        print("No test files found in the tests directory.")
        return
    
    print(f"Found {len(test_files)} test modules: {', '.join(test_files)}")
    print("-" * 50)
    
    # Import and run each test module
    for test_file in test_files:
        try:
            # Import the module
            module_name = f"tests.{test_file}"
            module = importlib.import_module(module_name)
            
            # Check if the module has a run_tests function
            if hasattr(module, 'run_tests'):
                print(f"Running tests from {module_name}...")
                
                # Run the tests
                if asyncio.iscoroutinefunction(module.run_tests):
                    asyncio.run(module.run_tests())
                else:
                    module.run_tests()
                    
                print(f"Completed tests from {module_name}")
            else:
                print(f"Module {module_name} does not have a run_tests function.")
                
            print("-" * 50)
            
        except Exception as e:
            print(f"Error running tests from {module_name}: {str(e)}")
            print("-" * 50)
    
    print("All tests completed!")

if __name__ == "__main__":
    run_test_modules()
