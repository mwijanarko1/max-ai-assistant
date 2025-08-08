# Max Voice Assistant - Keyboard Interruption Feature

## Overview

The keyboard interruption feature allows users to interrupt Max while he's speaking by pressing the **SPACEBAR**, preventing the microphone from picking up Max's speech and creating a more natural conversation flow.

## How It Works

### 1. Microphone Feedback Prevention
- When Max starts speaking, the STT (Speech-to-Text) module is automatically paused
- This prevents the microphone from picking up Max's speech and transcribing it
- The microphone resumes listening after Max finishes speaking

### 2. Keyboard Interruption Detection
The system supports multiple ways to interrupt Max:

#### A. Spacebar Interruption (Primary Method)
- Press **SPACEBAR** to immediately interrupt Max
- Works instantly and reliably
- No false triggers from background noise
- Cross-platform compatibility with fallback to Enter key

#### B. Voice Commands (Secondary Method)
- Listen for specific voice commands:
  - "stop"
  - "interrupt" 
  - "shut up"
  - "quiet"

#### C. Manual Interruption
- Press Ctrl+C to stop the entire system

### 3. State Management
- Tracks speaking state to prevent false interruptions
- Manages audio buffers to avoid processing old audio
- Provides callbacks for interruption events

## Technical Implementation

### Keyboard Interrupt Module
```python
# New keyboard_interrupt.py module:
- KeyboardInterrupt class for spacebar detection
- Fallback to Enter key if keyboard module unavailable
- Threading for non-blocking keyboard listening
- Cross-platform compatibility
```

### STT Module Enhancements
```python
# Enhanced STTModule:
- Simplified audio processing (removed audio level detection)
- Focus on speech transcription only
- Maintains pause/resume functionality for microphone control
```

### TTS Module Enhancements
```python
# Enhanced TTSModule:
- interrupt_speech(): Stops current speech
- set_interruption_callback(): Sets interruption handler
- Enhanced state management for speaking status
```

### Main Assistant Integration
```python
# Enhanced MaxVoiceAssistant:
- _on_keyboard_interruption(): Handles spacebar press
- _on_speech_interrupted(): Handles speech interruption
- Enhanced transcription handling with stop commands
```

## Installation

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Keyboard Module (Optional)
The system works with or without the keyboard module:
- **With keyboard module**: Press SPACEBAR to interrupt
- **Without keyboard module**: Press ENTER to interrupt (fallback)

```bash
# Install keyboard module for spacebar support
pip install keyboard
```

## Usage

### Running the Main Assistant
```bash
python test_stt_llm_voice.py
```

### Testing the Interruption Feature
```bash
python test_interruption.py
```

### Available Commands
- **Interrupt Max**: Press SPACEBAR or say "stop"
- **Exit**: Say "go to sleep", "goodbye", "bye", "exit", "quit"
- **Stop Command**: Say "stop", "interrupt", "shut up", "quiet"

## Configuration

### Adjusting Keyboard Sensitivity
The keyboard interrupt is immediate and doesn't require configuration. However, you can modify the behavior:

```python
# In keyboard_interrupt.py, you can change the key:
keyboard.wait('space')  # Change 'space' to any other key
```

### Adjusting Microphone Pause Behavior
The microphone pause/resume behavior can be customized in the TTS module:

```python
# In tts_module.py, _speak_sync method:
if self.stt_module:
    self.stt_module.pause_listening()  # Pause before speaking
    # ... speech synthesis ...
    self.stt_module.resume_listening() # Resume after speaking
```

## Benefits

1. **Reliable Interruption**: Spacebar is immediate and doesn't depend on audio levels
2. **No False Triggers**: Keyboard input is precise, no background noise interference
3. **Natural Conversation Flow**: Users don't have to wait for Max to finish speaking
4. **No Feedback Loops**: Microphone doesn't pick up Max's speech
5. **Cross-Platform**: Works on Windows, macOS, and Linux
6. **Fallback Support**: Uses Enter key if spacebar module unavailable

## Troubleshooting

### Issue: Spacebar Not Working
- Install keyboard module: `pip install keyboard`
- Check if another application is capturing the spacebar
- Try the fallback method (press Enter instead)

### Issue: Too Many False Interruptions
- This shouldn't happen with keyboard input
- Check if spacebar is stuck or being pressed repeatedly

### Issue: Not Detecting Interruptions
- Verify keyboard module is installed
- Check if running with appropriate permissions (may need sudo on Linux)
- Try the fallback Enter key method

### Issue: Microphone Still Picking Up Max's Speech
- Verify STT pause/resume is working correctly
- Check audio routing and speaker/microphone setup
- Ensure proper audio isolation between output and input

## Testing

The `test_interruption.py` script provides comprehensive testing:

1. **Keyboard Interruption Test**: Tests the core spacebar functionality
2. **Microphone Feedback Prevention Test**: Verifies Max's speech isn't transcribed
3. **Keyboard Interrupt Only Test**: Tests just the keyboard functionality
4. **Integration Test**: Tests the complete system

Run tests to verify the feature is working correctly in your environment.

## Platform-Specific Notes

### Windows
- Keyboard module works well
- May need to run as administrator for global keyboard capture

### macOS
- Keyboard module works well
- May need accessibility permissions in System Preferences

### Linux
- Keyboard module works well
- May need to run with sudo for global keyboard capture
- Alternative: Use Enter key fallback method

## Future Enhancements

1. **Customizable Keys**: Allow users to choose their preferred interruption key
2. **Gesture Recognition**: Add visual interruption methods
3. **Context-Aware Interruption**: Only allow interruption during certain types of responses
4. **Interruption History**: Track and learn from interruption patterns
5. **Voice Activity Detection**: More sophisticated speech detection algorithms
