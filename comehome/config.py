"""Runtime configuration for ComeHome."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("COMEHOME_DATA_DIR", ROOT / "data"))
DB_PATH = Path(os.getenv("COMEHOME_DB_PATH", DATA_DIR / "comehome.db"))
HOST = os.getenv("COMEHOME_HOST", "0.0.0.0")
PORT = int(os.getenv("COMEHOME_PORT", "8080"))
DASHBOARD_TOKEN = os.getenv("COMEHOME_DASHBOARD_TOKEN", "")
WHATSAPP_MODE = os.getenv("COMEHOME_WHATSAPP_MODE", "demo")  # demo | stub | live
BUSINESS_NAME = os.getenv("COMEHOME_BUSINESS_NAME", "ComeHome Demo Studio")
BUSINESS_VERTICAL = os.getenv("COMEHOME_BUSINESS_VERTICAL", "gym")
TIMEZONE = os.getenv("COMEHOME_TIMEZONE", "Africa/Harare")
CURRENCY = os.getenv("COMEHOME_CURRENCY", "USD")
