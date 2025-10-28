"""Entrypoint for the package's UI."""

from pyrobbot.app.app_new import run_app as run_gemini_app


def run_app():
    """Create and run the Gemini-powered chat application."""
    run_gemini_app()


if __name__ == "__main__":
    run_app()
