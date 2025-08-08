#!/usr/bin/env python3
"""
Memory Module for Max Voice Assistant
Handles session-based conversation logging and context management
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class MaxMemory:
    """Manages session-based memory for Max Voice Assistant"""
    
    def __init__(self, memory_dir: str = "memory"):
        """
        Initialize Max Memory system
        
        Args:
            memory_dir: Directory to store session files
        """
        # Use absolute path for memory directory
        self.memory_dir = os.path.abspath(memory_dir)
        self.current_session_file = os.path.join(self.memory_dir, "current_session.txt")
        self.session_start_time = None
        self.session_tags = []
        self.interaction_count = 0
        
        # Create memory directory if it doesn't exist
        os.makedirs(self.memory_dir, exist_ok=True)
        
        print(f"🧠 Memory system initialized: {self.memory_dir}/")
    
    def start_new_session(self):
        """Start a new conversation session"""
        self.session_start_time = datetime.now()
        self.session_tags = []
        self.interaction_count = 0
        
        # Log session metadata
        self._log_session_metadata()
        
        print(f"🆕 New session started: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _log_session_metadata(self):
        """Log session start information"""
        metadata = f"""=== SESSION STARTED: {self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")} ===
System: Max Voice Assistant
User: {os.getenv('USER', 'Unknown')}
Working Directory: {os.getcwd()}
Session ID: {self.session_start_time.strftime("%Y%m%d_%H%M%S")}
===============================================

"""
        
        with open(self.current_session_file, "w", encoding="utf-8") as f:
            f.write(metadata)
    
    def log_interaction(self, user_input: str, max_response: str, context: Optional[Dict] = None):
        """
        Log a user interaction to current session
        
        Args:
            user_input: What the user said
            max_response: What Max responded
            context: Additional context (current directory, tools used, etc.)
        """
        self.interaction_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format context for logging
        context_str = "None"
        if context:
            context_parts = []
            if 'current_directory' in context:
                context_parts.append(f"Directory: {context['current_directory']}")
            if 'tool_used' in context:
                context_parts.append(f"Tool: {context['tool_used']}")
            if 'files_accessed' in context:
                context_parts.append(f"Files: {', '.join(context['files_accessed'])}")
            if context_parts:
                context_str = " | ".join(context_parts)
        
        log_entry = f"""
=== Interaction #{self.interaction_count} - {timestamp} ===
User: {user_input}
Max: {max_response}
Context: {context_str}
"""
        
        with open(self.current_session_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(f"📝 Logged interaction #{self.interaction_count}")
    
    def get_session_context(self, max_lines: int = 200) -> str:
        """
        Get context from current session for LLM prompt
        
        Args:
            max_lines: Maximum number of lines to include
            
        Returns:
            Session context as string
        """
        try:
            with open(self.current_session_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                # If file is too long, take the last max_lines
                if len(lines) > max_lines:
                    lines = lines[-max_lines:]
                
                return "".join(lines)
        except FileNotFoundError:
            return ""
    
    def end_session(self, add_summary: bool = True):
        """
        End current session and archive it
        
        Args:
            add_summary: Whether to add session summary before archiving
        """
        if not os.path.exists(self.current_session_file):
            print("ℹ️  No current session to end")
            return
        
        if add_summary:
            self._add_session_summary()
        
        # Create archive filename
        timestamp = self.session_start_time.strftime("%Y_%m_%d_%H_%M_%S")
        archive_name = f"session_{timestamp}.txt"
        archive_path = os.path.join(self.memory_dir, archive_name)
        
        # Move current session to archive
        os.rename(self.current_session_file, archive_path)
        
        duration = datetime.now() - self.session_start_time
        print(f"📁 Session archived: {archive_name}")
        print(f"⏱️  Session duration: {duration}")
        print(f"💬 Total interactions: {self.interaction_count}")
    
    def _add_session_summary(self):
        """Add summary to current session before archiving"""
        duration = datetime.now() - self.session_start_time
        
        summary = f"""

=== SESSION SUMMARY ===
Session Duration: {duration}
Total Interactions: {self.interaction_count}
Session Tags: {', '.join(self.session_tags) if self.session_tags else 'None'}
Working Directory: {os.getcwd()}
Session Ended: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
===============================================
"""
        
        with open(self.current_session_file, "a", encoding="utf-8") as f:
            f.write(summary)
    
    def add_session_tag(self, tag: str):
        """Add a tag to the current session"""
        if tag not in self.session_tags:
            self.session_tags.append(tag)
            print(f"🏷️  Added session tag: {tag}")
    
    def get_interaction_count(self) -> int:
        """Get number of interactions in current session"""
        return self.interaction_count
    
    def search_past_sessions(self, query: str) -> List[tuple]:
        """
        Search through past session files
        
        Args:
            query: Search term
            
        Returns:
            List of (filename, content) tuples
        """
        results = []
        
        try:
            for filename in os.listdir(self.memory_dir):
                if filename.startswith("session_") and filename.endswith(".txt"):
                    filepath = os.path.join(self.memory_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append((filename, content))
        except FileNotFoundError:
            pass
        
        return results
    
    def list_sessions(self) -> List[str]:
        """List all archived sessions"""
        sessions = []
        
        try:
            for filename in os.listdir(self.memory_dir):
                if filename.startswith("session_") and filename.endswith(".txt"):
                    sessions.append(filename)
        except FileNotFoundError:
            pass
        
        return sorted(sessions, reverse=True)
    
    def get_session_stats(self) -> Dict:
        """Get statistics about the current session"""
        duration = datetime.now() - self.session_start_time if self.session_start_time else None
        
        return {
            "session_start": self.session_start_time.isoformat() if self.session_start_time else None,
            "duration": str(duration) if duration else None,
            "interactions": self.interaction_count,
            "tags": self.session_tags,
            "working_directory": os.getcwd()
        }
    
    def clear_current_session(self):
        """Clear the current session file"""
        if os.path.exists(self.current_session_file):
            os.remove(self.current_session_file)
            print("🗑️  Current session cleared")


def test_memory():
    """Test the memory module"""
    print("Testing Memory Module")
    print("=" * 30)
    
    try:
        memory = MaxMemory()
        
        # Start new session
        memory.start_new_session()
        
        # Log some interactions
        memory.log_interaction(
            "What time is it?",
            "It's 2:30 PM.",
            {"current_directory": "/Users/mikhail/Desktop", "tool_used": "get_current_time"}
        )
        
        memory.log_interaction(
            "Navigate to documents",
            "Successfully navigated to documents directory.",
            {"current_directory": "/Users/mikhail/Documents", "tool_used": "navigate_directory"}
        )
        
        memory.log_interaction(
            "Open the Apple file",
            "File 'Apple.txt' contents: [content here]",
            {"current_directory": "/Users/mikhail/Documents", "tool_used": "open_file", "files_accessed": ["Apple.txt"]}
        )
        
        # Add a tag
        memory.add_session_tag("file_operations")
        
        # Get session stats
        stats = memory.get_session_stats()
        print(f"\n📊 Session Stats: {stats}")
        
        # Get context
        context = memory.get_session_context()
        print(f"\n📝 Session Context (first 200 chars): {context[:200]}...")
        
        # End session
        memory.end_session()
        
        # List sessions
        sessions = memory.list_sessions()
        print(f"\n📁 Archived Sessions: {sessions}")
        
        print("\n✅ Memory module test completed!")
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")


if __name__ == "__main__":
    test_memory()
