"""
Autonomous Communication Manager — Entry point.

Starts the FastAPI server with agentica-powered triage and draft generation.

Usage:
    python main.py                    # Start on http://127.0.0.1:8000
    OPENROUTER_API_KEY=sk-... python main.py
"""

import asyncio
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()


def check_env() -> None:
    """Warn if required env vars are missing."""
    if not os.getenv("OPENROUTER_API_KEY"):
        print(
            "WARNING: OPENROUTER_API_KEY not set. "
            "Agentica features will fail at runtime.\n"
            "Set it in .env or export it before starting."
        )


def main() -> None:
    check_env()

    # Import after env is loaded so agentica sees the key
    from emailmanagement.api import app

    print("Starting Autonomous Communication Manager on http://127.0.0.1:8000")
    print("API docs available at http://127.0.0.1:8000/docs")

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
