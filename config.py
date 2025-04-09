import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.urandom(24)
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID') 