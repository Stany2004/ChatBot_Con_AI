"""Utilities for interacting with Google's Gemini API."""

import os
from typing import Any, Dict, List, Optional, Generator

import google.generativeai as genai
from google.generativeai.types import SafetySettingDict

def initialize_gemini(api_key: Optional[str] = None) -> None:
    """Initialize the Gemini API with the provided API key."""
    if api_key is None:
        api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("No Gemini API key provided")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List available models to verify API key works
        available_models = genai.list_models()
        if not available_models:
            raise ValueError("No models available. Check your API key.")
            
        # Print available models for debugging
        print("Available models:", [m.name for m in available_models])
        
        # Try different models in order of preference
        model_names = [
            "models/gemini-pro",  # Standard model
            "models/gemini-2.0-flash",  # Lighter model
            "models/gemini-2.0-flash-lite",  # Even lighter model
        ]
        
        initialized = False
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, testing the API.", safety_settings=[])
                if response:
                    initialized = True
                    break
            except Exception:
                continue
                
        if not initialized:
            raise ValueError("Failed to initialize with any available model")
            
    except Exception as e:
        raise ValueError(f"Failed to initialize Gemini API: {str(e)}")

def get_gemini_chat(
    model: str = "gemini-pro",
    temperature: float = 0.7,
    top_p: float = 0.8,
    top_k: int = 40,
    max_output_tokens: int = 2048,
    safety_settings: Optional[List[SafetySettingDict]] = None,
) -> Any:
    """Create and return a Gemini chat instance with the specified parameters."""
    # Try different models in order of preference
    model_names = [
        model,  # Try the requested model first
        "models/gemini-pro",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
    ]
    
    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,  # Use model_name instead of model
                generation_config={
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": max_output_tokens,
                },
                safety_settings=safety_settings or []
            )
            return model.start_chat(history=[])
        except Exception as e:
            last_error = e
            continue
    
    # If we get here, none of the models worked
    raise Exception(f"Failed to create Gemini chat instance with any model: {str(last_error)}")

def get_chat_response(
    chat: Any, 
    message: str,
    stream: bool = False
) -> str:
    """Get a response from the Gemini chat instance."""
    try:
        # Try to use the chat object first
        try:
            response = chat.send_message(message)
            if response and response.text:
                return response.text
        except Exception:
            pass  # Fall back to direct generation
            
        # Try different models if chat fails
        model_names = [
            "models/gemini-pro",
            "models/gemini-2.0-flash",
            "models/gemini-2.0-flash-lite",
        ]
        
        last_error = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(message, safety_settings=[])
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                continue
                
        raise ValueError(f"Failed to get response from any model: {str(last_error)}")
    except Exception as e:
        raise Exception(f"Failed to get chat response: {str(e)}")

def count_tokens(text: str) -> int:
    """Count the number of tokens in the given text using Gemini's tokenizer."""
    # Note: Gemini doesn't provide a direct token counting method
    # This is a rough estimate based on words
    return len(text.split())

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Estimate the cost of the API call based on token usage."""
    # Gemini Pro pricing (as of 2024):
    # Input: $0.00025 per 1K tokens
    # Output: $0.0005 per 1K tokens
    input_cost = (input_tokens / 1000) * 0.00025
    output_cost = (output_tokens / 1000) * 0.0005
    return input_cost + output_cost