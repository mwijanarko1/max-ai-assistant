#!/usr/bin/env python3
"""
Test script for Max's keyboard interruption feature
Demonstrates how to interrupt Max using the spacebar
"""

import time
import sys
from stt_module import STTModule
from tts_module import TTSModule
from keyboard_interrupt import KeyboardInterrupt

def test_keyboard_interruption_feature():
    """Test the keyboard interruption feature"""
    print("Max Keyboard Interruption Feature Test")
    print("=" * 45)
    print("This test demonstrates the keyboard interruption feature.")
    print("Max will speak a long sentence, and you can interrupt by:")
    print("1. Pressing SPACEBAR (keyboard interruption)")
    print("2. Saying 'stop' or 'interrupt' (voice command)")
    print("3. Pressing Ctrl+C (manual stop)")
    print("\nPress Enter to start the test...")
    input()
    
    try:
        # Initialize modules
        print("Initializing STT...")
        stt = STTModule(model_name="tiny")  # Use tiny for faster testing
        
        print("Initializing TTS...")
        tts = TTSModule(voice_lang="en", voice_slow=False, stt_module=stt)
        
        print("Initializing Keyboard Interrupt...")
        kb_interrupt = KeyboardInterrupt()
        
        # Set up callbacks
        kb_interrupt.set_interruption_callback(lambda: print("🚨 Keyboard interruption detected!"))
        tts.set_interruption_callback(lambda: print("🛑 Speech interrupted!"))
        
        print("\n🎤 Starting test...\n")
        
        def on_transcription(text):
            """Handle transcription"""
            if text.strip():
                print(f"🎤 You said: {text}")
                
                # Check for stop commands
                if any(phrase in text.lower() for phrase in ["stop", "interrupt", "shut up", "quiet"]):
                    print("🛑 Stop command detected!")
                    tts.interrupt_speech()
                    return
                
                # Check for exit
                if any(phrase in text.lower() for phrase in ["exit", "quit", "end test"]):
                    print("👋 Ending test...")
                    sys.exit(0)
        
        # Start keyboard interrupt listener
        kb_interrupt.start_listening()
        
        # Start listening
        stt.start_listening(callback=on_transcription)
        
        # Give a moment for initialization
        time.sleep(2)
        
        # Test speech that can be interrupted
        long_speech = """
        Hello! I am Max, your voice assistant. I'm going to speak for a while to demonstrate 
        the keyboard interruption feature. You can interrupt me at any time by pressing the 
        spacebar or saying the word 'stop'. This is a test of the keyboard interruption 
        capability that prevents the microphone from picking up my speech while still allowing 
        you to interrupt me when needed. The system uses keyboard input to identify when you 
        want to interrupt, and it also listens for specific voice commands like 'stop' or 
        'interrupt'. This creates a more natural conversation flow where you don't have to 
        wait for me to finish speaking before you can respond or ask a new question.
        """
        
        print("🗣️  Max will now speak a long sentence. Try interrupting!")
        print("💡 Press SPACEBAR or say 'stop' to interrupt.")
        print("💡 Say 'exit' to end the test.\n")
        
        # Speak the long text
        tts.speak(long_speech, blocking=False)
        
        # Keep the test running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Test stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_microphone_feedback_prevention():
    """Test that microphone doesn't pick up Max's speech"""
    print("\nMicrophone Feedback Prevention Test")
    print("=" * 40)
    print("This test verifies that the microphone doesn't pick up Max's speech.")
    print("Max will speak while the microphone is active but paused.")
    print("You should NOT see transcriptions of Max's speech.\n")
    
    try:
        # Initialize modules
        stt = STTModule(model_name="tiny")
        tts = TTSModule(voice_lang="en", voice_slow=False, stt_module=stt)
        
        def on_transcription(text):
            """Handle transcription"""
            if text.strip():
                print(f"🎤 Detected: {text}")
                if any(word in text.lower() for word in ["max", "assistant", "speaking", "interruption"]):
                    print("⚠️  WARNING: Microphone may be picking up Max's speech!")
                else:
                    print("✅ Good: This appears to be user speech, not Max's speech.")
        
        # Start listening
        stt.start_listening(callback=on_transcription)
        
        # Give a moment for initialization
        time.sleep(2)
        
        print("🗣️  Max will speak now. Watch for any transcriptions...")
        
        # Speak some text
        test_speech = "Hello, I am Max speaking. This is a test of microphone feedback prevention."
        tts.speak(test_speech, blocking=True)
        
        print("\n✅ Test completed. If you didn't see transcriptions of Max's speech, the feature is working!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_keyboard_interrupt_only():
    """Test just the keyboard interrupt functionality"""
    print("\nKeyboard Interrupt Test")
    print("=" * 30)
    print("This test focuses on the keyboard interrupt functionality.")
    print("Press SPACEBAR to trigger interruption.")
    print("Press Ctrl+C to stop the test.\n")
    
    try:
        kb_interrupt = KeyboardInterrupt()
        
        def on_interruption():
            print("✅ Keyboard interruption working correctly!")
        
        kb_interrupt.set_interruption_callback(on_interruption)
        kb_interrupt.start_listening()
        
        print("Press SPACEBAR to test interruption...")
        
        # Keep the test running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("Max Voice Assistant - Keyboard Interruption Feature Tests")
    print("=" * 60)
    
    while True:
        print("\nChoose a test:")
        print("1. Test keyboard interruption feature")
        print("2. Test microphone feedback prevention")
        print("3. Test keyboard interrupt only")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_keyboard_interruption_feature()
        elif choice == "2":
            test_microphone_feedback_prevention()
        elif choice == "3":
            test_keyboard_interrupt_only()
        elif choice == "4":
            test_keyboard_interruption_feature()
            test_microphone_feedback_prevention()
            test_keyboard_interrupt_only()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
