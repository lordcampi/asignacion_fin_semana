"""Entrypoint for Streamlit Cloud deployment."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.app.streamlit_app import run_app

run_app()
