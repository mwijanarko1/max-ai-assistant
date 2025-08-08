#!/usr/bin/env python3
"""
Test script to verify the fixes for tool calling and keyboard interrupt
"""

import time
from tools_module import ToolsModule
from llm_module import LLMModule
from keyboard_interrupt import KeyboardInterrupt

def test_tool_calling_fixes():
    """Test that tool calling is more conservative now"""
    print("Testing Tool Calling Fixes")
    print("=" * 30)
    
    tools = ToolsModule()
    llm = LLMModule(model_name="mistral:7b")
    
    # Test cases that should NOT trigger tool calls
    conversational_inputs = [
        "Hey Max",
        "How are you?",
        "Tell me about Islam",
        "What can you do?",
        "Hello there",
        "Good morning"
    ]
    
    print("Testing conversational inputs (should NOT trigger tools):")
    for input_text in conversational_inputs:
        print(f"\nInput: {input_text}")
        response = tools.process_with_tools(input_text, llm)
        print(f"Response: {response[:100]}...")
        time.sleep(1)  # Small delay to avoid overwhelming the LLM
    
    # Test cases that SHOULD trigger tool calls
    tool_inputs = [
        "What time is it?",
        "Calculate 2 + 3",
        "List directories",
        "What's the date today?"
    ]
    
    print("\n" + "="*50)
    print("Testing tool inputs (should trigger tools):")
    for input_text in tool_inputs:
        print(f"\nInput: {input_text}")
        response = tools.process_with_tools(input_text, llm)
        print(f"Response: {response}")
        time.sleep(1)

def test_keyboard_interrupt_fix():
    """Test the keyboard interrupt fix"""
    print("\nTesting Keyboard Interrupt Fix")
    print("=" * 30)
    
    kb_interrupt = KeyboardInterrupt()
    
    def on_interruption():
        print("✅ Keyboard interruption working!")
    
    kb_interrupt.set_interruption_callback(on_interruption)
    
    print("Starting keyboard interrupt listener...")
    print("Press SPACEBAR (or ENTER if fallback) to test interruption.")
    print("Press Ctrl+C to stop the test.")
    
    try:
        kb_interrupt.start_listening()
        
        # Keep the test running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user.")
    finally:
        kb_interrupt.stop_listening()

def main():
    """Main test function"""
    print("Max Assistant - Fix Verification Tests")
    print("=" * 40)
    
    while True:
        print("\nChoose a test:")
        print("1. Test tool calling fixes")
        print("2. Test keyboard interrupt fix")
        print("3. Run both tests")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_tool_calling_fixes()
        elif choice == "2":
            test_keyboard_interrupt_fix()
        elif choice == "3":
            test_tool_calling_fixes()
            test_keyboard_interrupt_fix()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
