#!/usr/bin/env python3
"""
Test Memory Integration with Voice Assistant
"""

from memory_module import MaxMemory
from llm_module import LLMModule
from tools_module import ToolsModule
import os

def test_memory_integration():
    """Test memory integration with voice assistant components"""
    print("Testing Memory Integration")
    print("=" * 40)
    
    try:
        # Initialize components
        memory = MaxMemory()
        llm = LLMModule(model_name="mistral:7b")
        tools = ToolsModule()
        
        # Start new session
        memory.start_new_session()
        
        # Test conversation flow
        test_conversations = [
            "What directory are we in?",
            "Navigate to desktop",
            "What files are here?",
            "Open the Apple file",
            "What's in it?",
            "Edit it with more content about Apple's history"
        ]
        
        for i, user_input in enumerate(test_conversations, 1):
            print(f"\n🧪 Test {i}: {user_input}")
            print("-" * 50)
            
            # Get memory context
            memory_context = memory.get_session_context()
            
            # Process with tools
            response = tools.process_with_tools(user_input, llm, memory_context)
            
            # Log interaction
            context = {
                "current_directory": os.getcwd(),
                "tool_used": "conversation" if "tool" not in response.lower() else "tool_call"
            }
            memory.log_interaction(user_input, response, context)
            
            print(f"📝 Response: {response}")
            print(f"📊 Memory interactions: {memory.get_interaction_count()}")
            
            print("\n" + "="*50)
        
        # End session
        memory.end_session()
        
        print("\n✅ Memory integration test completed!")
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")

if __name__ == "__main__":
    test_memory_integration()
