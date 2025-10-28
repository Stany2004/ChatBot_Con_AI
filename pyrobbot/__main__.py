#!/usr/bin/env python3
"""Program's entry point."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from pyrobbot.argparse_wrapper_new import get_parsed_args


def main(argv=None):
    """Program's main routine."""
    try:
        args = get_parsed_args(argv=argv)
        if hasattr(args, 'run_command'):
            return args.run_command(args=args)
        else:
            raise AttributeError("No run_command found in parsed arguments")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())