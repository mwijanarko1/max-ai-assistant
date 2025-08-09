#!/usr/bin/env python3
"""
Simple Interrupt Module for Max
Uses a more robust approach for interruption that works with audio input systems
"""

import threading
import time
import sys
import os
import select
from typing import Optional, Callable

# Import msvcrt only on Windows
if os.name == 'nt':
    import msvcrt

class SimpleInterrupt:
    def __init__(self):
        """Initialize simple interrupt listener"""
        self.is_listening = False
        self.interruption_callback = None
        self.listener_thread = None
    
    def set_interruption_callback(self, callback: Callable[[], None]):
        """Set callback for interruption events"""
        self.interruption_callback = callback
    
    def _check_input_available(self):
        """Check if input is available without blocking"""
        if os.name == 'nt':  # Windows
            return msvcrt.kbhit()
        else:  # Unix/Linux/macOS
            return select.select([sys.stdin], [], [], 0)[0]
    
    def _get_input(self):
        """Get input without blocking"""
        if os.name == 'nt':  # Windows
            if msvcrt.kbhit():
                return msvcrt.getch()
        else:  # Unix/Linux/macOS
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.readline()
        return None
    
    def start_listening(self):
        """Start listening for interruption using Enter key"""
        self.is_listening = True
        print("⌨️  Simple interrupt listener started. Press ENTER to interrupt Max.")
        
        def listen_for_enter():
            while self.is_listening:
                try:
                    # Use non-blocking input check
                    if self._check_input_available():
                        input_data = self._get_input()
                        if input_data and (input_data.strip() == '' or input_data.strip() == '\n'):
                            if self.is_listening and self.interruption_callback:
                                print("🚨 Enter pressed! Interrupting Max...")
                                self.interruption_callback()
                    else:
                        # Small sleep to prevent high CPU usage
                        time.sleep(0.1)
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
