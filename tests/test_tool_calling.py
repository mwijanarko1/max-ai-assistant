#!/usr/bin/env python3
"""
Test tool calling functionality with text input
"""

from llm_module import LLMModule
from tools_module import ToolsModule

def test_tool_calling():
    print("Testing Tool Calling")
    print("=" * 30)
    
    # Initialize modules
    llm = LLMModule(model_name="mistral:7b")
    tools = ToolsModule()
    
    # Test cases
    test_inputs = [
        "What time is it?",
        "Tell me the current time",
        "What's the date today?",
        "Hello, how are you?",
        "What time is it right now?",
        "What is 2 + 3?",
        "Calculate 10 * 5",
        "What's 15 divided by 3?",
        "List directories",
        "Show files",
        "Navigate to docs",
        "Go to docs"
    ]
    
    for test_input in test_inputs:
        print(f"\n🎤 Input: {test_input}")
        
        # Process with tools
        response = tools.process_with_tools(test_input, llm)
        
        print(f"🤖 Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_tool_calling()
