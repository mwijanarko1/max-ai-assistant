#!/usr/bin/env python3
"""
Test script for improved navigation capabilities
"""

import os
from tools_module import ToolsModule

def test_navigation_capabilities():
    """Test the improved navigation capabilities"""
    print("Testing Improved Navigation Capabilities")
    print("=" * 45)
    
    tools = ToolsModule()
    
    # Test current directory
    print("1. Current directory:")
    result = tools.call_tool("list_directories", {"path": "."})
    print(result["result"])
    print()
    
    # Test root directory
    print("2. Root directory:")
    result = tools.call_tool("list_directories", {"path": "/"})
    print(result["result"])
    print()
    
    # Test home directory
    print("3. Home directory:")
    result = tools.call_tool("list_directories", {"path": "~"})
    print(result["result"])
    print()
    
    # Test navigation to home
    print("4. Navigate to home:")
    result = tools.call_tool("navigate_directory", {"path": "~"})
    print(result["result"])
    print()
    
    # Test finding directories
    print("5. Find Documents directory:")
    result = tools.call_tool("find_directory", {"directory_name": "Documents"})
    print(result["result"])
    print()
    
    # Test navigation to found directory
    print("6. Navigate to Documents:")
    result = tools.call_tool("navigate_directory", {"path": "~/Documents"})
    print(result["result"])
    print()
    
    # Test listing Documents
    print("7. List Documents directory:")
    result = tools.call_tool("list_directories", {"path": "."})
    print(result["result"])
    print()
    
    # Test navigation back to original directory
    print("8. Navigate back to original directory:")
    original_dir = os.path.abspath(".")
    result = tools.call_tool("navigate_directory", {"path": original_dir})
    print(result["result"])
    print()

def test_special_paths():
    """Test special path handling"""
    print("\nTesting Special Path Handling")
    print("=" * 35)
    
    tools = ToolsModule()
    
    test_paths = [
        "~",  # Home directory
        "home",  # Home directory alias
        "/",  # Root directory
        "root",  # Root directory alias
        "~/Desktop",  # Desktop
        "~/Documents",  # Documents
        "~/Downloads",  # Downloads
    ]
    
    for path in test_paths:
        print(f"\nTesting path: {path}")
        result = tools.call_tool("list_directories", {"path": path})
        print(result["result"])
        print("-" * 30)

def test_directory_finding():
    """Test directory finding capabilities"""
    print("\nTesting Directory Finding")
    print("=" * 30)
    
    tools = ToolsModule()
    
    # Common directories to find
    common_dirs = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]
    
    for dir_name in common_dirs:
        print(f"\nFinding '{dir_name}' directory:")
        result = tools.call_tool("find_directory", {"directory_name": dir_name})
        print(result["result"])

def main():
    """Main test function"""
    print("Max Navigation Capabilities Test")
    print("=" * 35)
    
    while True:
        print("\nChoose a test:")
        print("1. Test navigation capabilities")
        print("2. Test special paths")
        print("3. Test directory finding")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_navigation_capabilities()
        elif choice == "2":
            test_special_paths()
        elif choice == "3":
            test_directory_finding()
        elif choice == "4":
            test_navigation_capabilities()
            test_special_paths()
            test_directory_finding()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
