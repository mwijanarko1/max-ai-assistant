#!/usr/bin/env python3
"""
Max AI Assistant - Main Entry Point
A voice-enabled AI assistant with memory, tools, and interruption capabilities
"""

import time
import sys
import os
from stt_module import STTModule
from llm_module import LLMModule
from tts_module import TTSModule
from tools_module import ToolsModule
from simple_interrupt import SimpleInterrupt
from memory_module import MaxMemory

class MaxAIAssistant:
    """Main Max AI Assistant class that integrates all modules"""
    
    def __init__(self):
        """Initialize Max AI Assistant with all capabilities"""
        self.stt = None
        self.llm = None
        self.tts = None
        self.tools = None
        self.simple_interrupt = None
        self.memory = None
        self.is_running = False
        self.current_response = None
        
    def initialize_modules(self):
        """Initialize all modules"""
        print("🤖 Initializing Max AI Assistant...")
        print("=" * 50)
        
        print("🎤 Initializing Speech Recognition...")
        self.stt = STTModule(model_name="base")
        
        print("🧠 Initializing Language Model...")
        self.llm = LLMModule(model_name="llama3:8b", fast_mode=True)
        
        print("🔊 Initializing Text-to-Speech...")
        self.tts = TTSModule(voice_lang="en", voice_slow=False, stt_module=self.stt)
        
        print("🛠️  Initializing Tools...")
        self.tools = ToolsModule()
        
        print("🧠 Initializing Memory...")
        self.memory = MaxMemory()
        self.memory.start_new_session()
        
        print("⏸️  Initializing Interruption System...")
        self.simple_interrupt = SimpleInterrupt()
        
        # Set up interruption callbacks
        self.simple_interrupt.set_interruption_callback(self._on_simple_interruption)
        self.tts.set_interruption_callback(self._on_speech_interrupted)
        
        print("\n✅ Max AI Assistant is ready!")
        print("=" * 50)
        print("🎤 Start speaking or press ENTER to interrupt...")
        print("\nAvailable tools:")
        for tool in self.tools.get_tools_schema():
            print(f"  - {tool['name']}: {tool['description']}")
        print("\n💡 Voice Commands:")
        print("  - 'stop' or 'interrupt' to stop Max's speech")
        print("  - 'go to sleep' or 'goodbye' to exit")
        print("  - Press ENTER to interrupt Max while speaking")
        print()
    
    def _on_simple_interruption(self):
        """Called when Enter is pressed to interrupt"""
        print("\n" + "="*50)
        print("🚨 ENTER PRESSED - INTERRUPTING MAX!")
        print("="*50)
        self.tts.interrupt_speech()
    
    def _on_speech_interrupted(self):
        """Called when speech is interrupted"""
        print("\n" + "="*50)
        print("🛑 MAX'S SPEECH INTERRUPTED!")
        print("🎤 LISTENING FOR YOUR VOICE NOW...")
        print("="*50)
        print()
    
    def _on_transcription(self, text):
        """Called when STT transcribes speech"""
        if text.strip():
            print(f"🎤 You said: {text}")
            
            # Check for sleep command
            if any(phrase in text.lower() for phrase in ["go to sleep", "goodbye", "bye", "exit", "quit"]):
                print("🤖 Max: Goodbye! Going to sleep now...")
                self.tts.speak("Goodbye! Going to sleep now.", blocking=True)
                print("\n👋 Max is now sleeping. Goodbye!")
                self.is_running = False
                sys.exit(0)
            
            # Check for stop/interrupt command
            if any(phrase in text.lower() for phrase in ["stop", "interrupt", "shut up", "quiet"]):
                print("🛑 Stop command detected!")
                self.tts.interrupt_speech()
                return
            
            # Get memory context
            memory_context = self.memory.get_session_context()
            
            # Process with tools
            start_time = time.time()
            response = self.tools.process_with_tools(text, self.llm, memory_context)
            end_time = time.time()
            
            # Log the interaction to memory
            context = {
                "current_directory": os.getcwd(),
                "tool_used": "conversation" if response and "tool" not in response.lower() else "tool_call"
            }
            self.memory.log_interaction(text, response, context)
            
            # Store current response for potential interruption
            self.current_response = response
            
            # Speak the response (don't print again, TTS will handle it)
            if response and response.strip():
                self.tts.speak_response(response)
            else:
                print("⚠️  No response generated, skipping speech")
            
            print("-" * 50)
    
    def start(self):
        """Start the Max AI Assistant"""
        try:
            self.initialize_modules()
            self.is_running = True
            
            # Start listening for speech
            self.stt.start_listening(self._on_transcription)
            
            # Start keyboard interruption monitoring
            self.simple_interrupt.start_listening()
            
            # Keep the main thread alive
            while self.is_running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received. Shutting down...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        # End session first to ensure proper archiving
        if self.memory:
            print("📝 Finalizing session memory...")
            self.memory.end_session()
        
        # Stop other modules
        if self.simple_interrupt:
            self.simple_interrupt.stop_listening()
        if self.stt:
            self.stt.stop_listening()
        if self.tts:
            self.tts.cleanup()
        
        print("✅ Cleanup complete!")

def main():
    """Main entry point"""
    print("🚀 Starting Max AI Assistant...")
    assistant = MaxAIAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
