import whisper
import sounddevice as sd
import numpy as np
import threading
import queue
import time
import torch
import warnings
import os
import sys
from typing import Optional, Callable

# Suppress FP16 warning for CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class STTModule:
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        """
        Initialize Speech-to-Text module using Whisper
        
        Args:
            model_name: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run model on ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.is_paused = False  # New: pause state
        self.sample_rate = 16000
        self.chunk_duration = 0.3  # Process 0.3-second chunks for more responsive processing
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        
        # Speech detection parameters
        self.silence_threshold = 0.01  # Threshold for silence detection
        self.silence_duration = 0.15  # Seconds of silence before processing (very fast)
        self.min_speech_duration = 0.1  # Minimum speech duration to process (instant)
        self.max_wait_time = 2.5  # Maximum time to wait before processing anyway
        
        # Load model
        self._load_model()
        
    def _load_model(self):
        """Load Whisper model"""
        print(f"Loading Whisper {self.model_name} model...")
        self.model = whisper.load_model(self.model_name, device=self.device)
        print(f"Whisper {self.model_name} model loaded successfully!")
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input"""
        if status:
            print(f"Audio callback status: {status}")
        # Only process audio if listening and not paused
        if self.is_listening and not self.is_paused:
            # Convert to float32 and normalize
            audio_data = indata.copy().astype(np.float32) / 32768.0
            self.audio_queue.put(audio_data)
    
    def pause_listening(self):
        """Pause audio processing (e.g., when Max is speaking)"""
        self.is_paused = True
        # Clear the audio queue to prevent processing old audio
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        print("🎤 STT paused (Max speaking)")
    
    def resume_listening(self):
        """Resume audio processing"""
        self.is_paused = False
        print("🎤 STT resumed (listening for user)")
    
    def _is_silence(self, audio_chunk: np.ndarray) -> bool:
        """Check if audio chunk is silence"""
        return np.max(np.abs(audio_chunk)) < self.silence_threshold
    
    def _process_audio_chunk(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Process a chunk of audio and return transcription"""
        try:
            # Ensure audio is the right shape
            if len(audio_chunk.shape) > 1:
                audio_chunk = audio_chunk[:, 0]  # Take first channel if stereo
            
            # Run Whisper transcription
            result = self.model.transcribe(audio_chunk, language="en")
            transcription = result["text"].strip()
            
            return transcription if transcription else None
            
        except Exception as e:
            print(f"Error processing audio chunk: {e}")
            return None
    
    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """
        Start listening for speech input
        
        Args:
            callback: Function to call with transcription results
        """
        self.is_listening = True
        self.is_paused = False  # Ensure we start unpaused
        self.callback = callback
        
        print("Starting audio capture...")
        print("Listening continuously... (Press Ctrl+C to stop)")
        
        try:
            with sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                dtype=np.int16,
                blocksize=self.chunk_samples
            ):
                self._process_audio_stream()
                
        except KeyboardInterrupt:
            print("\nStopping audio capture...")
            self.stop_listening()
    
    def _process_audio_stream(self):
        """Process incoming audio stream with silence detection"""
        audio_buffer = []
        silence_start = None
        last_speech_time = time.time()
        
        while self.is_listening:
            try:
                # Skip processing if paused
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                # Get audio chunk from queue
                audio_chunk = self.audio_queue.get(timeout=0.1)
                audio_buffer.append(audio_chunk)
                
                # Check if current chunk is silence
                is_silent = self._is_silence(audio_chunk)
                
                if is_silent:
                    if silence_start is None:
                        silence_start = time.time()
                else:
                    # Speech detected
                    silence_start = None
                    last_speech_time = time.time()
                
                # Process speech when we have enough audio and detect silence
                buffer_duration = len(audio_buffer) * self.chunk_duration
                silence_duration = time.time() - silence_start if silence_start else 0
                
                # Process if we have minimum speech duration and enough silence
                if (buffer_duration >= self.min_speech_duration and 
                    silence_duration >= self.silence_duration and 
                    len(audio_buffer) > 0):
                    
                    # Concatenate audio chunks
                    full_chunk = np.concatenate(audio_buffer)
                    
                    # Process the audio chunk
                    transcription = self._process_audio_chunk(full_chunk)
                    
                    if transcription:
                        print(f"Transcription: {transcription}")
                        if self.callback:
                            self.callback(transcription)
                    
                    # Clear buffer for next chunk
                    audio_buffer = []
                    silence_start = None
                
                # Also process if buffer gets too large or too much time has passed
                elif buffer_duration > 5.0:  # Max 5 seconds (reduced from 10s)
                    full_chunk = np.concatenate(audio_buffer)
                    transcription = self._process_audio_chunk(full_chunk)
                    
                    if transcription:
                        print(f"Transcription: {transcription}")
                        if self.callback:
                            self.callback(transcription)
                    
                    audio_buffer = []
                    silence_start = None
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in audio stream processing: {e}")
                break
    
    def stop_listening(self):
        """Stop listening for speech input"""
        self.is_listening = False
    
    def transcribe_file(self, audio_file_path: str) -> str:
        """
        Transcribe an audio file
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            result = self.model.transcribe(audio_file_path, language="en")
            return result["text"].strip()
        except Exception as e:
            print(f"Error transcribing file: {e}")
            return ""

def test_stt():
    """Test the STT module"""
    print("Testing Speech-to-Text Module")
    print("=" * 40)
    
    # Initialize STT module
    stt = STTModule(model_name="tiny")
    
    # Test with file transcription
    print("\n1. Testing file transcription...")
    # You can add a test audio file here if available
    # result = stt.transcribe_file("test_audio.wav")
    # print(f"File transcription: {result}")
    
    # Test real-time transcription
    print("\n2. Testing real-time transcription...")
    print("Speak for 1 second chunks. Press Ctrl+C to stop.")
    
    def on_transcription(text):
        print(f"Real-time: {text}")
    
    stt.start_listening(callback=on_transcription)

if __name__ == "__main__":
    test_stt()
