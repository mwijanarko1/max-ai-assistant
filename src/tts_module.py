#!/usr/bin/env python3
"""
Text-to-Speech Module for Max
Uses Google TTS (gTTS) for high-quality voices with interruption support
"""

import os
import tempfile
import threading
import time
import subprocess
import signal
import platform
from gtts import gTTS
from typing import Optional, Callable

class TTSModule:
    def __init__(self, voice_lang: str = "en", voice_slow: bool = False, stt_module=None):
        """
        Initialize TTS module using Google TTS
        
        Args:
            voice_lang: Language code (e.g., "en", "en-us", "en-gb")
            voice_slow: Whether to speak slowly
            stt_module: Optional STT module to pause during speech
        """
        self.voice_lang = voice_lang
        self.voice_slow = voice_slow
        self.is_speaking = False
        self.current_speech_process = None  # Track current speech process
        self.temp_dir = tempfile.mkdtemp()
        self.stt_module = stt_module  # Reference to STT module for pausing
        self.interruption_callback = None  # Callback for interruption events
        self.speech_thread = None  # Track the speech thread
        self.os_type = platform.system().lower()
        
        print(f"✅ TTS initialized successfully!")
        print(f"🎤 Language: {voice_lang}")
        print(f"🐌 Slow speech: {voice_slow}")
    
    def set_interruption_callback(self, callback: Callable[[], None]):
        """Set callback for interruption events"""
        self.interruption_callback = callback
    
    def speak(self, text: str, blocking: bool = False):
        """
        Speak the given text
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not text.strip():
            return
        
        print("🎤 TTS: Converting text to speech...")
        
        if blocking:
            # Speak synchronously
            self._speak_sync(text)
        else:
            # Speak asynchronously
            self.speech_thread = threading.Thread(target=self._speak_sync, args=(text,))
            self.speech_thread.daemon = True
            self.speech_thread.start()
    
    def _speak_sync(self, text: str):
        """Synchronous speech synthesis"""
        temp_file = None
        try:
            # Set speaking flag
            self.is_speaking = True
            
            # Pause STT listening if we have a reference
            if self.stt_module:
                self.stt_module.pause_listening()
            
            # Create TTS object
            print("🌐 TTS: Converting text to speech...")
            tts = gTTS(text=text, lang=self.voice_lang, slow=self.voice_slow)
            
            # Generate temporary file with unique name
            temp_file = os.path.join(self.temp_dir, f"speech_{int(time.time() * 1000)}.mp3")
            tts.save(temp_file)
            
            # Play the audio with process tracking for interruption
            self._play_audio_with_interruption(temp_file)
            
            # Resume STT listening after speech
            if self.stt_module:
                self.stt_module.resume_listening()
                
        except Exception as e:
            print(f"❌ TTS error: {e}")
        finally:
            # Always clean up the temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            # Make sure to resume STT even if there's an error
            if self.stt_module:
                self.stt_module.resume_listening()
            # Always reset speaking flag
            self.is_speaking = False
    
    def _play_audio_with_interruption(self, audio_file: str):
        """Play audio with interruption capability using subprocess"""
        try:
            # Use system audio player that can be interrupted
            if self.os_type == "darwin":  # macOS
                cmd = ["afplay", audio_file]
            elif self.os_type == "linux":
                cmd = ["aplay", audio_file]
            else:  # Windows
                cmd = ["start", "/min", "cmd", "/c", f'"{audio_file}"']
            
            # Start the audio process
            print("🔊 TTS: Playing audio...")
            self.current_speech_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for the process to complete (unless interrupted)
            while self.current_speech_process.poll() is None and self.is_speaking:
                time.sleep(0.1)
            
            # If we're no longer speaking, kill the process
            if not self.is_speaking and self.current_speech_process.poll() is None:
                self.current_speech_process.terminate()
                try:
                    self.current_speech_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.current_speech_process.kill()
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            # Fallback to playsound if subprocess fails
            try:
                from playsound import playsound
                playsound(audio_file)
            except Exception as fallback_error:
                print(f"Fallback audio also failed: {fallback_error}")
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.is_speaking:
            self.is_speaking = False
            print("🛑 SPEECH STOPPED!")
            
            # Kill the current speech process if it exists
            if self.current_speech_process and self.current_speech_process.poll() is None:
                try:
                    self.current_speech_process.terminate()
                    self.current_speech_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.current_speech_process.kill()
                except Exception as e:
                    print(f"Error stopping speech process: {e}")
            
            # Resume STT listening immediately
            if self.stt_module:
                self.stt_module.resume_listening()
    
    def interrupt_speech(self):
        """Interrupt current speech"""
        if self.is_speaking:
            print("🚨 SPEECH INTERRUPTED!")
            self.stop_speaking()
            
            # Call interruption callback if set
            if self.interruption_callback:
                self.interruption_callback()
    
    def speak_response(self, response: str):
        """
        Speak a Max response with proper formatting
        
        Args:
            response: Response text to speak
        """
        if not response.strip():
            return
        
        # Clean up response for speech
        clean_response = response.strip()
        
        # Remove any thinking tokens or extra formatting
        if clean_response.startswith("🤖 Max"):
            # Extract just the response part
            parts = clean_response.split(":", 1)
            if len(parts) > 1:
                clean_response = parts[1].strip()
        
        # Remove emojis from the response
        clean_response = self._remove_emojis(clean_response)
        
        print(f"🗣️  Max speaking: {clean_response}")
        self.speak(clean_response, blocking=False)
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        import re
        # Remove emoji characters (Unicode emoji ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return True  # gTTS is always available if installed
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_voice(self):
        """Test the TTS system"""
        print("Testing TTS Module")
        print("=" * 30)
        
        test_phrases = [
            "Hello, I am Max.",
            "How can I assist you today?",
            "The weather is sunny with a high of 75 degrees.",
            "Your calendar shows a meeting at 2 PM."
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n{i}. Speaking: {phrase}")
            self.speak(phrase, blocking=True)
            time.sleep(0.5)
        
        print("\n✅ TTS test completed!")

def test_tts():
    """Test the TTS module"""
    tts = TTSModule()
    tts.test_voice()

if __name__ == "__main__":
    test_tts()
