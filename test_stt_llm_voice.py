#!/usr/bin/env python3
"""
Test STT + LLM + TTS integration with keyboard interruption feature
Complete voice assistant with speech input and output
"""

import time
import sys
from stt_module import STTModule
from llm_module import LLMModule
from tts_module import TTSModule
from tools_module import ToolsModule
from keyboard_interrupt import KeyboardInterrupt

class MaxVoiceAssistant:
    def __init__(self):
        """Initialize Max Voice Assistant with keyboard interruption capability"""
        self.stt = None
        self.llm = None
        self.tts = None
        self.tools = None
        self.keyboard_interrupt = None
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
        
        print("Initializing Keyboard Interrupt...")
        self.keyboard_interrupt = KeyboardInterrupt()
        
        # Set up interruption callbacks
        self.keyboard_interrupt.set_interruption_callback(self._on_keyboard_interruption)
        self.tts.set_interruption_callback(self._on_speech_interrupted)
        
        print("\n🎤 Ready! Start speaking...\n")
        print("Available tools:")
        for tool in self.tools.get_tools_schema():
            print(f"  - {tool['name']}: {tool['description']}")
        print("\n💡 Tip: Press SPACEBAR to interrupt Max while he's speaking!")
        print("💡 Tip: Say 'stop' or 'interrupt' as voice commands!")
        print()
    
    def _on_keyboard_interruption(self):
        """Called when spacebar is pressed to interrupt"""
        print("🚨 Keyboard interruption detected! Stopping Max's speech...")
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
            
            # Process with tools
            start_time = time.time()
            response = self.tools.process_with_tools(text, self.llm)
            end_time = time.time()
            
            print(f"🤖 Max ({end_time - start_time:.2f}s): {response}")
            
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
            
            # Start keyboard interrupt listener
            self.keyboard_interrupt.start_listening()
            
            # Start listening for speech
            self.stt.start_listening(callback=self._on_transcription)
            
        except KeyboardInterrupt:
            print("\n\n👋 Voice assistant stopped by user.")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.is_running = False
            if self.keyboard_interrupt:
                self.keyboard_interrupt.stop_listening()

def main():
    print("Max Voice Assistant with Keyboard Interruption Feature")
    print("=" * 55)
    print("Speak and I'll respond with voice!")
    print("Press SPACEBAR to interrupt Max while he's speaking.")
    print("Say 'stop' or 'interrupt' as voice commands.")
    print("Say 'go to sleep' to exit gracefully.")
    print("Press Ctrl+C to stop.\n")
    
    assistant = MaxVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
