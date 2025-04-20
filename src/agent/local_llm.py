"""Local LLM handler for Asha AI."""

from typing import List, Dict, Any, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global cache directory
CACHE_DIR = Path.home() / ".cache" / "asha_ai"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default model configuration
DEFAULT_MODEL = "microsoft/phi-2"  # More capable than GPT-2
MAX_NEW_TOKENS = 200
TEMPERATURE = 0.7
TOP_P = 0.9

class LocalLLM:
    """Handler for local language models."""
    
    _instance = None
    
    def __new__(cls, model_name: str = DEFAULT_MODEL):
        if cls._instance is None:
            cls._instance = super(LocalLLM, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the local language model.
        
        Args:
            model_name: Name of the model to use
        """
        if self._initialized:
            return
            
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        try:
            # Load tokenizer with caching
            logger.info(f"Loading tokenizer for {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(CACHE_DIR),
                local_files_only=False,
                trust_remote_code=True
            )
            
            # Load model with simpler configuration first
            logger.info(f"Loading model {model_name}")
            try:
                # First try loading with device_map="auto"
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    cache_dir=str(CACHE_DIR),
                    local_files_only=False,
                    trust_remote_code=True
                )
            except Exception as e1:
                logger.warning(f"Could not load with device_map='auto': {str(e1)}")
                try:
                    # Try loading without device_map
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        cache_dir=str(CACHE_DIR),
                        local_files_only=False,
                        trust_remote_code=True
                    )
                    if self.device == "cuda":
                        self.model = self.model.to(self.device)
                except Exception as e2:
                    # Try loading in 8-bit if available
                    logger.warning(f"Standard loading failed: {str(e2)}")
                    try:
                        self.model = AutoModelForCausalLM.from_pretrained(
                            model_name,
                            load_in_8bit=True,
                            device_map="auto",
                            cache_dir=str(CACHE_DIR),
                            local_files_only=False,
                            trust_remote_code=True
                        )
                    except Exception as e3:
                        raise Exception(f"All loading attempts failed: {str(e3)}")
            
            # Create text generation pipeline
            logger.info("Creating text generation pipeline")
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise Exception(f"Error loading model {model_name}: {str(e)}")
    
    def generate_response(self, 
                         prompt: str, 
                         max_new_tokens: int = MAX_NEW_TOKENS,
                         temperature: float = TEMPERATURE,
                         top_p: float = TOP_P,
                         num_return_sequences: int = 1) -> str:
        """Generate a response using the local model.
        
        Args:
            prompt: The input prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            num_return_sequences: Number of sequences to generate
            
        Returns:
            Generated text response
        """
        try:
            # Generate text
            outputs = self.generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True
            )
            
            # Extract and clean the response
            response = outputs[0]['generated_text']
            response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise Exception(f"Error generating response: {str(e)}")
    
    def format_prompt(self, 
                     query: str, 
                     context: List[Dict[str, Any]], 
                     tool_response: Dict[str, Any]) -> str:
        """Format the prompt with context and tool response.
        
        Args:
            query: User query
            context: Retrieved context from knowledge base
            tool_response: Response from selected tool
            
        Returns:
            Formatted prompt
        """
        # Format context
        context_text = ""
        if context:
            context_text = "Here's some relevant information:\n"
            context_text += "\n".join([f"- {doc['text']}" for doc in context])
            context_text += "\n\n"
        
        # Format tool response
        tool_text = ""
        if isinstance(tool_response, dict):
            tool_text = "Based on my analysis:\n"
            for key, value in tool_response.items():
                if isinstance(value, list):
                    tool_text += f"{key}:\n" + "\n".join([f"- {item}" for item in value]) + "\n"
                else:
                    tool_text += f"{key}: {value}\n"
        
        # Create prompt
        prompt = f"""You are Asha, an AI career advisor focused on helping women in tech. 
Your responses should be empathetic, encouraging, and practical.

{context_text}
{tool_text}

User Query: {query}

Asha: I understand you're looking for information about {query}. Let me help you with that."""
        
        return prompt

def get_local_llm() -> LocalLLM:
    """Get a LocalLLM instance with configured model."""
    model_name = os.getenv('LLM_MODEL', DEFAULT_MODEL)
    return LocalLLM(model_name)





