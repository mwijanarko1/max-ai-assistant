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
    
    def _list_directories(self, path: str = ".") -> str:
        """List directories and files in the specified path"""
        try:
            # Security: Only allow operations in current directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            
            # Ensure the requested path is within the current directory
            if not requested_path.startswith(current_dir):
                return "Error: Access denied - can only access files in current directory and subdirectories"
            
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
            result = f"Current directory: {os.path.basename(requested_path)}\n"
            
            if directories:
                result += f"Directories: {', '.join(directories[:5])}\n"
            
            if files:
                result += f"Files: {', '.join(files[:8])}\n"
            
            if not directories and not files:
                result += "No visible files or directories found.\n"
            
            return result
            
        except FileNotFoundError:
            return f"Error: Directory '{path}' not found"
        except PermissionError:
            return f"Error: Permission denied for '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _navigate_directory(self, path: str) -> str:
        """Navigate to a specific directory"""
        try:
            # Security: Only allow operations in current directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            
            # Ensure the requested path is within the current directory
            if not requested_path.startswith(current_dir):
                return "Error: Access denied - can only access files in current directory and subdirectories"
            
            if os.path.isdir(requested_path):
                # Change to the directory
                os.chdir(requested_path)
                return f"Successfully navigated to: {os.path.basename(requested_path)}"
            else:
                return f"Error: '{path}' is not a directory"
                
        except FileNotFoundError:
            return f"Error: Directory '{path}' not found"
        except PermissionError:
            return f"Error: Permission denied for '{path}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _open_file(self, filename: str, path: str = ".") -> str:
        """Open and read the contents of a file"""
        try:
            # Security: Only allow operations in current directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            
            # Ensure the requested path is within the current directory
            if not requested_path.startswith(current_dir):
                return "Error: Access denied - can only access files in current directory and subdirectories"
            
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
            # Security: Only allow operations in current directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            
            # Ensure the requested path is within the current directory
            if not requested_path.startswith(current_dir):
                return "Error: Access denied - can only access files in current directory and subdirectories"
            
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
            # Security: Only allow operations in current directory and subdirectories
            current_dir = os.getcwd()
            requested_path = os.path.abspath(path)
            
            # Ensure the requested path is within the current directory
            if not requested_path.startswith(current_dir):
                return "Error: Access denied - can only access files in current directory and subdirectories"
            
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
    
    def parse_tool_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse tool call from LLM response
        Expected format: <tool_call>tool_name:arguments</tool_call>
        """
        import re
        
        # Look for tool call pattern
        pattern = r'<tool_call>(.*?):(.*?)</tool_call>'
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
    
    def process_with_tools(self, user_input: str, llm_module) -> str:
        """
        Process user input with tool calling capability
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
            "navigate": any(word in user_input.lower() for word in ["navigate", "go to", "change directory", "cd"]),
            "open_file": any(word in user_input.lower() for word in ["open", "read", "show file", "file contents"]),
            "write_file": any(word in user_input.lower() for word in ["write", "save", "create file with content"]),
            "edit_file": any(word in user_input.lower() for word in ["edit", "append", "add to file", "modify file"])
        }
        
        # If no explicit tool request, respond conversationally
        if not any(tool_requests.values()):
            # Generate conversational response without tools
            prompt = f"""You are Max, a helpful voice assistant. Respond conversationally to the user's input.

User input: {user_input}
Response:"""
            return llm_module.generate_response(prompt)
        
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
- "Edit notes.txt with 'new line'" → <tool_call>edit_file:{{"filename": "notes.txt", "content": "new line", "mode": "append"}}</tool_call>

If no tool is needed, respond normally with a conversational response.

User input: {user_input}
Response:"""
        
        # Get LLM response
        llm_response = llm_module.generate_response(prompt)
        
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
                
                if tool_name == "get_current_time":
                    # Make the response more natural based on the format
                    if tool_call['arguments'].get('format') == 'time_only':
                        return f"It's {result}."
                    elif tool_call['arguments'].get('format') == 'date_only':
                        return f"Today is {result}."
                    else:
                        return f"The current time is {result}."
                elif tool_name == "calculate":
                    return f"The result is {result}."
                elif tool_name == "list_directories":
                    return result
                elif tool_name == "navigate_directory":
                    return result
                elif tool_name == "open_file":
                    return result
                elif tool_name == "write_file":
                    return result
                elif tool_name == "edit_file":
                    return result
                else:
                    return f"Tool result: {result}"
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
