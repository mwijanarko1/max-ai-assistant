import requests
import json
import time
from typing import Optional, Dict, Any

class LLMModule:
    def __init__(self, model_name: str = "llama3:8b", base_url: str = "http://localhost:11434", fast_mode: bool = True):
        """
        Initialize LLM module using Ollama
        
        Args:
            model_name: Ollama model name (e.g., "qwen3:4b")
            base_url: Ollama API base URL
            fast_mode: Enable performance optimizations
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
        self.fast_mode = fast_mode
        
        # Test connection
        self._test_connection()
        
        # Conversation context
        self.conversation_history = []
        self.max_history = 5  # Keep last 5 exchanges
        
    def _test_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                print(f"✅ Connected to Ollama successfully!")
                print(f"📦 Using model: {self.model_name}")
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")
            raise
    
    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only last max_history exchanges
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def _build_prompt(self, user_input: str) -> str:
        """Build a prompt for the LLM with context"""
        
        # System prompt for Friday - very simple and direct
        system_prompt = """Respond to this in one sentence: {user_input}"""
        
        return system_prompt.format(user_input=user_input)
    
    def _first_sentence(self, text: str) -> str:
        """Return the first sentence worth speaking."""
        for end in [". ", "? ", "! ", ".\n", "?\n", "!\n", ".", "?", "!"]:
            idx = text.find(end)
            if idx != -1:
                return text[: idx + len(end.strip())].strip()
        return text.strip()
    
    def generate_response(self, user_input: str, memory_context: str = "") -> str:
        """
        Generate a response using the LLM with memory context
        
        Args:
            user_input: User's input
            memory_context: Session memory context to include in prompt
        """
        try:
            # Temporarily disable history to prevent hallucination
            # self._add_to_history("user", user_input)
            
            # Use Qwen3 chat template format
            messages = [
                {"role": "user", "content": user_input}
            ]
            
            # Optimized prompt for speed - only include essential memory context
            if self.fast_mode and memory_context and len(memory_context) > 100:
                # Fast mode: minimal context for speed
                recent_context = memory_context[-200:]  # Very limited context
                prompt = f"""Max (be concise): {user_input}"""
            elif memory_context and len(memory_context) > 100:
                # Normal mode: include some context
                recent_context = memory_context[-500:]  # Limit to last 500 chars
                prompt = f"""Max AI Assistant (be concise). Recent context: {recent_context}

User: {user_input}
Max:"""
            else:
                # Fast response for simple queries
                prompt = f"""Max AI Assistant (be concise). User: {user_input}
