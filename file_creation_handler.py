#!/usr/bin/env python3
"""
File Creation Handler for Max Assistant
Handles interactive file creation with user confirmation
"""

import os
import re
from typing import Dict, Any, Optional

class FileCreationHandler:
    """Handles interactive file creation with user confirmation"""
    
    def __init__(self):
        self.pending_creation = None
        self.desktop_path = self._get_desktop_path()
    
    def _get_desktop_path(self) -> str:
        """Get the desktop directory path"""
        try:
            # Try to get desktop path
            if os.name == 'nt':  # Windows
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            else:  # macOS and Linux
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # If desktop doesn't exist, fall back to home directory
            if not os.path.exists(desktop):
                desktop = os.path.expanduser("~")
            
            return desktop
        except Exception:
            # Fallback to current directory
            return os.getcwd()
    
    def start_file_creation(self, user_input: str) -> str:
        """Start the file creation process"""
        # Check if user wants to create a file
        if any(phrase in user_input.lower() for phrase in ["create file", "make file", "new file", "create a file", "make a text file"]):
            return self._initiate_file_creation()
        return None
    
    def _initiate_file_creation(self) -> str:
        """Start the file creation process"""
        desktop_name = os.path.basename(self.desktop_path)
        
        return f"""I'll help you create a file. 

Please tell me:
1. What would you like to name the file?
2. What type of file should it be? (txt, md, docx, py, etc.)

The file will be created on your {desktop_name} by default.

For example, you could say:
- "Create a file called 'notes' as a text file"
- "Make a file named 'project' as markdown"
- "Create a file called 'todo' as txt"

What would you like to name your file?"""
    
    def parse_file_creation_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Parse file creation request from user input"""
        # Patterns to match file creation requests
        patterns = [
            r"create.*file.*called\s+['\"]?(\w+)['\"]?\s+as\s+(\w+)",
            r"make.*file.*named\s+['\"]?(\w+)['\"]?\s+as\s+(\w+)",
            r"create.*file.*(\w+)\s+(\w+)",
            r"file.*(\w+)\s+(\w+)",
            r"(\w+)\s+(\w+)\s+file",  # "notes txt file"
            r"(\w+)\s+file\s+(\w+)"   # "notes file txt"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                filename = match.group(1)
                file_type = match.group(2)
                
                return {
                    "filename": filename,
                    "file_type": file_type,
                    "directory": self.desktop_path
                }
        
        # If no pattern matches, try to extract just a filename
        # Look for words that could be filenames
        words = user_input.lower().split()
        for word in words:
            if word.isalnum() and len(word) > 1:
                return {
                    "filename": word,
                    "file_type": "txt",  # Default to text file
                    "directory": self.desktop_path
                }
        
        return None
    
    def confirm_file_creation(self, filename: str, file_type: str, directory: str = None) -> str:
        """Confirm file creation with user"""
        if directory is None:
            directory = self.desktop_path
            
        # Ensure file type has dot
        if not file_type.startswith('.'):
            file_type = '.' + file_type
        
        full_filename = filename + file_type
        full_path = os.path.join(directory, full_filename)
        
        return f"""I'm about to create a file with these details:

📁 Directory: {os.path.basename(directory)}
📄 Filename: {full_filename}
📍 Full path: {full_path}

Please confirm by saying "yes" or "confirm" to create this file, or "no" to cancel."""
    
    def execute_file_creation(self, filename: str, file_type: str, directory: str = None) -> str:
        """Actually create the file"""
        try:
            if directory is None:
                directory = self.desktop_path
            
            # Security: Only allow operations in desktop or current directory
            current_dir = os.getcwd()
            requested_dir = os.path.abspath(directory)
            
            # Ensure the requested directory is safe (desktop or current directory)
            if not (requested_dir.startswith(current_dir) or requested_dir == self.desktop_path):
                return "Error: Access denied - can only create files in desktop or current directory"
            
            # Create the full file path
            if not file_type.startswith('.'):
                file_type = '.' + file_type
            
            full_filename = filename + file_type
            file_path = os.path.join(requested_dir, full_filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                return f"Error: File '{full_filename}' already exists in {os.path.basename(directory)}"
            
            # Create the file with some basic content
            with open(file_path, 'w') as f:
                f.write(f"# {filename}\n\nCreated by Max Assistant\n\n")
            
            return f"✅ Successfully created file '{full_filename}' in {os.path.basename(directory)}"
            
        except PermissionError:
            return f"Error: Permission denied for creating file in '{os.path.basename(directory)}'"
        except Exception as e:
            return f"Error: {str(e)}"

def test_file_creation():
    """Test the file creation handler"""
    handler = FileCreationHandler()
    
    # Test file creation initiation
    print("Testing file creation initiation:")
    result = handler.start_file_creation("I want to create a file")
    print(result)
    print()
    
    # Test parsing file creation request
    print("Testing file creation parsing:")
    test_inputs = [
        "Create a file called notes as txt",
        "Make a file named project as md",
        "Create file test as py",
        "notes txt file",
        "todo file"
    ]
    
    for test_input in test_inputs:
        parsed = handler.parse_file_creation_request(test_input)
        print(f"Input: {test_input}")
        print(f"Parsed: {parsed}")
        print()
    
    # Test confirmation message
    print("Testing confirmation message:")
    confirm_msg = handler.confirm_file_creation("notes", "txt")
    print(confirm_msg)

if __name__ == "__main__":
    test_file_creation()
