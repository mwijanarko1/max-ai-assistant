import requests
import json
import time
from typing import Optional, Dict, Any

class LLMModule:
    def __init__(self, model_name: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        """
        Initialize LLM module using Ollama
        
        Args:
            model_name: Ollama model name (e.g., "qwen3:4b")
            base_url: Ollama API base URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
        
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
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response using the LLM with <3s target latency
        """
        try:
            # Temporarily disable history to prevent hallucination
            # self._add_to_history("user", user_input)
            
            # Use Qwen3 chat template format
            messages = [
                {"role": "user", "content": user_input}
            ]
            
            # Very strict prompt to prevent hallucination
            prompt = f"""You are Friday. Respond ONLY to this specific input. Do not make up conversations or add fictional exchanges.

Input: {user_input}
Response:"""
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "enable_thinking": False
                }
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
        Extract intent from user input quickly
        """
        try:
            intent_prompt = f"""Classify intent of: "{user_input}"
Return one word: greeting, question, command, goodbye, or unknown."""

            payload = {
                "model": self.model_name,
                "prompt": intent_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 4,
                    "stop": ["\n"],
                    "enable_thinking": False
                }
            }
            
            start_time = time.time()
            response = requests.post(self.api_url, json=payload, timeout=2.5)
            if response.status_code == 200:
                intent_time = time.time() - start_time
                intent = response.json().get("response", "unknown").strip().lower()
                intent_mapping = {
                    "greeting": "greeting",
                    "question": "question",
                    "command": "command",
                    "goodbye": "goodbye",
                    "unknown": "unknown",
                }
                print(f"🎯 Intent: {intent_mapping.get(intent, 'unknown')} ({intent_time:.2f}s)")
                return {"intent": intent_mapping.get(intent, "unknown"), "confidence": 0.8, "original_input": user_input}
            return {"intent": "unknown", "confidence": 0.0, "original_input": user_input}
        except Exception as e:
            print(f"❌ Error extracting intent: {e}")
            return {"intent": "unknown", "confidence": 0.0, "original_input": user_input}
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")


def test_llm():
    """Test the LLM module"""
    print("Testing LLM Module")
    print("=" * 30)
    
    try:
        llm = LLMModule(model_name="mistral:7b")
        
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
