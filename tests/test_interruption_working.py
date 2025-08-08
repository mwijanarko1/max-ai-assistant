#!/usr/bin/env python3
"""
Test script to verify speech interruption is working
"""

import time
import threading
from tts_module import TTSModule
from simple_interrupt import SimpleInterrupt

def test_speech_interruption():
    """Test that speech interruption works correctly"""
    print("Testing Speech Interruption")
    print("=" * 30)
    
    # Initialize modules
    tts = TTSModule()
    simple_interrupt = SimpleInterrupt()
    
    def on_interruption():
        print("🚨 Interruption detected! Stopping speech...")
        tts.interrupt_speech()
    
    def on_speech_interrupted():
        print("✅ Speech was successfully interrupted!")
    
    # Set up callbacks
    simple_interrupt.set_interruption_callback(on_interruption)
    tts.set_interruption_callback(on_speech_interrupted)
    
    print("Starting interruption listener...")
    simple_interrupt.start_listening()
    
    # Test speech that can be interrupted
    long_speech = """
    Hello! I am Max, your voice assistant. I'm going to speak for a while to test 
    the interruption feature. You can interrupt me at any time by pressing the Enter key. 
    This is a test of the speech interruption capability. The system should be able to 
    stop my speech immediately when you press Enter. Let me continue speaking for a bit 
    longer to give you time to test the interruption feature.
    """
    
    print("\n🗣️  Max will now speak a long sentence. Press ENTER to interrupt!")
    print("💡 The speech should stop immediately when you press Enter.")
    print("💡 Press Ctrl+C to stop the test.\n")
    
    try:
        # Speak the long text
        tts.speak(long_speech, blocking=False)
        
        # Keep the test running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user.")
    finally:
        simple_interrupt.stop_listening()

def test_interruption_timing():
    """Test the timing of interruption"""
    print("\nTesting Interruption Timing")
    print("=" * 30)
    
    tts = TTSModule()
    simple_interrupt = SimpleInterrupt()
    
    def on_interruption():
        print("🚨 Interruption detected!")
        tts.interrupt_speech()
    
    simple_interrupt.set_interruption_callback(on_interruption)
    simple_interrupt.start_listening()
    
    print("I'll speak a short phrase. Try interrupting it quickly!")
    
    try:
        # Speak a short phrase
        tts.speak("This is a test of quick interruption.", blocking=False)
        
        # Keep running for a few seconds
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user.")
    finally:
        simple_interrupt.stop_listening()

def main():
    """Main test function"""
    print("Speech Interruption Test")
    print("=" * 25)
    
    while True:
        print("\nChoose a test:")
        print("1. Test long speech interruption")
        print("2. Test quick interruption timing")
        print("3. Run both tests")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_speech_interruption()
        elif choice == "2":
            test_interruption_timing()
        elif choice == "3":
            test_speech_interruption()
            test_interruption_timing()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
