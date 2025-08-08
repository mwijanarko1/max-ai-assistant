#!/usr/bin/env python3
"""
Simple test to debug tool calling
"""

from tools_module import ToolsModule
from llm_module import LLMModule

def test_simple_tool():
    """Test simple tool calling"""
    print("Testing Simple Tool Call")
    print("=" * 30)
    
    try:
        tools = ToolsModule()
        llm = LLMModule(model_name="mistral:7b")
        
        # Test direct tool call
        print("\n1. Testing direct tool call:")
        result = tools.call_tool("get_current_directory", {})
        print(f"Direct result: {result}")
        
        # Test with LLM
        print("\n2. Testing with LLM:")
        response = tools.process_with_tools("What directory are we in?", llm)
        print(f"LLM response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_tool()
