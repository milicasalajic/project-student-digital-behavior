"""Centralna konfiguracija (učitava se iz .env ako postoji, inače podrazumevane vrednosti)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv je opcioni; radimo i bez njega
    pass

ROOT = Path(__file__).resolve().parent.parent

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_V1 = os.getenv("DB_V1", "sbp-v1")
DB_V2 = os.getenv("DB_V2", "sbp-v2")

_default_csv = ROOT / "data" / "global_student_digital_behavior_dataset.csv"
CSV_PATH = os.getenv("CSV_PATH", str(_default_csv))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))
TOTAL_ROWS = 500_000  # za tqdm progres
