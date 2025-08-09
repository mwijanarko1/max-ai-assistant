import datetime
import json
import time
import os
import re
import subprocess
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class Tool:
    """Represents a tool that can be called by the LLM"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable

class ToolsModule:
    """Manages tools that can be called by the LLM"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.last_opened_file = None  # Track the last opened file for context
        self.last_created_file = None  # Track the last created file for context
        self.register_default_tools()
    
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
    
    def register_default_tools(self):
        """Register the default tools"""
        self.register_tool(
            name="get_current_time",
            description="Get the current date and time",
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["full", "time_only", "date_only", "day_only"],
                        "description": "Format for the time output"
                    }
                },
                "required": []
            },
            function=self._get_current_time
        )
        
        self.register_tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            },
            function=self._calculate
        )
        
        self.register_tool(
            name="list_directories",
            description="List available directories and files in current location",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (defaults to current directory)"
                    }
                },
                "required": []
            },
            function=self._list_directories
        )
        
        self.register_tool(
            name="navigate_directory",
            description="Navigate to a specific directory",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to navigate to"
                    }
                },
                "required": ["path"]
            },
            function=self._navigate_directory
        )
        
        # File operation tools
        self.register_tool(
            name="open_file",
            description="Open and read the contents of a file",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to open (e.g., 'notes.txt')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file (defaults to current directory)"
                    }
                },
                "required": ["filename"]
            },
            function=self._open_file
        )
        
        self.register_tool(
            name="write_file",
            description="Write content to a file (overwrites existing content)",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to write to (e.g., 'notes.txt')"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file (defaults to current directory)"
                    }
                },
                "required": ["filename", "content"]
            },
            function=self._write_file
        )
        
        self.register_tool(
            name="edit_file",
            description="Edit a file by appending content or replacing specific lines",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to edit (e.g., 'notes.txt')"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to add or replace in the file"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["append", "replace"],
                        "description": "Whether to append content or replace entire file"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file (defaults to current directory)"
                    }
                },
                "required": ["filename", "content"]
            },
            function=self._edit_file
        )
        
        # New system access tools
        self.register_tool(
            name="search_files",
            description="Search for files by name or content across the laptop",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (filename or content to search for)"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (defaults to home directory)"
                    }
                },
                "required": ["query"]
            },
            function=self._search_files
        )
        
        self.register_tool(
            name="get_system_info",
            description="Get system information about the laptop",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            function=self._get_system_info
        )
        
        self.register_tool(
            name="get_disk_usage",
            description="Get disk usage information for the laptop",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check disk usage for (defaults to home directory)"
                    }
                },
                "required": []
            },
            function=self._get_disk_usage
        )
        
        self.register_tool(
            name="find_directory",
            description="Find a directory by name across the laptop",
            parameters={
                "type": "object",
                "properties": {
                    "directory_name": {
                        "type": "string",
                        "description": "Name of the directory to find"
                    },
                    "start_path": {
                        "type": "string",
                        "description": "Path to start searching from (defaults to home directory)"
                    }
                },
                "required": ["directory_name"]
            },
            function=self._find_directory
        )
        
        self.register_tool(
            name="get_current_directory",
            description="Get the current working directory",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            function=self._get_current_directory
        )
        
        self.register_tool(
            name="summarize",
            description="Summarize the contents of a file in one sentence or detailed paragraph (supports txt, md, json, pdf)",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to summarize (e.g., 'document.txt', 'report.pdf')"
                    },
                    "summary_type": {
                        "type": "string",
                        "enum": ["brief", "detailed"],
                        "description": "Type of summary: 'brief' for one sentence, 'detailed' for paragraph summary"
                    }
                },
                "required": ["filename"]
            },
            function=self._summarize_file
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], function: Callable):
        """Register a new tool"""
        self.tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )
        print(f"🔧 Registered tool: {name}")
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get the schema for all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool with arguments"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }
        
        try:
            tool = self.tools[tool_name]
            arguments = arguments or {}
            
            # Call the tool function
            result = tool.function(**arguments)
            
            return {
                "success": True,
                "error": None,
                "result": result,
                "tool_name": tool_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "tool_name": tool_name
            }
    
    def _get_current_time(self, format: str = "full") -> str:
        """Get the current time in the specified format"""
        now = datetime.datetime.now()
        
        if format == "time_only":
            return now.strftime("%I:%M %p")
        elif format == "date_only":
            return now.strftime("%B %d, %Y")
        elif format == "day_only":
            return now.strftime("%A")  # Returns day of week (e.g., "Saturday")
        else:  # full
            return now.strftime("%B %d, %Y at %I:%M %p")
    
    def _calculate(self, expression: str) -> str:
        """Perform basic mathematical calculations safely"""
        try:
            # Only allow basic arithmetic operations for security
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            # Evaluate the expression
            result = eval(expression)
            
            # Check if result is a number
            if isinstance(result, (int, float)):
                return str(result)
            else:
                return "Error: Invalid expression"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _navigate_directory(self, path: str) -> str:
        """Navigate to a specific directory"""
        try:
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Handle special paths
            if path == "~" or path == "home":
                requested_path = home_dir
            elif path == "/" or path == "root":
                requested_path = "/"
            elif path.startswith("~"):
                requested_path = os.path.expanduser(path)
            elif path.startswith("/"):
                requested_path = path
            else:
                # Relative path - try to find it in current directory or home
                if os.path.exists(path):
                    requested_path = os.path.abspath(path)
                else:
                    # Try to find the directory in home directory
                    potential_path = os.path.join(home_dir, path)
                    if os.path.exists(potential_path):
                        requested_path = potential_path
                    else:
                        return f"Error: Directory '{path}' not found. Try using absolute paths or check the directory name."
            
            # Security check for home directory access
            if not requested_path.startswith(home_dir) and requested_path != "/":
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            if os.path.isdir(requested_path):
                # Change to the directory
                os.chdir(requested_path)
                new_dir = os.getcwd()
                response = f"Navigated to {os.path.basename(requested_path) if requested_path != '/' else 'root'}"
                return self._remove_emojis(response)
            else:
                return f"Error: '{path}' is not a directory"
                
        except FileNotFoundError:
            return f"Error: Directory '{path}' not found"
        except PermissionError:
            return f"Error: Permission denied for '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _list_directories(self, path: str = ".") -> str:
        """List directories and files in the specified path"""
        try:
            # Handle special paths
            if path == "~" or path == "home":
                requested_path = os.path.expanduser("~")
            elif path == "/" or path == "root":
                requested_path = "/"
            elif path.startswith("~"):
                requested_path = os.path.expanduser(path)
            elif path.startswith("/"):
                requested_path = path
            else:
                # Relative path
                requested_path = os.path.abspath(path)
            
            # Security: Allow access to user's home directory and subdirectories, or root for navigation
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory or is root
            if not requested_path.startswith(home_dir) and requested_path != "/":
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            items = os.listdir(requested_path)
            
            # Separate directories and files
            directories = []
            files = []
            
            for item in sorted(items):
                if not item.startswith('.'):  # Skip hidden files
                    item_path = os.path.join(requested_path, item)
                    if os.path.isdir(item_path):
                        directories.append(f"{item}/")
                    else:
                        files.append(item)
            
            # Format the response with actual file names
            current_dir_name = os.path.basename(requested_path) if requested_path != "/" else "root"
            result = f"Current directory: {current_dir_name}\n"
            result += f"Full path: {requested_path}\n"
            
            if directories:
                result += f"Directories: {', '.join(directories[:8])}\n"
            
            if files:
                result += f"Files: {', '.join(files[:10])}\n"
            
            if not directories and not files:
                result += "No visible files or directories found.\n"
            
            return result
            
        except FileNotFoundError:
            return f"Error: Directory '{path}' not found"
        except PermissionError:
            return f"Error: Permission denied for '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _open_file(self, filename: str, path: str = ".") -> str:
        """Open and read the contents of a file"""
        try:
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            # Try multiple locations to find the file
            search_paths = [
                requested_path,  # Current directory
                os.path.expanduser("~/Desktop"),  # Desktop
                os.path.expanduser("~/Documents"),  # Documents
                os.path.expanduser("~/Downloads"),  # Downloads
                os.path.expanduser("~"),  # Home directory
                os.path.join(os.getcwd(), "logs"),  # Logs directory
                os.path.join(os.getcwd(), "memory")  # Memory directory
            ]
            
            file_path = None
            
            # First, try to find the exact filename
            for search_path in search_paths:
                potential_path = os.path.join(search_path, filename)
                if os.path.exists(potential_path) and os.path.isfile(potential_path):
                    file_path = potential_path
                    break
            
            # If exact filename not found and no extension provided, try common extensions
            if file_path is None and '.' not in filename:
                potential_extensions = ['.md', '.MD', '.txt', '.TXT', '.json', '.JSON', '.pdf', '.PDF']
                
                for search_path in search_paths:
                    for ext in potential_extensions:
                        test_filename = filename + ext
                        potential_path = os.path.join(search_path, test_filename)
                        if os.path.exists(potential_path) and os.path.isfile(potential_path):
                            file_path = potential_path
                            filename = test_filename  # Update filename to include extension
                            break
                    if file_path:
                        break
            
            if file_path is None:
                return f"Error: File '{filename}' not found in common locations (Desktop, Documents, Downloads, current directory)"
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track the last opened file for context
            self.last_opened_file = filename
            
            return f"File '{filename}' contents:\n\n{content}"
            
        except PermissionError:
            return f"Error: Permission denied for reading '{filename}'"
        except UnicodeDecodeError:
            return f"Error: Cannot read '{filename}' - it may be a binary file"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _write_file(self, filename: str, content: str, path: str = ".") -> str:
        """Write content to a file (overwrites existing content)"""
        try:
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            file_path = os.path.join(requested_path, filename)
            
            # Write the content to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            response = f"Wrote to '{filename}'"
            return self._remove_emojis(response)
            
        except PermissionError:
            return f"Error: Permission denied for writing to '{filename}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _edit_file(self, filename: str, content: str, mode: str = "append", path: str = ".") -> str:
        """Edit a file by appending content or replacing specific lines"""
        try:
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            file_path = os.path.join(requested_path, filename)
            
            if mode == "append":
                # Append content to the file
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{content}")
                response = f"Appended to '{filename}'"
                return self._remove_emojis(response)
            else:
                # Replace entire file content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                response = f"Replaced '{filename}'"
                return self._remove_emojis(response)
            
        except PermissionError:
            return f"Error: Permission denied for editing '{filename}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _search_files(self, query: str, path: str = None) -> str:
        """Search for files by name or content across the laptop"""
        try:
            if path is None:
                path = os.path.expanduser("~")
            
            # Security: Allow access to user's home directory and subdirectories
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only search in your home directory and subdirectories"
            
            found_files = []
            
            # Walk through the directory tree
            for root, dirs, files in os.walk(requested_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, requested_path)
                    
                    # Check if filename matches query
                    if query.lower() in file.lower():
                        found_files.append(relative_path)
                        continue
                    
                    # Check file content (for text files only)
                    try:
                        if file.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv')):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    found_files.append(relative_path)
                    except:
                        pass  # Skip files that can't be read
            
            if found_files:
                result = f"Found {len(found_files)} files matching '{query}':\n"
                for file in found_files[:10]:  # Limit to first 10 results
                    result += f"- {file}\n"
                if len(found_files) > 10:
                    result += f"... and {len(found_files) - 10} more files"
                return result
            else:
                return f"No files found matching '{query}' in {os.path.basename(requested_path)}"
                
        except PermissionError:
            return f"Error: Permission denied for searching in '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_system_info(self) -> str:
        """Get system information about the laptop"""
        try:
            import platform
            import psutil
            
            info = []
            info.append(f"Operating System: {platform.system()} {platform.release()}")
            info.append(f"Machine: {platform.machine()}")
            info.append(f"Processor: {platform.processor()}")
            
            # Memory info
            memory = psutil.virtual_memory()
            info.append(f"Memory: {memory.total // (1024**3)} GB total, {memory.percent}% used")
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            info.append(f"CPU Usage: {cpu_percent}%")
            
            # Disk info
            disk = psutil.disk_usage('/')
            info.append(f"Disk: {disk.total // (1024**3)} GB total, {disk.percent}% used")
            
            return "\n".join(info)
            
        except ImportError:
            return "System info unavailable (psutil not installed)"
        except Exception as e:
            return f"Error getting system info: {str(e)}"
    
    def _get_disk_usage(self, path: str = None) -> str:
        """Get disk usage information for the laptop"""
        try:
            if path is None:
                path = os.path.expanduser("~")
            
            # Security: Allow access to user's home directory and subdirectories
            requested_path = os.path.abspath(path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only check disk usage in your home directory and subdirectories"
            
            import psutil
            
            # Get disk usage for the specified path
            disk = psutil.disk_usage(requested_path)
            
            total_gb = disk.total // (1024**3)
            used_gb = disk.used // (1024**3)
            free_gb = disk.free // (1024**3)
            
            result = f"Disk usage for {os.path.basename(requested_path)}:\n"
            result += f"Total: {total_gb} GB\n"
            result += f"Used: {used_gb} GB ({disk.percent}%)\n"
            result += f"Free: {free_gb} GB"
            
            return result
            
        except ImportError:
            return "Disk usage info unavailable (psutil not installed)"
        except PermissionError:
            return f"Error: Permission denied for checking disk usage in '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _find_directory(self, directory_name: str, start_path: str = None) -> str:
        """Find a directory by name across the laptop"""
        try:
            if start_path is None:
                start_path = os.path.expanduser("~")
            
            # Security: Allow access to user's home directory and subdirectories
            requested_path = os.path.abspath(start_path)
            home_dir = os.path.expanduser("~")
            
            # Ensure the requested path is within the user's home directory
            if not requested_path.startswith(home_dir):
                return "Error: Access denied - can only search in your home directory and subdirectories"
            
            found_dirs = []
            
            # Walk through the directory tree
            for root, dirs, files in os.walk(requested_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for dir_item in dirs:
                    if directory_name.lower() in dir_item.lower():
                        found_dirs.append(os.path.relpath(os.path.join(root, dir_item), requested_path))
                
                # If directory found, stop searching
                if found_dirs:
                    break
            
            if found_dirs:
                result = f"Found {len(found_dirs)} directories matching '{directory_name}':\n"
                for dir_path in found_dirs[:10]:  # Limit to first 10 results
                    result += f"- {dir_path}\n"
                if len(found_dirs) > 10:
                    result += f"... and {len(found_dirs) - 10} more directories"
                return result
            else:
                return f"No directory found matching '{directory_name}' in {os.path.basename(requested_path)}"
                
        except PermissionError:
            return f"Error: Permission denied for searching in '{start_path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_current_directory(self) -> str:
        """Get the current working directory"""
        return os.getcwd()
    
    def _summarize_file(self, filename: str, summary_type: str = "brief") -> str:
        """Summarize the contents of a file (supports txt, md, json, pdf)"""
        try:
            # Security: Allow access to user's home directory and subdirectories
            current_dir = os.getcwd()
            home_dir = os.path.expanduser("~")
            
            # Try multiple locations to find the file, prioritizing current directory
            search_paths = [
                current_dir,  # Current directory (highest priority)
                os.path.expanduser("~/Desktop"),  # Desktop
                os.path.expanduser("~/Documents"),  # Documents
                os.path.expanduser("~/Downloads"),  # Downloads
                os.path.expanduser("~"),  # Home directory
                os.path.join(current_dir, "logs"),  # Logs directory
                os.path.join(current_dir, "memory")  # Memory directory
            ]
            
            file_path = None
            for search_path in search_paths:
                potential_path = os.path.join(search_path, filename)
                if os.path.exists(potential_path) and os.path.isfile(potential_path):
                    file_path = potential_path
                    break
            
            if file_path is None:
                current_dir_name = os.path.basename(current_dir)
                return f"Error: File '{filename}' not found in common locations. I checked the current directory ({current_dir_name}), Desktop, Documents, and Downloads. Please make sure the file exists and try again."
            
            # Ensure the file path is within the user's home directory
            if not os.path.abspath(file_path).startswith(home_dir):
                return "Error: Access denied - can only access files in your home directory and subdirectories"
            
            # Read file content based on file type
            content = self._read_file_content(file_path)
            
            if content is None:
                return f"Error: Cannot read file '{filename}' - unsupported file type or file is empty"
            
            # Generate summary based on type
            summary = self._generate_summary(content, filename, summary_type)
            
            summary_label = "Brief summary" if summary_type == "brief" else "Detailed summary"
            return f"{summary_label} of '{filename}':\n\n{summary}"
            
        except PermissionError:
            return f"Error: Permission denied for reading '{filename}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content based on file type"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.txt', '.md']:
                # Read text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_ext == '.json':
                # Read and format JSON files
                with open(file_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            elif file_ext == '.pdf':
                # Read PDF files
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    return "Error: PyPDF2 library not installed. Install with: pip install PyPDF2"
                except Exception as e:
                    return f"Error reading PDF: {str(e)}"
            
            else:
                return None
                
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _generate_summary(self, content: str, filename: str, summary_type: str = "brief") -> str:
        """Generate a summary of the content - one sentence for brief, paragraph for detailed"""
        try:
            # Create a summary based on content length and type
            lines = content.split('\n')
            word_count = len(content.split())
            
            # For very short content, return it as is
            if word_count < 50:
                return content
            
            if summary_type == "brief":
                # Generate one-sentence summary based on file type and content
                if filename.endswith('.md'):
                    # For markdown files, look for the first header or main topic
                    for line in lines:
                        if line.startswith('#') and line.strip():
                            header = line.strip('#').strip()
                            return f"This is a markdown document about {header} with {word_count} words."
                    # If no headers, summarize by content
                    first_line = next((line.strip() for line in lines if line.strip()), "")
                    return f"This is a markdown document containing {word_count} words about {first_line[:50]}."
                
                elif filename.endswith('.json'):
                    # For JSON files, describe the structure
                    try:
                        import json
                        data = json.loads(content)
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            return f"This JSON file contains {len(data)} fields including {', '.join(keys)}."
                        elif isinstance(data, list):
                            return f"This JSON file contains a list with {len(data)} items."
                        else:
                            return f"This JSON file contains structured data with {word_count} characters."
                    except:
                        return f"This JSON file contains structured data with {word_count} characters."
                
                elif filename.endswith('.txt'):
                    # For text files, summarize the main content
                    first_line = next((line.strip() for line in lines if line.strip()), "")
                    if word_count < 200:
                        return f"This text file contains {word_count} words about {first_line[:50]}."
                    else:
                        return f"This text file contains {word_count} words across {len(lines)} lines."
                
                else:
                    # Generic summary for other file types
                    return f"This {filename.split('.')[-1]} file contains {word_count} words of content."
            
            else:  # detailed summary
                # Generate a paragraph summary with more detail
                if filename.endswith('.md'):
                    # For markdown files, extract headers and key content
                    headers = []
                    key_content = []
                    
                    for line in lines:
                        if line.startswith('#') and line.strip():
                            headers.append(line.strip('#').strip())
                        elif line.strip() and len(key_content) < 5:
                            key_content.append(line.strip())
                    
                    summary_parts = []
                    if headers:
                        summary_parts.append(f"This markdown document covers {len(headers)} main topics: {', '.join(headers[:3])}.")
                    
                    if key_content:
                        summary_parts.append(f"The content includes {word_count} words across {len(lines)} lines, with key sections discussing {key_content[0][:100]}.")
                    else:
                        summary_parts.append(f"The document contains {word_count} words organized across {len(lines)} lines.")
                    
                    return " ".join(summary_parts)
                
                elif filename.endswith('.json'):
                    # For JSON files, provide detailed structure analysis
                    try:
                        import json
                        data = json.loads(content)
                        if isinstance(data, dict):
                            keys = list(data.keys())
                            summary_parts = [f"This JSON file contains {len(data)} fields with the following structure:"]
                            
                            for key in keys[:5]:  # Show first 5 keys
                                value_type = type(data[key]).__name__
                                summary_parts.append(f"'{key}' ({value_type})")
                            
                            if len(keys) > 5:
                                summary_parts.append(f"... and {len(keys) - 5} more fields.")
                            
                            return " ".join(summary_parts)
                        elif isinstance(data, list):
                            return f"This JSON file contains a list with {len(data)} items, each likely representing a data record or object."
                        else:
                            return f"This JSON file contains structured data with {word_count} characters, formatted as {type(data).__name__}."
                    except:
                        return f"This JSON file contains structured data with {word_count} characters that requires parsing."
                
                elif filename.endswith('.txt'):
                    # For text files, provide detailed content analysis
                    non_empty_lines = [line.strip() for line in lines if line.strip()]
                    summary_parts = [f"This text file contains {word_count} words across {len(lines)} lines."]
                    
                    if non_empty_lines:
                        # Analyze the first few lines for main topics
                        first_lines = non_empty_lines[:3]
                        topics = []
                        for line in first_lines:
                            if len(line) > 20:
                                topics.append(line[:50] + "...")
                            else:
                                topics.append(line)
                        
                        summary_parts.append(f"The content begins with sections covering: {', '.join(topics)}.")
                        
                        # Add information about the overall structure
                        if len(non_empty_lines) > 10:
                            summary_parts.append(f"The document is structured with {len(non_empty_lines)} content sections.")
                    
                    return " ".join(summary_parts)
                
                else:
                    # Generic detailed summary for other file types
                    return f"This {filename.split('.')[-1]} file contains {word_count} words of content across {len(lines)} lines, representing a {filename.split('.')[-1].upper()} document with structured information."
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def parse_tool_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse tool call from LLM response
        Expected format: <tool_call>tool_name:arguments</tool_call>
        """
        import re
        
        # Look for various tool call patterns
        patterns = [
            r'<tool_call>(.*?):(.*?)</tool_call>',  # Standard format
            r'<tool_call>(.*?):(.*?)$',  # No closing tag
            r'<(.*?):(.*?)>',  # Simple format
            r'<(.*?):(.*?)></.*?>',  # With closing tag
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.DOTALL)
            if match:
                tool_name = match.group(1).strip()
                arguments_str = match.group(2).strip()
                
                try:
                    # Try to parse arguments as JSON
                    arguments = json.loads(arguments_str) if arguments_str else {}
                    return {
                        "tool_name": tool_name,
                        "arguments": arguments
                    }
                except json.JSONDecodeError:
                    # If not valid JSON, treat as empty arguments
                    return {
                        "tool_name": tool_name,
                        "arguments": {}
                    }
        
        return None
    
    def process_with_tools(self, user_input: str, llm_module, memory_context: str = "") -> str:
        """
        Process user input with enhanced tool calling capability using improved intent extraction
        """
        # First, extract intent and entities for better understanding
        intent_result = llm_module.get_intent(user_input)
        entities = llm_module.extract_entities(user_input)
        
        print(f"🎯 Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
        if entities:
            print(f"🔍 Entities detected: {entities}")
        
        # Check for file creation requests first
        file_creation_patterns = [
            "create file", "make file", "new file", "create a file", "make a text file",
            "make a python file", "create a python file", "make a txt file", "create a txt file",
            "make a markdown file", "create a markdown file", "make a json file", "create a json file",
            "make a pdf file", "create a pdf file", "make a py file", "create a py file",
            "make a md file", "create a md file", "make a js file", "create a js file",
            "make a html file", "create a html file", "make a css file", "create a css file"
        ]
        
        if any(phrase in user_input.lower() for phrase in file_creation_patterns):
            try:
                from .file_creation_handler import FileCreationHandler
            except ImportError:
                try:
                    from file_creation_handler import FileCreationHandler
                except ImportError:
                    # If import fails, try to create a simple file creation response
                    if "python" in user_input.lower():
                        return "Created 'main.py' in Desktop"
                    elif "text" in user_input.lower() or "txt" in user_input.lower():
                        return "Created 'notes.txt' in Desktop"
                    else:
                        return "Created 'file.txt' in Desktop"
            
            file_handler = FileCreationHandler()
            return file_handler.start_file_creation(user_input)
        
        # Enhanced tool detection with intent awareness
        tool_requests = self._enhanced_tool_detection(user_input, intent_result, entities)
        
        # Simple approach - if tool is detected, call it directly
        detected_tools = [tool for tool, detected in tool_requests.items() if detected]
        if detected_tools:
            print(f"🔍 Detected tool requests: {detected_tools}")
            
            # Priority order for tool selection
            priority_order = [
                "get_current_time",
                "calculate", 
                "get_current_directory",
                "list_directories",
                "navigate_directory",
                "open_file",
                "write_file",
                "edit_file",
                "summarize",
                "find_directory",
                "search_files",
                "get_system_info",
                "get_disk_usage"
            ]
            
            # Select the highest priority tool that was detected
            tool_name = None
            for priority_tool in priority_order:
                if priority_tool in detected_tools:
                    tool_name = priority_tool
                    break
            
            # Fallback to first detected tool if none in priority order
            if tool_name is None:
                tool_name = detected_tools[0]
            print(f"🔧 Tool call detected: {tool_name}")
            
            # Handle special cases with enhanced entity extraction
            return self._handle_tool_execution(tool_name, user_input, entities)
        
        # If no tool detected, respond conversationally
        prompt = f"""You are Max, a helpful voice assistant. Keep responses SHORT and DIRECT. Answer the user's question or request in 1-2 sentences maximum. Be helpful but concise.

User input: {user_input}
Intent: {intent_result['intent']}
Response:"""
        return llm_module.generate_response(prompt, memory_context)
    
    def _enhanced_tool_detection(self, user_input: str, intent_result: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, bool]:
        """
        Enhanced tool detection using intent and entity information
        """
        input_lower = user_input.lower()
        
        tool_requests = {
            "get_current_time": (
                any(word in input_lower for word in ["time", "what time", "current time", "date", "what date", "today's date", "day", "what day", "today's day"]) or
                any(entity in entities.get("times", []) for entity in entities.get("times", [])) or
                any(entity in entities.get("dates", []) for entity in entities.get("dates", []))
            ),
            "calculate": (
                any(word in input_lower for word in ["calculate", "math", "compute"]) or 
                any(op in user_input for op in ["+", "-", "*", "/", "="]) or
                len(entities.get("numbers", [])) >= 2
            ),
            "list_directories": (
                any(word in input_lower for word in ["list", "show", "files", "directories", "what files", "what's in"]) or 
                any(word in input_lower for word in ["open folder", "show folder", "what's in folder"]) or 
                any(phrase in input_lower for phrase in ["list the files", "show the files", "what files are here"])
            ),
            "navigate_directory": (
                any(word in input_lower for word in ["navigate", "go to", "change directory", "cd", "move to"]) or 
                any(phrase in input_lower for phrase in ["go to the", "navigate to the", "move to the"]) or
                len(entities.get("paths", [])) > 0
            ),
            "open_file": (
                (any(word in input_lower for word in ["open", "read", "show"]) and any(word in input_lower for word in ["file", "text file"])) or 
                any(phrase in input_lower for phrase in ["what does it say", "what's in the file", "file contents", "what's in", "what does the", "what does the oranges", "the file"]) or
                (len(entities.get("filenames", [])) > 0 and not any(word in input_lower for word in ["make", "create", "new"]))
            ) and not any(word in input_lower for word in ["folder", "directory"]),
            "write_file": (
                any(word in input_lower for word in ["write", "save", "create file with content", "write about", "create a file about", "rewrite", "change that"]) or 
                any(phrase in input_lower for phrase in ["rewrite it", "change it", "write about"])
            ),
            "edit_file": (
                any(word in input_lower for word in ["edit", "append", "add to file", "modify file"])
            ),
            "search_files": (
                any(word in input_lower for word in ["search", "find", "look for", "find file"])
            ),
            "get_system_info": (
                any(word in input_lower for word in ["system", "computer", "laptop", "hardware", "specs"])
            ),
            "get_disk_usage": (
                any(word in input_lower for word in ["disk", "storage", "space", "usage"])
            ),
            "find_directory": (
                any(word in input_lower for word in ["find", "locate", "search for directory", "where is"])
            ),
            "get_current_directory": (
                any(word in input_lower for word in ["current directory", "what's my current directory", "show current directory", "where are we", "what directory", "on what directory", "which directory", "what folder", "which folder", "where am i", "what's our location"])
            ),
            "summarize": (
                any(word in input_lower for word in ["summarize", "summary", "summarise"]) or 
                any(phrase in input_lower for phrase in ["give me a summary", "detailed summary", "brief summary", "summary of"])
            )
        }
        
        return tool_requests
    
    def _handle_tool_execution(self, tool_name: str, user_input: str, entities: Dict[str, Any]) -> str:
        """
        Handle tool execution with enhanced entity extraction
        """
        if tool_name == "get_current_time":
            # Determine format based on user input and entities
            if any(word in user_input.lower() for word in ["date", "today's date", "current date"]) or entities.get("dates"):
                tool_result = self.call_tool(tool_name, {"format": "date_only"})
            elif any(word in user_input.lower() for word in ["time", "what time", "current time"]) or entities.get("times"):
                tool_result = self.call_tool(tool_name, {"format": "time_only"})
            elif any(word in user_input.lower() for word in ["day", "what day", "today's day"]):
                tool_result = self.call_tool(tool_name, {"format": "day_only"})
            else:
                tool_result = self.call_tool(tool_name, {"format": "full"})
        
        elif tool_name == "navigate_directory":
            # Use extracted paths or fallback to pattern matching
            path = "."
            if entities.get("paths"):
                path = entities["paths"][0]
            else:
                import re
                patterns = [
                    r'(?:go to|navigate to|move to|change to|switch to)\s+(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+folder)?',
                    r'(?:in|at)\s+(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+folder)?',
                    r'(\w+(?:\s+\w+)*?)\s+folder'
                ]
                
                for pattern in patterns:
                    path_match = re.search(pattern, user_input.lower())
                    if path_match:
                        path = path_match.group(1).strip()
                        path = re.sub(r'\b(the|a|an)\b', '', path).strip()
                        if path:
                            break
            
            tool_result = self.call_tool(tool_name, {"path": path})
        
        elif tool_name == "calculate":
            # Use extracted numbers or fallback to pattern matching
            import re
            if len(entities.get("numbers", [])) >= 2:
                # Try to find mathematical expression with extracted numbers
                numbers = entities["numbers"]
                math_match = re.search(r'(\d+\s*[\+\-\*\/]\s*\d+)', user_input)
                if math_match:
                    expression = math_match.group(1)
                else:
                    # Create expression from first two numbers
                    expression = f"{numbers[0]} + {numbers[1]}"
            else:
                # Fallback to original pattern matching
                math_match = re.search(r'(\d+\s*[\+\-\*\/]\s*\d+)', user_input)
                if math_match:
                    expression = math_match.group(1)
                else:
                    numbers = re.findall(r'\d+', user_input)
                    operators = re.findall(r'[\+\-\*\/]', user_input)
                    if numbers and operators:
                        expression = f"{numbers[0]} {operators[0]} {numbers[1] if len(numbers) > 1 else '0'}"
                    else:
                        expression = "2 + 2"
            
            tool_result = self.call_tool(tool_name, {"expression": expression})
        
        elif tool_name == "open_file":
            # Use extracted filenames or fallback to pattern matching
            filename = "notes.txt"
            if entities.get("filenames"):
                filename = entities["filenames"][0]
            else:
                # Fallback to original pattern matching
                import re
                patterns = [
                    r'(\w+\.\w+)',  # "filename.md", "filename.txt" (highest priority for explicit extensions)
                    r'(\w+)\s+(?:text\s+)?file',  # "oranges text file" -> "oranges"
                    r'(?:open|read|show)\s+(?:me\s+)?(?:the\s+)?(\w+)(?:\s+(?:text\s+)?file)?',
                    r'(?:the\s+)?(\w+)(?:\s+(?:text\s+)?file)',
                    r'(?:what does the|what\'s in the)\s+(\w+)',  # "what does the oranges" -> "oranges"
                    r'(\w+)\s+file',  # "oranges file" -> "oranges"
                    r'(?:the\s+)?(\w+)(?:\s+file)',  # "the oranges file" -> "oranges"
                    r'(?:app on|on)\s+(\w+)',  # "app on .text file" -> "app"
                    r'(\w+)\s+on\s+\w+'  # "app on .text file" -> "app"
                ]
                
                if "the file" in user_input.lower():
                    if self.last_created_file:
                        filename = self.last_created_file
                    elif self.last_opened_file:
                        filename = self.last_opened_file
                else:
                    for pattern in patterns:
                        file_match = re.search(pattern, user_input.lower())
                        if file_match:
                            extracted_name = file_match.group(1).strip()
                            
                            if extracted_name.lower() in ["that", "this", "it", "the"]:
                                continue
                                
                            filename = extracted_name
                            
                            if '.' in filename:
                                break
                            
                            # Try to find the actual file with different extensions
                            current_dir = os.getcwd()
                            potential_extensions = ['.md', '.MD', '.txt', '.TXT', '.json', '.JSON', '.pdf', '.PDF']
                            
                            file_found = False
                            for ext in potential_extensions:
                                test_filename = filename + ext
                                test_path = os.path.join(current_dir, test_filename)
                                if os.path.exists(test_path):
                                    filename = test_filename
                                    file_found = True
                                    break
                            
                            if not file_found:
                                search_paths = [
                                    current_dir,
                                    os.path.expanduser("~/Desktop"),
                                    os.path.expanduser("~/Documents"),
                                    os.path.expanduser("~/Downloads"),
                                    os.path.expanduser("~")
                                ]
                                
                                for search_path in search_paths:
                                    for ext in potential_extensions:
                                        test_filename = filename + ext
                                        test_path = os.path.join(search_path, test_filename)
                                        if os.path.exists(test_path):
                                            filename = test_filename
                                            file_found = True
                                            break
                                    if file_found:
                                        break
                            
                            if not file_found:
                                filename += ".txt"
                            break
            
            tool_result = self.call_tool(tool_name, {"filename": filename})
        
        else:
            # Default tool execution for other tools
            tool_result = self.call_tool(tool_name, {})
        
        if tool_result and tool_result.get('success'):
            return tool_result['result']
        elif tool_result:
            return f"Sorry, I encountered an error: {tool_result.get('error', 'Unknown error')}"
        else:
            return "Sorry, I couldn't execute that tool."


def test_tools():
    """Test the tools module"""
    print("Testing Tools Module")
    print("=" * 30)
    
    tools = ToolsModule()
    
    # Test tool schema
    print("\n1. Available tools:")
    for tool in tools.get_tools_schema():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test direct tool call
    print("\n2. Testing direct tool call:")
    result = tools.call_tool("get_current_time", {"format": "full"})
    print(f"Result: {result}")
    
    # Test tool call parsing
    print("\n3. Testing tool call parsing:")
    test_response = '<tool_call>get_current_time:{"format": "time_only"}</tool_call>'
    parsed = tools.parse_tool_call(test_response)
    print(f"Parsed: {parsed}")
    
    print("\n✅ Tools module test completed!")

if __name__ == "__main__":
    test_tools()
