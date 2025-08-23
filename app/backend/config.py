import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

URL_DATABASE = os.getenv("URL_DATABASE")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


LOG_DIR = Path('logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_CONF = {
    "format": "Log: [{extra[log_id]}:{time} - {level} - {message} ",
    "enqueue": True,
    "rotation": "10 MB",
    "retention": "10 days"
}