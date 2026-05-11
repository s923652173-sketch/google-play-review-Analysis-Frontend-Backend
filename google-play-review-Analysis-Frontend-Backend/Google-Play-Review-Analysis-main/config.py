import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"
APPS_CSV = f"{DATA_DIR}/apps.csv"
REVIEWS_CSV = f"{DATA_DIR}/reviews.csv"
RECOMMENDATIONS_CSV = f"{DATA_DIR}/recommendations.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
