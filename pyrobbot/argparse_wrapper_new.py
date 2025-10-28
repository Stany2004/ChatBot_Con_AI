"""Argument parser wrapper for the application."""
import argparse
import sys
from typing import Optional, Sequence

def get_parsed_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(description="Chat with Gemini AI")
    
    # Common arguments
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (0.0 to 1.0)",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.8,
        help="Nucleus sampling parameter (0.0 to 1.0)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=40,
        help="Top-k sampling parameter",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Maximum number of tokens in the response",
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Browser interface (default)
    browser_parser = subparsers.add_parser("browser", help="Launch browser interface")
    browser_parser.set_defaults(run_command=lambda args: browser_chat(args))
    
    # Terminal chat
    terminal_parser = subparsers.add_parser("terminal", help="Chat in terminal")
    terminal_parser.set_defaults(run_command=lambda args: terminal_chat(args))
    
    # Voice chat
    voice_parser = subparsers.add_parser("voice", help="Voice chat mode")
    voice_parser.set_defaults(run_command=lambda args: voice_chat(args))
    
    args = parser.parse_args(argv)
    
    # Default to browser interface if no command specified
    if not hasattr(args, "run_command"):
        args.run_command = lambda args: browser_chat(args)
    
    return args

# Import these after function definition to avoid circular imports
from .command_definitions_new import browser_chat, terminal_chat, voice_chat