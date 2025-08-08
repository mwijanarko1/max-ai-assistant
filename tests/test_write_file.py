#!/usr/bin/env python3
"""
Test write_file functionality
"""

from tools_module import ToolsModule
from llm_module import LLMModule

def test_write_file():
    """Test the write_file functionality"""
    print("Testing Write File Functionality")
    print("=" * 40)
    
    try:
        # Initialize modules
        tools = ToolsModule()
        llm = LLMModule(model_name="mistral:7b")
        
        # Test cases
        test_inputs = [
            "Can you write about the history of Apple?",
            "Write about Python programming",
            "Create a file about machine learning"
        ]
        
        for test_input in test_inputs:
            print(f"\n🧪 Testing: {test_input}")
            print("-" * 50)
            
            # Process the input
            response = tools.process_with_tools(test_input, llm)
            print(f"📝 Response: {response}")
            
            print("\n" + "="*50)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_write_file()
