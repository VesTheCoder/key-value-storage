import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", "True") == "True"

DB_URL = "sqlite+aiosqlite:///test.db" if DEBUG else os.environ.get("DB_URL")

TLL_DEFAULT = int(os.environ.get("TLL_DEFAULT", "30"))
