import os
from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = os.environ.get("DEBUG", "True") == "True"

DB_URL = "sqlite+aiosqlite:///test.db" if DEBUG else os.environ.get("DB_URL")

APP_HOST: str = "localhost" if DEBUG else os.environ.get("APP_HOST")
APP_PORT: int = 6969 if DEBUG else int(os.environ.get("APP_PORT"))

TLL_DEFAULT: int = int(os.environ.get("TLL_DEFAULT", "30"))
