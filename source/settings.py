import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", "True").lower == "true"

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///test.db")

TLL_DEFAULT = int(os.environ.get("TLL_DEFAULT", "30"))


