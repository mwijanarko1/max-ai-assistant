Product Requirements Document (PRD): Friday Assistant

1. Product Overview

1.1 Purpose

Friday is a voice-activated, locally-run personal assistant inspired by Iron Man's Friday, designed to process spoken commands, execute tasks via tool-calling, and respond with natural speech. It operates offline on a system with 16GB RAM, prioritizing privacy, low latency, and resource efficiency.

1.2 Scope





Core Features:





Speech-to-text (STT) for command input.



Local large language model (LLM) for natural language understanding and response generation.



Text-to-speech (TTS) for spoken output.



Tool-calling for task execution (e.g., task management, calendar, local search).



Offline operation with minimal memory footprint.



Exclusions: No weather, email, smart home control, music, or location-based services.



Target Platform: Desktop or laptop with 16GB RAM, CPU (GPU optional for acceleration).

2. Functional Requirements

2.1 Speech-to-Text (STT)





Description: Convert spoken user commands into text using a local STT model.



Requirements:





Use Whisper Tiny or Base model (open-source) for transcription.



Support English with robustness to varied accents and moderate background noise.



Process audio in real-time or near-real-time (<1s latency for short commands).



Memory usage: <2GB RAM.



User Interaction: User speaks (e.g., “Add a task to buy milk”), and system transcribes accurately.

2.2 Local Large Language Model (LLM)





Description: Process transcribed text to identify intents, extract entities, and generate responses.



Requirements:





Use Mistral 7B (4-bit quantized) for low memory footprint (~5-6GB RAM).



Support intent recognition for 10+ predefined commands (e.g., “add_task”, “search_notes”).



Maintain conversation context for at least 3 turns.



Generate concise, natural responses (<50 words).



Allow fine-tuning on a small dataset of sample commands (provided later).



User Interaction: Transcribed text (e.g., “List my tasks”) is processed to execute the correct tool and respond (e.g., “You have 2 tasks: buy milk, finish report”).

2.3 Text-to-Speech (TTS)





Description: Convert text responses into natural-sounding speech.



Requirements:





Use Coqui TTS (small model, e.g., XTTS-v2) for local processing.



Support English with a natural, human-like voice.



Latency: <1s for generating speech from short responses.



Memory usage: <2GB RAM.



Cache frequent responses to reduce computation.



User Interaction: System speaks responses (e.g., “Task added: buy milk”).

2.4 Tool-Calling





Description: Execute tasks by calling predefined tools based on LLM-detected intents.



Tools and Requirements:





Calendar (Local iCal File):





Add, read, and delete events in a local iCal file using icalendar library.



Example: “Schedule a meeting at 3 PM” → Add event to iCal file.



Memory: <100MB.



Task Management (Taskwarrior):





Manage tasks (add, list, complete) using Taskwarrior’s CLI.



Example: “Add task: finish report” → Execute Taskwarrior command.



Memory: <50MB.



News Retrieval (RSS Feed Parser):





Parse locally cached RSS feeds using feedparser.



Example: “What’s the latest science news?” → Read cached feeds and summarize.



Memory: <100MB; cache feeds to disk.



Local Search (Whoosh):





Index and search local documents (e.g., notes, PDFs) using Whoosh.



Example: “Find my AI notes” → Return relevant documents.



Memory: <500MB; store indexes on disk.



Custom Script Runner (Python):





Execute user-defined Python scripts via subprocess.



Example: “Run my backup script” → Trigger script.



Memory: <1GB, depending on script.



Local Database (SQLite):





Query structured data (e.g., expenses, logs) using sqlite3.



Example: “List my expenses” → Query SQLite table.



Memory: <100MB; store data on disk.



File Management (Local File System):





Read/write/organize local files using pathlib or os.



Example: “Read my journal” → Access text file.



Memory: <100MB.



Requirements:





Map LLM intents to tools using a lightweight dispatcher (e.g., JSON-based intent-to-tool mapping).



Handle errors gracefully (e.g., “Task not found” for invalid commands).



Support asynchronous execution for scripts and database queries.



Total memory usage for tools: <2GB combined.

2.5 Context Management





Description: Store conversation history and session data to support multi-turn interactions.



Requirements:





Use SQLite to store context (e.g., recent commands, user preferences).



Retain context for at least 3 turns or 5 minutes.



Memory usage: <100MB.



Clear context on user command (e.g., “Reset session”).



User Interaction: System recalls prior context (e.g., “Add another task” after “Add task: buy milk”).

3. Non-Functional Requirements

3.1 Performance





Latency:





STT: <1s for 5-second audio clips.



LLM processing: <2s for intent recognition and response generation.



TTS: <1s for short responses (<50 words).



Tool execution: <1s for lightweight tools (e.g., SQLite, Taskwarrior).



Throughput: Handle one command at a time (single-user system).



Startup Time: System initializes in <30s.

3.2 Memory Constraints





Total RAM Usage: <12GB to leave ~4GB for OS and background processes.



Breakdown:





Whisper (STT): ~1-2GB (Tiny/Base model).



Mistral 7B (LLM): ~5-6GB (4-bit quantized).



Coqui TTS: ~1-2GB (small model).



Tools and context: ~1-2GB combined.



Optimization:





Use quantized models (4-bit for LLM).



Process components sequentially (e.g., unload Whisper before loading Mistral).



