# Max AI Assistant - Voice AI Assistant

A complete voice-activated AI assistant that listens, thinks, and responds with natural speech. Built with Whisper for speech recognition, Llama 3 8B for language processing, and Google TTS for speech synthesis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎤 Core Voice Capabilities
- **Real-time Speech Recognition** - Whisper Base model with <1s latency
- **Intelligent Responses** - Llama 3 8B LLM via Ollama for natural conversations
- **Natural Speech Output** - Google TTS for high-quality voice responses
- **Smart Audio Control** - Automatically pauses listening when speaking to prevent feedback
- **Voice Commands** - Say "go to sleep", "goodbye", "bye", "exit", or "quit" to exit
- **Interruption Support** - Press ENTER to interrupt Max while speaking
- **Fast Performance** - <4s end-to-end response time
- **Memory Efficient** - Uses <8GB RAM total

### 🧠 Advanced Intelligence
- **Two-Tier Intent Detection** - Fast keyword-based detection with LLM fallback for complex cases
- **Entity Extraction** - Automatically extracts filenames, paths, numbers, dates, times, and commands
- **Context-Aware Processing** - Remembers previous interactions and file references
- **Smart File Detection** - Intelligent file extension detection (.md, .txt, .json, .pdf)
- **Natural Language Understanding** - Handles variations like "PRD file", "the PRD", "PRD.md"

### 🛠️ File & System Tools
- **File Operations** - Open, read, write, edit, and search files
- **Directory Management** - Navigate, list, and find directories
- **File Search** - Search for files by name or content across the system
- **File Summarization** - Generate brief or detailed summaries of documents
- **System Information** - Get system info, disk usage, and current directory
- **Mathematical Calculations** - Perform basic math operations
- **Time & Date** - Get current time, date, or day of week

### 💾 Memory & Context
- **Session Memory** - Tracks conversation history and context
- **File Context** - Remembers last opened and created files
- **Interaction Logging** - Logs all interactions with timestamps
- **Context-Aware References** - Understands "it", "that", and "the file" references
- **Session Archiving** - Automatically archives sessions for future reference

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- **Operating System**: macOS (tested on macOS 13+)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space for models and dependencies
- **Python**: 3.9 or higher

