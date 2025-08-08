#!/usr/bin/env python3
"""
Keyboard Interrupt Module for Max
Listens for spacebar press to interrupt Max's speech
"""

import threading
import time
import sys
import os
import platform
from typing import Optional, Callable

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️  keyboard module not available. Install with: pip install keyboard")

class KeyboardInterrupt:
    def __init__(self):
        """Initialize keyboard interrupt listener"""
        self.is_listening = False
        self.interruption_callback = None
        self.listener_thread = None
        self.admin_error_shown = False
        self.os_type = platform.system().lower()
        
        if not KEYBOARD_AVAILABLE:
            print("❌ Keyboard module not available. Using fallback method.")
    
    def set_interruption_callback(self, callback: Callable[[], None]):
        """Set callback for interruption events"""
        self.interruption_callback = callback
    
    def start_listening(self):
        """Start listening for spacebar press"""
        if not KEYBOARD_AVAILABLE:
            print("⚠️  Keyboard module not available. Using fallback method.")
            self._start_fallback_listener()
            return
        
        # On macOS, keyboard module often has permission issues
        if self.os_type == "darwin":  # macOS
            print("🍎 macOS detected. Using fallback method for better compatibility.")
            self._start_fallback_listener()
            return
        
        self.is_listening = True
        print("⌨️  Keyboard interrupt listener started. Press SPACEBAR to interrupt Max.")
        
        def listen_for_spacebar():
            try:
                keyboard.wait('space')
                if self.is_listening and self.interruption_callback:
                    print("🚨 Spacebar pressed! Interrupting Max...")
                    self.interruption_callback()
            except OSError as e:
                error_msg = str(e)
                if any(msg in error_msg for msg in ["Error 13", "Must be run as administrator", "Permission denied"]):
                    if not self.admin_error_shown:
                        print("⚠️  Keyboard module requires special permissions.")
                        if self.os_type == "darwin":
                            print("💡 On macOS, this requires accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility")
                            print("💡 For now, using ENTER key for interruption.")
                        elif self.os_type == "linux":
                            print("💡 On Linux, run with sudo for global keyboard capture")
                        else:
                            print("💡 On Windows, run as administrator for global keyboard capture")
                        self.admin_error_shown = True
                    self._start_fallback_listener()
                else:
                    print(f"Error in keyboard listener: {e}")
                    self._start_fallback_listener()
            except Exception as e:
                print(f"Error in keyboard listener: {e}")
                self._start_fallback_listener()
        
        self.listener_thread = threading.Thread(target=listen_for_spacebar, daemon=True)
        self.listener_thread.start()
    
    def _start_fallback_listener(self):
        """Fallback method using input() for systems without keyboard module or admin privileges"""
        if self.is_listening:
            return  # Already listening
        
        self.is_listening = True
        print("⌨️  Fallback keyboard listener started. Press ENTER to interrupt Max.")
        
        def fallback_listener():
            while self.is_listening:
                try:
                    input()  # Wait for Enter key
                    if self.is_listening and self.interruption_callback:
                        print("🚨 Enter pressed! Interrupting Max...")
                        self.interruption_callback()
                except KeyboardInterrupt:
                    break
                except EOFError:
                    # Handle case where input() fails (e.g., in non-interactive environments)
                    break
                except Exception as e:
                    print(f"Error in fallback listener: {e}")
                    break
        
        self.listener_thread = threading.Thread(target=fallback_listener, daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for keyboard input"""
        self.is_listening = False
        print("⌨️  Keyboard interrupt listener stopped.")

def test_keyboard_interrupt():
    """Test the keyboard interrupt functionality"""
    print("Testing Keyboard Interrupt Module")
    print("=" * 40)
    
    if not KEYBOARD_AVAILABLE:
        print("❌ Keyboard module not available. Install with: pip install keyboard")
        print("Using fallback method with Enter key.")
    
    def on_interruption():
        print("✅ Interruption callback triggered!")
    
    kb_interrupt = KeyboardInterrupt()
    kb_interrupt.set_interruption_callback(on_interruption)
    
    print("Press SPACEBAR (or ENTER in fallback mode) to test interruption.")
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

if __name__ == "__main__":
    test_keyboard_interrupt()
