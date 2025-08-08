#!/usr/bin/env python3
"""
Test STT + LLM + TTS integration with simple interruption feature
Complete voice assistant with speech input and output
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

class MaxVoiceAssistant:
    def __init__(self):
        """Initialize Max Voice Assistant with simple interruption capability"""
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
        print("Initializing STT...")
        self.stt = STTModule(model_name="base")
        
        print("Initializing LLM...")
        self.llm = LLMModule(model_name="mistral:7b")
        
        print("Initializing TTS...")
        self.tts = TTSModule(voice_lang="en", voice_slow=False, stt_module=self.stt)
        
        print("Initializing Tools...")
        self.tools = ToolsModule()
        
        print("Initializing Memory...")
        self.memory = MaxMemory()
        self.memory.start_new_session()
        
        print("Initializing Simple Interrupt...")
        self.simple_interrupt = SimpleInterrupt()
        
        # Set up interruption callbacks
        self.simple_interrupt.set_interruption_callback(self._on_simple_interruption)
        self.tts.set_interruption_callback(self._on_speech_interrupted)
        
        print("\n🎤 Ready! Start speaking...\n")
        print("Available tools:")
        for tool in self.tools.get_tools_schema():
            print(f"  - {tool['name']}: {tool['description']}")
        print("\n💡 Tip: Press ENTER to interrupt Max while he's speaking!")
        print("💡 Tip: Say 'stop' or 'interrupt' as voice commands!")
        print()
    
    def _on_simple_interruption(self):
        """Called when Enter is pressed to interrupt"""
        print("🚨 Simple interruption detected! Stopping Max's speech...")
        self.tts.interrupt_speech()
    
    def _on_speech_interrupted(self):
        """Called when speech is interrupted"""
        print("🛑 Max's speech was interrupted. Listening for your input...")
    
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
            
            print(f"🤖 Max ({end_time - start_time:.2f}s): {response}")
            
            # Log the interaction to memory
            context = {
                "current_directory": os.getcwd(),
                "tool_used": "conversation" if "tool" not in response.lower() else "tool_call"
            }
            self.memory.log_interaction(text, response, context)
            
            # Store current response for potential interruption
            self.current_response = response
            
            # Speak the response
            if response.strip():
                self.tts.speak_response(response)
            
            print("-" * 50)
    
    def start(self):
        """Start the voice assistant"""
        try:
            self.initialize_modules()
            self.is_running = True
            
            # Start simple interrupt listener
            self.simple_interrupt.start_listening()
            
            # Start listening for speech
            self.stt.start_listening(callback=self._on_transcription)
            
        except KeyboardInterrupt:
            print("\n\n👋 Voice assistant stopped by user.")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.is_running = False
            if self.memory:
                self.memory.end_session()
            if self.simple_interrupt:
                self.simple_interrupt.stop_listening()

def main():
    print("Max Voice Assistant with Simple Interruption Feature")
    print("=" * 55)
    print("Speak and I'll respond with voice!")
    print("Press ENTER to interrupt Max while he's speaking.")
    print("Say 'stop' or 'interrupt' as voice commands.")
    print("Say 'go to sleep' to exit gracefully.")
    print("Press Ctrl+C to stop.\n")
    
    assistant = MaxVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
