#!/usr/bin/env python3
"""
Test Voice Assistant with Memory
"""

from memory_module import MaxMemory
from llm_module import LLMModule
from tools_module import ToolsModule
import os

def test_voice_with_memory():
    """Test voice assistant with memory"""
    print("Testing Voice Assistant with Memory")
    print("=" * 40)
    
    try:
        # Initialize components
        memory = MaxMemory()
        llm = LLMModule(model_name="mistral:7b")
        tools = ToolsModule()
        
        # Start new session
        memory.start_new_session()
        
        # Simulate a conversation flow
        conversation = [
            "What directory are we in?",
            "Navigate to desktop",
            "What files are here?",
            "Open the apple.txt file",
            "What's in it?",
            "Edit it with more content about Apple's history"
        ]
        
        for i, user_input in enumerate(conversation, 1):
            print(f"\n🎤 User: {user_input}")
            
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
            
            print(f"🤖 Max: {response}")
            print(f"📊 Memory interactions: {memory.get_interaction_count()}")
            
            print("-" * 50)
        
        # End session
        memory.end_session()
        
        print("\n✅ Voice assistant with memory test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_voice_with_memory()
