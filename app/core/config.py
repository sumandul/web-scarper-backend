 
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env into environment

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
DATABASE_URL= os.getenv("DATABASE_URL")