### Required Software
1. **Python 3.9+** - [Download here](https://www.python.org/downloads/)
2. **Homebrew** - [Install here](https://brew.sh/)
3. **Ollama** - [Install here](https://ollama.ai/)

### Hardware Requirements
- **Microphone**: Built-in or external microphone
- **Speakers**: Built-in or external speakers/headphones
- **Internet**: Required for initial model downloads

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/mwijanarko1/max-ai-assistant.git

# Navigate to the project directory
cd max-ai-assistant
```

### Step 2: Install System Dependencies

#### macOS
```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PortAudio
brew install portaudio
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pip python3-venv
```

#### Windows
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# Then install PortAudio manually or use conda
conda install -c conda-forge portaudio
```

### Step 3: Set Up Python Environment

```bash
# Create a virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Install Ollama and Models

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download Llama 3 8B model (this may take a while)
ollama pull llama3:8b
```

### Step 5: Verify Installation

```bash
# Test if all dependencies are installed correctly
python3 -c "import whisper, torch, sounddevice, gtts, playsound; print('✅ All dependencies installed successfully!')"
```

## 🎯 Quick Start

### 1. Start Ollama (if not running)
```bash
# In a separate terminal window
ollama serve
```

### 2. Run Max AI Assistant
```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Start Max AI Assistant
python3 run_max.py
```

### 3. Start Speaking!
- **Wake up**: Say "Hey Max" or any greeting
- **Test commands**: Try "What time is it?" or "List the files here"
- **Exit**: Say "go to sleep" or "goodbye"

## 🎮 Usage

### Basic Commands
- **"Hello, how are you?"** - General conversation
- **"What time is it?"** - Get current time
- **"What's the day today?"** - Get current day
- **"Calculate 15 times 23"** - Mathematical calculations

### File Operations
- **"Open the README file"** - Open and read files
- **"List the files in this directory"** - List directory contents
- **"Navigate to the desktop folder"** - Change directories
- **"Search for Python files"** - Search for files
- **"Summarize the README file"** - Generate file summaries
- **"Create a new text file"** - Create new files

### System Commands
- **"What's my current directory?"** - Get current working directory
- **"Show system information"** - Get system details
- **"Check disk usage"** - Check disk space
- **"Find the documents folder"** - Find directories

### Voice Control
- **"Stop" or "interrupt"** - Stop Max's speech
- **"Go to sleep" or "goodbye"** - Exit gracefully
- **Press ENTER** - Interrupt Max while speaking

## 🏗️ Architecture

```
User Speech → Whisper STT → Llama 3 8B LLM → Tool Detection → Tool Execution → Google TTS → Voice Response
                                    ↓
                              Memory Context
```

### Core Components

- **`max_ai_assistant.py`** - Main AI assistant that integrates all modules
- **`stt_module.py`** - Speech-to-text using Whisper Base
- **`llm_module.py`** - Language processing using Llama 3 8B via Ollama
- **`tts_module.py`** - Text-to-speech using Google TTS
- **`tools_module.py`** - File system and utility tools
- **`memory_module.py`** - Conversation memory and context
- **`simple_interrupt.py`** - Keyboard interruption handling

## 🛠️ Available Tools

### Time & Date
- **`get_current_time`** - Get current date, time, or day of week
- **`calculate`** - Perform mathematical calculations

### File Management
- **`list_directories`** - List files and directories in current location
- **`navigate_directory`** - Navigate to specific directories
- **`open_file`** - Open and read file contents
- **`write_file`** - Write content to files
- **`edit_file`** - Edit files by appending or replacing content
- **`search_files`** - Search for files by name or content
- **`summarize`** - Generate brief or detailed file summaries

### System Information
- **`get_system_info`** - Get system information
- **`get_disk_usage`** - Check disk usage
- **`find_directory`** - Find directories by name
- **`get_current_directory`** - Get current working directory

## 📊 Performance

- **STT Latency**: <1s for 5-second audio
- **LLM Processing**: <2s for response generation
- **TTS Latency**: <1s for short responses
- **End-to-End**: <4s total per command
- **Memory Usage**: <8GB RAM total
- **Intent Detection**: 95%+ accuracy with two-tier system
- **File Detection**: 95%+ accuracy with intelligent extension detection

## 🏗️ Project Structure

```
max-ai-assistant/
├── src/
│   ├── max_ai_assistant.py     # Main AI assistant
│   ├── stt_module.py           # Speech-to-text module
│   ├── llm_module.py           # Language model module
│   ├── tts_module.py           # Text-to-speech module
│   ├── tools_module.py         # File system and utility tools
│   ├── memory_module.py        # Conversation memory and context
│   └── simple_interrupt.py     # Keyboard interruption handling
├── memory/                     # Session memory and logs (ignored by git)
├── docs/                       # Documentation (ignored by git)
│   ├── prd.md                 # Product requirements
│   └── implementation_checklist.md
├── requirements.txt            # Python dependencies
├── run_max.py                 # Main entry point
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🛠️ Troubleshooting

### Common Issues

#### Audio Issues
```bash
# Check if microphone is working
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Test audio recording
python3 -c "import sounddevice as sd; print('Recording for 3 seconds...'); sd.rec(3*44100, samplerate=44100, channels=1); sd.wait(); print('Recording complete!')"
```

#### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

#### Python Dependencies
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check Python version
python3 --version  # Should be 3.9+
```

#### Memory Issues
```bash
# Check available RAM
free -h  # Linux
vm_stat   # macOS
```

### Performance Optimization

1. **Close other applications** - Free up RAM for Max
2. **Use SSD storage** - Faster model loading
3. **Update drivers** - Ensure latest audio drivers
4. **Check background processes** - Close unnecessary services

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Add comments for complex logic
- Include docstrings for functions
- Test your changes before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Mikhail Wijanarko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **Meta Llama 3** - Language model
- **Google TTS** - Text-to-speech synthesis
- **Ollama** - Local LLM serving
- **PortAudio** - Audio processing

## 📞 Support

If you encounter any issues or have questions:

1. **Check the [Troubleshooting](#-troubleshooting) section**
2. **Search existing [Issues](https://github.com/mwijanarko1/max-ai-assistant/issues)**
3. **Create a new issue** with detailed information about your problem

---

**Made with ❤️ by [Mikhail Wijanarko](https://github.com/mwijanarko1)**
