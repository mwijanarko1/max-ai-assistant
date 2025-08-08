#!/usr/bin/env python3
"""
Simple Interrupt Module for Max
Uses a simpler approach for interruption that works on all platforms
"""

import threading
import time
import sys
import os
from typing import Optional, Callable

class SimpleInterrupt:
    def __init__(self):
        """Initialize simple interrupt listener"""
        self.is_listening = False
        self.interruption_callback = None
        self.listener_thread = None
    
    def set_interruption_callback(self, callback: Callable[[], None]):
        """Set callback for interruption events"""
        self.interruption_callback = callback
    
    def start_listening(self):
        """Start listening for interruption using Enter key"""
        self.is_listening = True
        print("⌨️  Simple interrupt listener started. Press ENTER to interrupt Max.")
        
        def listen_for_enter():
            while self.is_listening:
                try:
                    input()  # Wait for Enter key
                    if self.is_listening and self.interruption_callback:
                        print("🚨 Enter pressed! Interrupting Max...")
                        self.interruption_callback()
                except KeyboardInterrupt:
                    break
                except EOFError:
                    # Handle case where input() fails
                    break
                except Exception as e:
                    print(f"Error in interrupt listener: {e}")
                    break
        
        self.listener_thread = threading.Thread(target=listen_for_enter, daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for keyboard input"""
        self.is_listening = False
        print("⌨️  Simple interrupt listener stopped.")

def test_simple_interrupt():
    """Test the simple interrupt functionality"""
    print("Testing Simple Interrupt Module")
    print("=" * 35)
    
    def on_interruption():
        print("✅ Simple interruption working!")
    
    simple_interrupt = SimpleInterrupt()
    simple_interrupt.set_interruption_callback(on_interruption)
    
    print("Press ENTER to test interruption.")
    print("Press Ctrl+C to stop the test.")
    
    try:
        simple_interrupt.start_listening()
        
        # Keep the test running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user.")
    finally:
        simple_interrupt.stop_listening()

if __name__ == "__main__":
    test_simple_interrupt()
