"""Command definitions for the application."""
import argparse
from typing import Optional

from pyrobbot.chat_config_new import ChatConfig
from pyrobbot.chat_new import Chat

def setup_chat(args: argparse.Namespace) -> Chat:
    """Set up chat with appropriate configuration."""
    config = ChatConfig(
        provider="gemini",  # Default to Gemini
        gemini_config={
            "temperature": args.temperature if hasattr(args, 'temperature') else 0.7,
            "top_p": args.top_p if hasattr(args, 'top_p') else 0.8,
            "top_k": args.top_k if hasattr(args, 'top_k') else 40,
            "max_output_tokens": args.max_tokens if hasattr(args, 'max_tokens') else 2048,
        }
    )
    return Chat(config=config)

def browser_chat(args: Optional[argparse.Namespace] = None) -> None:
    """Launch the browser interface."""
    from .app.app import run_app
    run_app()

def terminal_chat(args: Optional[argparse.Namespace] = None) -> None:
    """Start chat in terminal mode."""
    chat = setup_chat(args or argparse.Namespace())
    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            print("\nAssistant:", end=" ")
            response = chat.send_message(user_input)
            print(response)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue

def voice_chat(args: Optional[argparse.Namespace] = None) -> None:
    """Start voice chat mode."""
    from .voice_chat import VoiceChat
    chat = setup_chat(args or argparse.Namespace())
    voice_chat = VoiceChat(chat=chat)
    voice_chat.start()