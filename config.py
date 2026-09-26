import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

@dataclass(frozen=True)
class Settings:
    max_items: int
    positive_threshold: float
    negative_threshold: float
    database_path: str

settings = Settings(
    max_items=int(os.getenv("MAX_ITEMS", "500")),
    positive_threshold=float(os.getenv("POSITIVE_THRESHOLD", "0.05")),
    negative_threshold=float(os.getenv("NEGATIVE_THRESHOLD", "-0.05")),
    database_path=os.getenv("DATABASE_PATH", str(BASE_DIR / "sentio.db")),
)
