# Max AI Assistant - Voice AI Assistant

A complete voice-activated AI assistant that listens, thinks, and responds with natural speech. Built with Whisper for speech recognition, Mistral 7B for language processing, and Google TTS for speech synthesis.

## 🚀 Quick Start

### 1. Install Dependencies

First, install system dependencies:
```bash
brew install portaudio
```

Then install Python packages:
```bash
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
```

### 2. Start Max AI Assistant
```bash
python3 run_max.py
```

Or run directly from the source:
```bash
cd src
python3 max_ai_assistant.py
```

Speak naturally and Max will respond with voice! Say "go to sleep" to exit gracefully.

## ✨ Features

- **🎤 Real-time Speech Recognition** - Whisper Base model with <1s latency
- **🧠 Intelligent Responses** - Mistral 7B LLM via Ollama for natural conversations
- **🗣️ Natural Speech Output** - Google TTS for high-quality voice responses
- **⏸️ Smart Audio Control** - Automatically pauses listening when speaking to prevent feedback
- **😴 Voice Commands** - Say "go to sleep", "goodbye", "bye", "exit", or "quit" to exit
- **⚡ Fast Performance** - <4s end-to-end response time
- **💾 Memory Efficient** - Uses <8GB RAM total

## 🏗️ Architecture

```
User Speech → Whisper STT → Mistral 7B LLM → Google TTS → Voice Response
```

### Core Components

- **`max_ai_assistant.py`** - Main AI assistant that integrates all modules
- **`stt_module.py`** - Speech-to-text using Whisper Base
- **`llm_module.py`** - Language processing using Mistral 7B via Ollama
- **`tts_module.py`** - Text-to-speech using Google TTS
- **`tools_module.py`** - File system and utility tools
- **`memory_module.py`** - Conversation memory and context
- **`simple_interrupt.py`** - Keyboard interruption handling

## 🎯 How It Works

1. **Listen** - Max continuously listens for your voice
2. **Transcribe** - Whisper converts speech to text in real-time
3. **Process** - Mistral 7B generates intelligent responses with memory context
4. **Execute Tools** - Can perform file operations, calculations, and system tasks
5. **Speak** - Google TTS converts responses to natural speech
6. **Pause** - Automatically pauses listening while speaking to prevent feedback

## 📊 Performance

- **STT Latency**: <1s for 5-second audio
- **LLM Processing**: <2s for response generation
- **TTS Latency**: <1s for short responses
- **End-to-End**: <4s total per command
- **Memory Usage**: <8GB RAM total

## 🛠️ Troubleshooting

### Audio Issues
- Make sure your microphone is working
- Check system audio permissions
- Try different audio devices if available

### Performance Issues
- The first run will download the Whisper model (~39MB)
- Subsequent runs will be faster
- Close other audio applications if needed

### Dependencies Issues

If you encounter installation problems:

```bash
# Update pip and setuptools first
pip3 install --upgrade pip setuptools wheel

# Install system dependencies
brew install portaudio

# Install packages individually if needed
pip3 install openai-whisper
pip3 install sounddevice
pip3 install torch
pip3 install numpy scipy
pip3 install gtts playsound
```

## 🎮 Usage Examples

Try saying these phrases to test Max:

- "Hello, how are you?"
- "What's the weather like?"
- "Tell me a joke"
- "What time is it?"
- "Go to sleep" (to exit)

## 📁 Project Structure

```
Friday/
├── stt_module.py          # Speech-to-text module
├── llm_module.py          # Language model module
├── tts_module.py          # Text-to-speech module
├── test_stt_llm_voice.py  # Main voice assistant
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── docs/                  # Documentation
    ├── prd.md            # Product requirements
    └── implementation_checklist.md
```

## 🔮 Next Steps

This core pipeline is ready for integration with:
- File management tools
- Calendar integration
- Task management
- Local search capabilities
- Internet search (RSS feeds)

## 📝 Notes

- All processing is done offline for privacy
- Single-user system
- No cloud dependencies
- Built for macOS with 16GB RAM
- Focus on functional implementation first
