import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"
LOG_DIR = BASE_DIR / "logs"

load_dotenv(BASE_DIR / ".env")

CITIES = {
    "Mumbai": {"latitude": 19.07, "longitude": 72.87},
    "Delhi": {"latitude": 28.61, "longitude": 77.21},
    "Bengaluru": {"latitude": 12.97, "longitude": 77.59},
}

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "aqi_db"