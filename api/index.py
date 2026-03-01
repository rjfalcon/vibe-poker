"""Vercel serverless entry point for the FastAPI backend."""
import sys
from pathlib import Path

# Make the backend package importable from this directory
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app  # noqa: E402 - path must be set first

__all__ = ["app"]
