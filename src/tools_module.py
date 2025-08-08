import datetime
import json
import time
import os
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
        self.register_default_tools()
    
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
                        "enum": ["full", "time_only", "date_only"],
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
                return f"Successfully navigated to: {os.path.basename(requested_path) if requested_path != '/' else 'root'}\nCurrent directory: {new_dir}"
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
            
            file_path = os.path.join(requested_path, filename)
            
            if not os.path.exists(file_path):
                return f"Error: File '{filename}' not found"
            
            if not os.path.isfile(file_path):
                return f"Error: '{filename}' is not a file"
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            return f"✅ Successfully wrote content to '{filename}'"
            
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
                return f"✅ Successfully appended content to '{filename}'"
            else:
                # Replace entire file content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"✅ Successfully replaced content in '{filename}'"
            
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
    
    def parse_tool_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse tool call from LLM response
        Expected format: <tool_call>tool_name:arguments</tool_call>
        """
        import re
        
        # Look for tool call pattern - handle both with and without closing tag
        pattern1 = r'<tool_call>(.*?):(.*?)</tool_call>'
        pattern2 = r'<tool_call>(.*?):(.*?)$'
        
        match = re.search(pattern1, llm_response, re.DOTALL)
        if not match:
            match = re.search(pattern2, llm_response, re.DOTALL)
        

        
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
        Process user input with tool calling capability
        
        Args:
            user_input: User's input
            llm_module: LLM module instance
            memory_context: Session memory context
        """
        # Check for file creation requests first
        if any(phrase in user_input.lower() for phrase in ["create file", "make file", "new file", "create a file", "make a text file"]):
            from file_creation_handler import FileCreationHandler
            file_handler = FileCreationHandler()
            return file_handler.start_file_creation(user_input)
        
        # Check for explicit tool requests first
        tool_requests = {
            "time": any(word in user_input.lower() for word in ["time", "what time", "current time"]),
            "date": any(word in user_input.lower() for word in ["date", "what date", "today's date", "current date"]),
            "calculate": any(word in user_input.lower() for word in ["calculate", "math", "what is", "compute", "+", "-", "*", "/"]),
            "list_files": any(word in user_input.lower() for word in ["list", "show", "files", "directories", "what files", "what's in"]),
            "navigate": any(word in user_input.lower() for word in ["navigate", "go to", "change directory", "cd", "move to"]),
            "open_file": any(word in user_input.lower() for word in ["open", "read", "show file", "file contents"]),
            "write_file": any(word in user_input.lower() for word in ["write", "save", "create file with content", "write about", "create a file about"]),
            "edit_file": any(word in user_input.lower() for word in ["edit", "append", "add to file", "modify file"]),
            "search_files": any(word in user_input.lower() for word in ["search", "find", "look for", "find file"]),
            "system_info": any(word in user_input.lower() for word in ["system", "computer", "laptop", "hardware", "specs"]),
            "disk_usage": any(word in user_input.lower() for word in ["disk", "storage", "space", "usage"]),
            "find_directory": any(word in user_input.lower() for word in ["find", "locate", "search for directory", "where is"]),
            "get_current_directory": any(word in user_input.lower() for word in ["current directory", "what's my current directory", "show current directory", "where are we", "what directory", "on what directory", "which directory"])
        }
        
        # If no explicit tool request, respond conversationally
        if not any(tool_requests.values()):
            # Generate conversational response without tools
            prompt = f"""You are Max, a helpful voice assistant. Respond conversationally to the user's input.

User input: {user_input}
Response:"""
            return llm_module.generate_response(prompt, memory_context)
        
        # Debug: Print detected tool requests
        detected_tools = [tool for tool, detected in tool_requests.items() if detected]
        if detected_tools:
            print(f"🔍 Detected tool requests: {detected_tools}")
        
        # Special handling for write_file requests that need content generation
        if tool_requests.get("write_file") and any(phrase in user_input.lower() for phrase in ["write about", "create a file about", "write content about"]):
            # Generate content first, then write to file
            content_prompt = f"""You are Max, a helpful assistant. The user wants to write about a topic. Generate informative content about the topic.

User request: {user_input}

Generate a comprehensive, well-written response about the topic. Make it informative and engaging. Write it as if you're creating content for a file.

Response:"""
            
            # Generate content
            content_response = llm_module.generate_response(content_prompt, memory_context)
            
            # Extract filename from the request or use a default
            filename = "content.txt"
            if "apple" in user_input.lower():
                filename = "apple_history.txt"
            elif "history" in user_input.lower():
                filename = "history.txt"
            else:
                # Try to extract a filename from the request
                words = user_input.lower().split()
                for i, word in enumerate(words):
                    if word in ["about", "on", "for"] and i + 1 < len(words):
                        topic = words[i + 1]
                        filename = f"{topic}.txt"
                        break
            
            # Write the content to file
            write_result = self.call_tool("write_file", {
                "filename": filename,
                "content": content_response
            })
            
            if write_result['success']:
                return f"✅ I've written about the topic and saved it to '{filename}'. The file contains comprehensive information about the subject."
            else:
                return f"Sorry, I encountered an error while writing the file: {write_result['error']}"
        
        # Only use tools for explicit requests
        tools_schema = self.get_tools_schema()
        
        # Create a prompt that includes tool information
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tools_schema
        ])
        
        prompt = f"""You are Max, a helpful voice assistant. You have access to these tools:

{tools_info}

ONLY use a tool call if the user explicitly asks for information that these tools can provide. For example:
- "What time is it?" → use get_current_time with "time_only" format
- "What's the date?" → use get_current_time with "date_only" format  
- "What's today's date and time?" → use get_current_time with "full" format
- "What is 2 + 3?" or "Calculate 10 * 5" → use calculate
- "List directories" or "Show files" → use list_directories
- "Navigate to docs" or "Go to docs" → use navigate_directory
- "Open notes.txt" or "Read my file" → use open_file
- "Write 'hello world' to test.txt" → use write_file
- "Edit my file with new content" → use edit_file
- "Search for myfile.txt" or "Find documents" → use search_files
- "System information" or "Computer specs" → use get_system_info
- "Disk usage" or "Storage space" → use get_disk_usage
- "Find directory 'my_dir'" or "Locate 'my_dir'" → use find_directory
- "What's my current directory?" or "Where are we?" → use get_current_directory
- "Where are we?" → <tool_call>get_current_directory:{{}}
- "What directory are we on?" → <tool_call>get_current_directory:{{}}

If the user asks for information that can be provided by these tools, respond with a tool call in this format:
<tool_call>tool_name:arguments</tool_call>

For example:
- "What time is it?" → <tool_call>get_current_time:{{"format": "time_only"}}</tool_call>
- "What's the date?" → <tool_call>get_current_time:{{"format": "date_only"}}</tool_call>
- "What's today's date and time?" → <tool_call>get_current_time:{{"format": "full"}}</tool_call>
- "What is 2 + 3?" → <tool_call>calculate:{{"expression": "2 + 3"}}</tool_call>
- "Calculate 10 * 5" → <tool_call>calculate:{{"expression": "10 * 5"}}</tool_call>
- "List directories" → <tool_call>list_directories:{{"path": "."}}</tool_call>
- "Navigate to docs" → <tool_call>navigate_directory:{{"path": "docs"}}</tool_call>
- "Open notes.txt" → <tool_call>open_file:{{"filename": "notes.txt"}}</tool_call>
- "Write 'hello world' to test.txt" → <tool_call>write_file:{{"filename": "test.txt", "content": "hello world"}}</tool_call>
- "Write about the history of Apple" → <tool_call>write_file:{{"filename": "apple_history.txt", "content": "Apple Inc. was founded in 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne. The company revolutionized personal computing with products like the Apple I, Apple II, Macintosh, iPod, iPhone, and iPad. Apple has become one of the world's most valuable companies, known for innovation in design and technology."}}</tool_call>
- "Edit notes.txt with 'new line'" → <tool_call>edit_file:{{"filename": "notes.txt", "content": "new line", "mode": "append"}}</tool_call>
- "Search for myfile.txt" → <tool_call>search_files:{{"query": "myfile.txt"}}</tool_call>
- "System information" → <tool_call>get_system_info:{{}}</tool_call>
- "Disk usage" → <tool_call>get_disk_usage:{{"path": "~"}}</tool_call>
- "Find directory 'my_dir'" → <tool_call>find_directory:{{"directory_name": "my_dir"}}</tool_call>
- "What's my current directory?" → <tool_call>get_current_directory:{{}}

If no tool is needed, respond normally with a conversational response.

User input: {user_input}
Response:"""
        
        # Get LLM response
        llm_response = llm_module.generate_response(prompt, memory_context)
        
        # Check if response contains a tool call
        tool_call = self.parse_tool_call(llm_response)
        
        if tool_call:
            print(f"🔧 Tool call detected: {tool_call['tool_name']}")
            
            # Execute the tool
            tool_result = self.call_tool(tool_call['tool_name'], tool_call['arguments'])
            
            if tool_result['success']:
                # Create a response based on the tool result
                tool_name = tool_call['tool_name']
                result = tool_result['result']
                
                # Update context for memory logging
                context = {
                    "current_directory": os.getcwd(),
                    "tool_used": tool_name,
                    "files_accessed": [result] if "file" in tool_name.lower() else []
                }
                
                if tool_name == "get_current_time":
                    # Make the response more natural based on the format
                    if tool_call['arguments'].get('format') == 'time_only':
                        response = f"It's {result}."
                    elif tool_call['arguments'].get('format') == 'date_only':
                        response = f"Today is {result}."
                    else:
                        response = f"The current time is {result}."
                elif tool_name == "calculate":
                    response = f"The result is {result}."
                elif tool_name == "list_directories":
                    response = result
                elif tool_name == "navigate_directory":
                    response = result
                elif tool_name == "open_file":
                    response = result
                elif tool_name == "write_file":
                    response = result
                elif tool_name == "edit_file":
                    response = result
                elif tool_name == "search_files":
                    response = result
                elif tool_name == "get_system_info":
                    response = result
                elif tool_name == "get_disk_usage":
                    response = result
                elif tool_name == "find_directory":
                    response = result
                elif tool_name == "get_current_directory":
                    response = f"My current directory is: {result}"
                else:
                    response = f"Tool result: {result}"
                
                return response
            else:
                return f"Sorry, I encountered an error: {tool_result['error']}"
        else:
            # No tool call, return the original response
            return llm_response

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
