import os
from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = os.environ.get("DEBUG", "True") == "True"

DB_URL = "sqlite+aiosqlite:///test.db" if DEBUG else os.environ.get("DB_URL")

APP_HOST: str = os.environ.get("APP_HOST", "localhost")
APP_PORT: int = int(os.environ.get("APP_PORT", "6969"))

TLL_DEFAULT: int = int(os.environ.get("TLL_DEFAULT", "30"))