Cache frequent responses and store data on disk (e.g., SQLite, Whoosh indexes).

3.3 Privacy and Security





Offline Operation: All processing (STT, LLM, TTS, tools) must run locally without internet dependency.



Data Protection:





Encrypt SQLite databases and iCal files (use Python’s cryptography library).



Avoid storing raw audio files; delete temporary audio after transcription.



Script Safety: Restrict custom script runner to a sandboxed environment (e.g., limited file system access).

3.4 Reliability





Uptime: System should run continuously without crashing for at least 24 hours.



Error Handling:





STT: Fallback to “Please repeat” for unclear audio.



LLM: Default to “I don’t understand” for unrecognized intents.



Tools: Return user-friendly error messages (e.g., “No notes found”).



Recovery: Restart components automatically if they crash.

3.5 Usability





User Experience:





Natural, concise responses (<50 words).



Clear spoken output with minimal distortion.



Support for follow-up commands (e.g., “Add another task”).



Accessibility: Handle varied accents and moderate background noise in STT.

4. System Architecture





Components:





Audio Input: Capture via microphone using PyAudio.



STT Module: Whisper Tiny/Base for transcription.



LLM Module: Mistral 7B (4-bit) for intent recognition and response generation.



Tool-Calling Module: JSON-based dispatcher to map intents to tools.



TTS Module: Coqui TTS for speech output.



Context Manager: SQLite for storing session data.



Data Flow:





Audio → Whisper → Text.



Text → Mistral 7B → Intent + Parameters.



Intent → Tool (e.g., Taskwarrior, SQLite) → Result.



Result → Mistral 7B → Response Text.



Response Text → Coqui TTS → Speech.



Context → SQLite (updated after each interaction).



Optimization:





Sequential processing to stay within 16GB RAM.



Disk-based storage for tools (e.g., SQLite, Whoosh indexes).



Cache frequent TTS outputs to reduce computation.

5. Development Phases





Phase 1: Core Pipeline





Implement STT (Whisper Tiny), LLM (Mistral 7B), and TTS (Coqui).



Test with a single command (e.g., “Hello” → “Hi!”).



Verify RAM usage <10GB.



Phase 2: Add Core Tools





Integrate Taskwarrior and SQLite for task and data management.



Test end-to-end flow (e.g., “Add task” → Taskwarrior → TTS).



Phase 3: Expand Tools





Add iCal, Whoosh, RSS parser, and file operations.



Test multi-turn interactions (e.g., “Add task” → “List tasks”).



Phase 4: Optimize and Secure





Optimize memory (e.g., 4-bit quantization, caching).



Add encryption for SQLite and iCal.



Test with noisy audio and complex commands.



Phase 5: Deploy and Validate





Deploy on 16GB RAM system (e.g., PC, Raspberry Pi).



Validate performance (<2s latency) and memory (<12GB).

6. Technical Constraints





Hardware: 16GB RAM, CPU (GPU optional for acceleration).



Operating System: Linux or Windows (developer’s choice; ensure compatibility).



Dependencies:





Python 3.9+ for all components.



Libraries: whisper.cpp, llama.cpp or Ollama, Coqui TTS, icalendar, feedparser, Whoosh, sqlite3, pathlib.



No cloud-based APIs or services.



Memory Limit: Total usage <12GB RAM at peak.



Offline Requirement: All components must function without internet.

7. Success Criteria





Functional:





System correctly processes 10+ unique commands across all tools.



Multi-turn interactions work seamlessly (e.g., “Add task” → “List tasks”).



STT handles varied accents with >90% accuracy.



TTS produces clear, natural speech.



Performance:





End-to-end latency <4s per command.



RAM usage <12GB at all times.



Reliability:





No crashes during 24-hour operation.



Graceful error handling for all edge cases.



Privacy:





All data processed and stored locally.



Encrypted storage for sensitive data.

8. Risks and Mitigations





Risk: Memory overflow (>16GB).





Mitigation: Use quantized models, sequential processing, and disk-based storage.



Risk: Slow inference on CPU.





Mitigation: Optimize Whisper/Mistral (e.g., small models, low batch size).



Risk: Poor STT accuracy with noise.





Mitigation: Test with diverse audio; implement “Please repeat” fallback.



Risk: Complex intents confuse LLM.





Mitigation: Fine-tune Mistral on sample commands; use clear intent mapping.

9. Deliverables





Fully functional Friday system running on 16GB RAM.



Documentation: Setup guide, tool integration details, and user manual.



Test suite: Automated tests for STT, LLM, TTS, and each tool.



Performance report: RAM usage, latency, and accuracy metrics.

10. Timeline (Estimate)





Phase 1: 2 weeks (core pipeline).



Phase 2: 2 weeks (core tools).



Phase 3: 3 weeks (additional tools).



Phase 4: 2 weeks (optimization/security).



Phase 5: 1 week (deployment/validation).



Total: ~10 weeks.

11. Assumptions





Developer has access to a 16GB RAM system with Python 3.9+.



Sample command dataset for LLM fine-tuning will be provided.



No internet required post-setup (all dependencies downloaded locally).



Single-user system; no multi-user support needed.

12. Next Steps





Developer to confirm tech stack (e.g., whisper.cpp, llama.cpp, Coqui).



Set up development environment and test Whisper Tiny on sample audio.



Report initial RAM usage for core components (STT, LLM, TTS).