Max:"""
            
            # Optimize parameters based on mode - keep responses concise
            if self.fast_mode:
                options = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "enable_thinking": False,
                    "num_ctx": 1024,  # Very small context for speed
                    "num_predict": 50,  # Very short responses
                    "repeat_penalty": 1.1
                }
            else:
                options = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "enable_thinking": False,
                    "num_ctx": 2048,
                    "num_predict": 75,  # Shorter responses
                    "repeat_penalty": 1.1
                }
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": options
            }
            
            # Stream the response
            start = time.time()
            first_token_time = None
            token_count = 0
            response = requests.post(self.api_url, json=payload, timeout=60.0, stream=True)
            
            if response.status_code == 200:
                aggregated = []
                inside_thinking = False  # Track if we're inside a thinking block
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    if chunk.get("done"):
                        break
                    
                    token = chunk.get("response", "")
                    if token:
                        # Track first token time
                        if first_token_time is None:
                            first_token_time = time.time()
                        
                        # Properly filter out thinking tokens between <think> and </think> tags
                        if "<think>" in token:
                            # Start of thinking block - skip this token and all subsequent tokens
                            inside_thinking = True
                            continue
                        elif "</think>" in token:
                            # End of thinking block - resume normal processing
                            inside_thinking = False
                            continue
                        elif inside_thinking:
                            # Inside thinking block - skip all tokens
                            continue
                        else:
                            # Outside thinking block - add token to response
                            aggregated.append(token)
                            token_count += 1
                
                llm_response = "".join(aggregated).strip()
                if llm_response:
                    # Calculate stats
                    total_time = time.time() - start
                    time_to_first_token = first_token_time - start if first_token_time else 0
                    tokens_per_sec = token_count / total_time if total_time > 0 else 0
                    
                    # Print stats
                    print(f"📊 Stats: Model={self.model_name}, Tokens={token_count}, Time={total_time:.2f}s, FirstToken={time_to_first_token:.2f}s, Speed={tokens_per_sec:.1f} tokens/sec")
                    
                    # Temporarily disable history to prevent hallucination
                    # self._add_to_history("assistant", llm_response)
                    
                    # Clear history after each response to prevent context contamination
                    # if len(self.conversation_history) > 4:  # Keep only last 2 exchanges
                    #     self.conversation_history = self.conversation_history[-4:]
                    
                    return llm_response
            
            # Return empty if no response
            return ""
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return ""
    
    def get_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Extract intent from user input with improved accuracy and confidence scoring
        """
        try:
            # First, try keyword-based intent detection for speed and accuracy
            keyword_intent = self._keyword_based_intent_detection(user_input)
            if keyword_intent["confidence"] > 0.7:
                return keyword_intent
            
            # Fallback to LLM-based intent detection for complex cases
            return self._llm_based_intent_detection(user_input)
            
        except Exception as e:
            print(f"❌ Error extracting intent: {e}")
            return {"intent": "unknown", "confidence": 0.0, "original_input": user_input}
    
    def _keyword_based_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """
        Fast keyword-based intent detection for common patterns
        """
        input_lower = user_input.lower().strip()
        
        # Goodbye patterns (highest priority)
        goodbye_patterns = [
            "goodbye", "bye", "see you", "later", "good night", "night",
            "go to sleep", "exit", "quit", "stop", "end"
        ]
        if any(pattern in input_lower for pattern in goodbye_patterns):
            return {"intent": "goodbye", "confidence": 0.95, "original_input": user_input}
        
        # Special handling for "can you" - check if it's followed by a command
        if "can you" in input_lower or "could you" in input_lower or "would you" in input_lower:
            # Check if "can you" is followed by a command word
            command_words_after_can_you = [
                "open", "read", "write", "create", "delete", "move", "copy", "find",
                "search", "list", "show", "navigate", "go", "change", "set",
                "calculate", "compute", "get", "fetch", "download", "upload",
                "file", "document", "folder", "directory", "edit", "save"
            ]
            if any(cmd_word in input_lower for cmd_word in command_words_after_can_you):
                return {"intent": "command", "confidence": 0.85, "original_input": user_input}
            else:
                return {"intent": "question", "confidence": 0.85, "original_input": user_input}
        
        # Command patterns (action verbs and imperative structures)
        command_indicators = [
            "open", "read", "write", "create", "delete", "move", "copy", "find",
            "search", "list", "show", "navigate", "go to", "change", "set",
            "calculate", "compute", "get", "fetch", "download", "upload"
        ]
        if any(indicator in input_lower for indicator in command_indicators):
            return {"intent": "command", "confidence": 0.9, "original_input": user_input}
        
        # Time/date patterns
        time_patterns = [
            "time", "date", "day", "today", "current", "now", "when"
        ]
        if any(pattern in input_lower for pattern in time_patterns):
            return {"intent": "command", "confidence": 0.8, "original_input": user_input}
        
        # File operation patterns
        file_patterns = [
            "file", "document", "folder", "directory", "open", "read", "write",
            "create", "edit", "delete", "save"
        ]
        if any(pattern in input_lower for pattern in file_patterns):
            return {"intent": "command", "confidence": 0.85, "original_input": user_input}
        
        # System/computer patterns
        system_patterns = [
            "system", "computer", "laptop", "hardware", "specs", "info",
            "disk", "storage", "space", "usage", "memory", "cpu"
        ]
        if any(pattern in input_lower for pattern in system_patterns):
            return {"intent": "command", "confidence": 0.8, "original_input": user_input}
        
        # Calculation patterns
        calc_patterns = ["calculate", "compute", "math", "+", "-", "*", "/", "="]
        if any(pattern in input_lower for pattern in calc_patterns):
            return {"intent": "command", "confidence": 0.9, "original_input": user_input}
        
        # Greeting patterns (check after commands)
        greeting_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "howdy", "greetings", "what's up", "sup", "yo"
        ]
        if any(pattern in input_lower for pattern in greeting_patterns):
            return {"intent": "greeting", "confidence": 0.95, "original_input": user_input}
        
        # Question patterns (interrogative words and question marks) - check AFTER commands
        question_indicators = [
            "what", "when", "where", "who", "why", "how", "which", "whose",
            "do you", "does", "is", "are", "will", "should", "might", "may"
        ]
        
        if any(indicator in input_lower for indicator in question_indicators) or "?" in user_input:
            return {"intent": "question", "confidence": 0.85, "original_input": user_input}
        
        # Default to unknown for keyword-based detection
        return {"intent": "unknown", "confidence": 0.3, "original_input": user_input}
    
    def _llm_based_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """
        LLM-based intent detection for complex or ambiguous cases
        """
        try:
            intent_prompt = f"""Classify the intent of this user input: "{user_input}"

Choose from these intents:
- greeting: User is saying hello or starting a conversation
- question: User is asking for information or clarification
- command: User wants to perform an action or get something done
- goodbye: User is ending the conversation or saying farewell
- unknown: Intent is unclear or doesn't fit other categories

Return only the intent word:"""

            payload = {
                "model": self.model_name,
                "prompt": intent_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 8,
                    "stop": ["\n", ".", " "],
                    "enable_thinking": False
                }
            }
            
            start_time = time.time()
            response = requests.post(self.api_url, json=payload, timeout=3.0)
            if response.status_code == 200:
                intent_time = time.time() - start_time
                intent = response.json().get("response", "unknown").strip().lower()
                
                # Map LLM response to intent
                intent_mapping = {
                    "greeting": "greeting",
                    "question": "question", 
                    "command": "command",
                    "goodbye": "goodbye",
                    "unknown": "unknown",
                }
                
                detected_intent = intent_mapping.get(intent, "unknown")
                confidence = 0.7 if detected_intent != "unknown" else 0.3
                
                print(f"🎯 LLM Intent: {detected_intent} ({intent_time:.2f}s)")
                return {
                    "intent": detected_intent, 
                    "confidence": confidence, 
                    "original_input": user_input,
                    "method": "llm"
                }
            
            return {"intent": "unknown", "confidence": 0.0, "original_input": user_input, "method": "llm"}
            
        except Exception as e:
            print(f"❌ Error in LLM intent detection: {e}")
            return {"intent": "unknown", "confidence": 0.0, "original_input": user_input, "method": "llm"}
    
    def extract_entities(self, user_input: str) -> Dict[str, Any]:
        """
        Extract entities (filenames, paths, numbers, etc.) from user input
        """
        entities = {
            "filenames": [],
            "paths": [],
            "numbers": [],
            "dates": [],
            "times": [],
            "commands": []
        }
        
        import re
        
        # Extract filenames (with or without extensions)
        filename_patterns = [
            r'\b(\w+\.(?:txt|md|json|pdf|py|js|html|css|xml|csv))\b',
            r'\b(\w+)\s+(?:file|document)\b',
            r'(?:open|read|show|edit|write)\s+(?:the\s+)?(\w+(?:\.\w+)?)'
        ]
        
        for pattern in filename_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            entities["filenames"].extend(matches)
        
        # Extract paths
        path_patterns = [
            r'\b(?:go to|navigate to|move to|in|at)\s+(?:the\s+)?([\w\/\-\.]+)',
            r'\b(?:directory|folder)\s+([\w\/\-\.]+)'
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            entities["paths"].extend(matches)
        
        # Extract numbers
        number_patterns = [
            r'\b(\d+(?:\.\d+)?)\b',
            r'\b(\d+)\s*(?:hours?|minutes?|days?|weeks?|months?|years?)\b'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            entities["numbers"].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\b(today|tomorrow|yesterday|next week|last week)\b',
            r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            entities["dates"].extend(matches)
        
        # Extract times
        time_patterns = [
            r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b',
            r'\b(\d{1,2}\s*(?:AM|PM|am|pm))\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            entities["times"].extend(matches)
        
        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")


def test_llm():
    """Test the LLM module"""
    print("Testing LLM Module")
    print("=" * 30)
    
    try:
        llm = LLMModule(model_name="llama3:8b")
        
        print("\n1. Testing response generation...")
        test_inputs = [
            "Hello",
            "What time is it?",
            "How are you doing?",
            "Goodbye"
        ]
        
        for test_input in test_inputs:
            print(f"\nInput: {test_input}")
            t0 = time.time()
            response = llm.generate_response(test_input)
            dt = time.time() - t0
            print(f"Response ({dt:.2f}s): {response}")
        
        print("\n2. Testing intent extraction...")
        for test_input in test_inputs:
            intent_result = llm.get_intent(test_input)
            print(f"Input: {test_input}")
            print(f"Intent: {intent_result['intent']}")
        
        print("\n✅ LLM module test completed!")
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")

if __name__ == "__main__":
    test_llm()
