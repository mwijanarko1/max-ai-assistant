#!/usr/bin/env python3
"""
Test script for current directory functionality
"""

import os
from tools_module import ToolsModule

def test_current_directory():
    """Test that Max can know the current directory"""
    print("Testing Current Directory Functionality")
    print("=" * 40)
    
    tools = ToolsModule()
    
    # Test current directory
    print("1. Getting current directory:")
    result = tools.call_tool("get_current_directory", {})
    print(f"Result: {result['result']}")
    print()
    
    # Test navigation and then check current directory
    print("2. Navigate to home and check current directory:")
    nav_result = tools.call_tool("navigate_directory", {"path": "~"})
    print(f"Navigation: {nav_result['result']}")
    print()
    
    # Check current directory after navigation
    print("3. Current directory after navigation:")
    result = tools.call_tool("get_current_directory", {})
    print(f"Result: {result['result']}")
    print()
    
    # Test listing directories (should show current directory info)
    print("4. List directories (should show current directory):")
    list_result = tools.call_tool("list_directories", {"path": "."})
    print(f"List result: {list_result['result']}")
    print()
    
    # Navigate back to original directory
    print("5. Navigate back to original directory:")
    original_dir = os.path.abspath(".")
    nav_result = tools.call_tool("navigate_directory", {"path": original_dir})
    print(f"Navigation: {nav_result['result']}")
    print()
    
    # Final current directory check
    print("6. Final current directory check:")
    result = tools.call_tool("get_current_directory", {})
    print(f"Result: {result['result']}")

def test_directory_awareness():
    """Test that Max is aware of current directory in responses"""
    print("\nTesting Directory Awareness")
    print("=" * 30)
    
    tools = ToolsModule()
    
    # Test different directory operations and their awareness
    operations = [
        ("Navigate to Desktop", "navigate_directory", {"path": "~/Desktop"}),
        ("List current directory", "list_directories", {"path": "."}),
        ("Get current directory", "get_current_directory", {}),
        ("Navigate to Documents", "navigate_directory", {"path": "~/Documents"}),
        ("List current directory", "list_directories", {"path": "."}),
        ("Navigate to root", "navigate_directory", {"path": "/"}),
        ("List root directory", "list_directories", {"path": "."}),
    ]
    
    for i, (description, tool_name, args) in enumerate(operations, 1):
        print(f"\n{i}. {description}:")
        result = tools.call_tool(tool_name, args)
        print(f"Result: {result['result']}")
        print("-" * 50)

def main():
    """Main test function"""
    print("Max Current Directory Test")
    print("=" * 25)
    
    while True:
        print("\nChoose a test:")
        print("1. Test current directory functionality")
        print("2. Test directory awareness")
        print("3. Run both tests")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_current_directory()
        elif choice == "2":
            test_directory_awareness()
        elif choice == "3":
            test_current_directory()
            test_directory_awareness()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
