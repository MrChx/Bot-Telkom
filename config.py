import os
from dotenv import load_dotenv

# Muat variabel environment
load_dotenv()

class Config:
    # Ambil variabel dari .env dengan aman
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE')
    AUTH_BOT_TOKEN = os.getenv('AUTH_BOT_TOKEN')
    ASSISTANT_BOT_TOKEN = os.getenv('ASSISTANT_BOT_TOKEN')
    ASSISTANT_GROUP_LINK = os.getenv('ASSISTANT_GROUP_LINK')
    HELPER_BOT_TOKEN = os.getenv('HELPER_BOT_TOKEN')
    HELPER_BOT_LINK = os.getenv('HELPER_BOT_LINK')
    WEB_LOGIN_URL = os.getenv('WEB_LOGIN_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'