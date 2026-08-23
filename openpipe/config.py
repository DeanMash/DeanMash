"""Runtime configuration for OpenPipe."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("OPENPIPE_DATA_DIR", ROOT / "data"))
DB_PATH = Path(os.getenv("OPENPIPE_DB_PATH", DATA_DIR / "openpipe.db"))
HOST = os.getenv("OPENPIPE_HOST", "0.0.0.0")
PORT = int(os.getenv("OPENPIPE_PORT", "8090"))
DASHBOARD_TOKEN = os.getenv("OPENPIPE_DASHBOARD_TOKEN", "")
EMAIL_MODE = os.getenv("OPENPIPE_EMAIL_MODE", "demo")  # demo | stub | live
BUSINESS_NAME = os.getenv("OPENPIPE_BUSINESS_NAME", "Horizon Cover Brokers")
BUSINESS_VERTICAL = os.getenv("OPENPIPE_BUSINESS_VERTICAL", "insurance")
TIMEZONE = os.getenv("OPENPIPE_TIMEZONE", "Africa/Harare")
DAILY_SEND_CAP = int(os.getenv("OPENPIPE_DAILY_SEND_CAP", "80"))
AUTO_RUN_ENABLED = os.getenv("OPENPIPE_AUTO_RUN", "1") not in {"0", "false", "False"}
AUTO_RUN_INTERVAL_SEC = int(os.getenv("OPENPIPE_AUTO_RUN_INTERVAL", "60"))
