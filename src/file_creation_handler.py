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
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        # Remove emoji characters (Unicode emoji ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()
    
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
        input_lower = user_input.lower()
        
        # Enhanced file creation detection patterns
        file_creation_patterns = [
            "create file", "make file", "new file", "create a file", "make a text file",
            "make a python file", "create a python file", "make a txt file", "create a txt file",
            "make a markdown file", "create a markdown file", "make a json file", "create a json file",
            "make a pdf file", "create a pdf file", "make a py file", "create a py file",
            "make a md file", "create a md file", "make a js file", "create a js file",
            "make a html file", "create a html file", "make a css file", "create a css file"
        ]
        
        # Check if user wants to create a file
        if any(phrase in input_lower for phrase in file_creation_patterns):
            # Try to parse the command immediately
            parsed = self.parse_file_creation_request(user_input)
            if parsed:
                # If we can parse it, create the file directly
                return self.execute_file_creation(parsed["filename"], parsed["file_type"], parsed["directory"])
            else:
                # If we can't parse it, ask for more details
                return self._initiate_file_creation()
        return None
    
    def _initiate_file_creation(self) -> str:
        """Start the file creation process"""
        desktop_name = os.path.basename(self.desktop_path)
        
        return f"""I'll help you create a file. What would you like to name it? (It will be created on your {desktop_name} as a text file by default.)"""
    
    def parse_file_creation_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Parse file creation request from user input"""
        input_lower = user_input.lower()
        
        # Special handling for "make a python file" and "create a python file" without specific names
        if "python" in input_lower and ("make" in input_lower or "create" in input_lower) and "file" in input_lower:
            # Check if there's a specific name mentioned
            if "called" in input_lower:
                # Extract name after "called"
                called_match = re.search(r"called\s+(\w+)", input_lower)
                if called_match:
                    filename = called_match.group(1)
                else:
                    filename = "main"  # Default name for Python files
            else:
                filename = "main"  # Default name for Python files
            return {
                "filename": filename,
                "file_type": "py",
                "directory": self.desktop_path
            }
        
        # Special handling for "make a text file" and "create a text file" without specific names
        if ("text" in input_lower or "txt" in input_lower) and ("make" in input_lower or "create" in input_lower) and "file" in input_lower:
            # Check if there's a specific name mentioned
            if "called" in input_lower:
                # Extract name after "called"
                called_match = re.search(r"called\s+(\w+)", input_lower)
                if called_match:
                    filename = called_match.group(1)
                else:
                    filename = "notes"  # Default name for text files
            else:
                filename = "notes"  # Default name for text files
            return {
                "filename": filename,
                "file_type": "txt",
                "directory": self.desktop_path
            }
        
        # Special handling for "make a markdown file" and "create a markdown file" without specific names
        if ("markdown" in input_lower or "md" in input_lower) and ("make" in input_lower or "create" in input_lower) and "file" in input_lower:
            # Check if there's a specific name mentioned
            if "called" in input_lower:
                # Extract name after "called"
                called_match = re.search(r"called\s+(\w+)", input_lower)
                if called_match:
                    filename = called_match.group(1)
                else:
                    filename = "readme"  # Default name for markdown files
            else:
                filename = "readme"  # Default name for markdown files
            return {
                "filename": filename,
                "file_type": "md",
                "directory": self.desktop_path
            }
        
        # Special handling for "make a json file" and "create a json file" without specific names
        if "json" in input_lower and ("make" in input_lower or "create" in input_lower) and "file" in input_lower:
            # Check if there's a specific name mentioned
            if "called" in input_lower:
                # Extract name after "called"
                called_match = re.search(r"called\s+(\w+)", input_lower)
                if called_match:
                    filename = called_match.group(1)
                else:
                    filename = "data"  # Default name for JSON files
            else:
                filename = "data"  # Default name for JSON files
            return {
                "filename": filename,
                "file_type": "json",
                "directory": self.desktop_path
            }
        
        # Enhanced patterns for better parsing
        enhanced_patterns = [
            # Python file patterns with specific names
            r"make.*python.*file.*called\s+(\w+)",  # "make a python file called test"
            r"create.*python.*file.*called\s+(\w+)",  # "create a python file called test"
            r"make.*(\w+)\s+python.*file",  # "make test python file"
            r"create.*(\w+)\s+python.*file",  # "create test python file"
            
            # Text file patterns with specific names
            r"make.*text.*file.*called\s+(\w+)",  # "make a text file called apple"
            r"create.*text.*file.*called\s+(\w+)",  # "create a text file called apple"
            r"make.*(\w+)\s+text.*file",  # "make apple text file"
            r"create.*(\w+)\s+text.*file",  # "create apple text file"
            r"make.*txt.*file.*called\s+(\w+)",  # "make a txt file called apple"
            r"create.*txt.*file.*called\s+(\w+)",  # "create a txt file called apple"
            
            # General file patterns
            r"make.*file.*called\s+(\w+)",  # "make a file called apple"
            r"create.*file.*called\s+(\w+)",  # "create a file called apple"
            r"make.*(\w+)\s+file",  # "make apple file"
            r"create.*(\w+)\s+file",  # "create apple file"
            
            # Specific file type patterns
            r"make.*(\w+)\.(\w+)",  # "make test.py" or "make test.txt"
            r"create.*(\w+)\.(\w+)",  # "create test.py" or "create test.txt"
            
            # Original patterns
            r"create.*file.*called\s+['\"]?(\w+)['\"]?\s+as\s+(\w+)",
            r"make.*file.*named\s+['\"]?(\w+)['\"]?\s+as\s+(\w+)",
            r"create.*file.*(\w+)\s+(\w+)",
            r"file.*(\w+)\s+(\w+)",
            r"(\w+)\s+(\w+)\s+file",  # "notes txt file"
            r"(\w+)\s+file\s+(\w+)"   # "notes file txt"
        ]
        
        # Try enhanced patterns first
        for pattern in enhanced_patterns:
            match = re.search(pattern, input_lower)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    # Single group - extract filename and infer file type
                    filename = groups[0]
                    # Skip common words that shouldn't be filenames
                    if filename.lower() in ["a", "an", "the", "file", "create", "make", "new"]:
                        continue
                    file_type = self._infer_file_type(input_lower, filename)
                elif len(groups) == 2:
                    # Two groups - filename and file type
                    filename = groups[0]
                    file_type = groups[1]
                else:
                    continue
                
                return {
                    "filename": filename,
                    "file_type": file_type,
                    "directory": self.desktop_path
                }
        
        # If no pattern matches, try to extract just a filename
        # Look for words that could be filenames
        words = input_lower.split()
        for word in words:
            if word.isalnum() and len(word) > 1 and word not in ["file", "create", "make", "new", "a", "an", "the"]:
                file_type = self._infer_file_type(input_lower, word)
                return {
                    "filename": word,
                    "file_type": file_type,
                    "directory": self.desktop_path
                }
        
        return None
    
    def _infer_file_type(self, user_input: str, filename: str) -> str:
        """Infer file type from user input"""
        input_lower = user_input.lower()
        
        # Check for specific file types in the input
        if "python" in input_lower or "py" in input_lower:
            return "py"
        elif "text" in input_lower or "txt" in input_lower:
            return "txt"
        elif "markdown" in input_lower or "md" in input_lower:
            return "md"
        elif "json" in input_lower:
            return "json"
        elif "html" in input_lower:
            return "html"
        elif "css" in input_lower:
            return "css"
        elif "javascript" in input_lower or "js" in input_lower:
            return "js"
        elif "pdf" in input_lower:
            return "pdf"
        else:
            # Default to txt for unknown types
            return "txt"
    
    def confirm_file_creation(self, filename: str, file_type: str, directory: str = None) -> str:
        """Confirm file creation with user"""
        if directory is None:
            directory = self.desktop_path
            
        # Ensure file type has dot
        if not file_type.startswith('.'):
            file_type = '.' + file_type
        
        full_filename = filename + file_type
        full_path = os.path.join(directory, full_filename)
        
        return f"""Creating '{full_filename}' in {os.path.basename(directory)}. Say "yes" to confirm or "no" to cancel."""
    
    def execute_file_creation(self, filename: str, file_type: str, directory: str = None) -> str:
        """Actually create the file"""
        try:
            if directory is None:
                directory = self.desktop_path
            
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            requested_dir = os.path.abspath(directory)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested directory is within the user's home directory
            if not requested_dir.startswith(home_dir):
                return "Error: Access denied - can only create files in your home directory and subdirectories"
            
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
            
            response = f"Created '{full_filename}' in {os.path.basename(directory)}"
            return self._remove_emojis(response)
            
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
        "todo file",
        "Make a text file called Apple",
        "Create a text file called Test",
        "Make a file called MyFile"
    ]
    
    for test_input in test_inputs:
        parsed = handler.parse_file_creation_request(test_input)
        print(f"Input: {test_input}")
        print(f"Parsed: {parsed}")
        if parsed:
            result = handler.execute_file_creation(parsed["filename"], parsed["file_type"], parsed["directory"])
            print(f"Result: {result}")
        print()

if __name__ == "__main__":
    test_file_creation()
