#!/usr/bin/env python3
"""
Test File Creation System for Max Assistant
"""

from file_creation_handler import FileCreationHandler
from tools_module import ToolsModule

def test_file_creation_system():
    print("Testing File Creation System")
    print("=" * 40)
    
    # Initialize handlers
    file_handler = FileCreationHandler()
    tools = ToolsModule()
    
    # Test 1: File creation initiation
    print("\n1. Testing file creation initiation:")
    result = file_handler.start_file_creation("I want to create a file")
    print(result)
    
    # Test 2: Parsing file creation requests
    print("\n2. Testing file creation request parsing:")
    test_requests = [
        "Create a file called notes as txt in docs",
        "Make a file named project as md in current directory",
        "Create file test as py in src"
    ]
    
    for request in test_requests:
        parsed = file_handler.parse_file_creation_request(request)
        print(f"Input: {request}")
        print(f"Parsed: {parsed}")
        print()
    
    # Test 3: Confirmation messages
    print("\n3. Testing confirmation messages:")
    confirm_msg = file_handler.confirm_file_creation("notes", "txt", "docs")
    print(confirm_msg)
    print()
    
    # Test 4: Directory listing
    print("\n4. Testing directory listing:")
    result = tools.call_tool("list_directories", {"path": "."})
    print(f"Directory listing result: {result}")
    print()
    
    # Test 5: File creation execution
    print("\n5. Testing file creation execution:")
    result = file_handler.execute_file_creation("test_notes", "txt", ".")
    print(f"File creation result: {result}")
    print()
    
    # Test 6: Directory navigation
    print("\n6. Testing directory navigation:")
    result = tools.call_tool("navigate_directory", {"path": "docs"})
    print(f"Navigation result: {result}")
    
    # List contents of docs directory
    result = tools.call_tool("list_directories", {"path": "docs"})
    print(f"Docs directory contents: {result}")

if __name__ == "__main__":
    test_file_creation_system()
