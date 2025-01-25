import telebot
import os
from dotenv import load_dotenv
from app.database import UserDatabase

load_dotenv()

class AuthBot:
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv('AUTH_BOT_TOKEN'))
        self.db = UserDatabase()
        self.assistant_group_link = os.getenv('ASSISTANT_GROUP_LINK')
        self.helper_bot_link = os.getenv('HELPER_BOT_LINK')

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            welcome_text = (
                "Selamat datang! 🤖\n\n"
                f"Silakan login di: {os.getenv('WEB_LOGIN_URL')}\n"
                "Setelah login, Anda akan mendapatkan link grup asisten dan bot helper."
            )
            self.bot.reply_to(message, welcome_text)

        @self.bot.message_handler(commands=['login'])
        def send_login_link(message):
            login_text = (
                "Login melalui web: "
                f"{os.getenv('WEB_LOGIN_URL')}\n"
                "Dapatkan akses ke grup asisten dan bot helper setelah login."
            )
            self.bot.reply_to(message, login_text)

    def kirim_link_setelah_login(self, user_id):
        # Kirim link ke grup asisten
        self.bot.send_message(
            user_id, 
            f"Bergabung ke grup asisten: {self.assistant_group_link}"
        )
        
        # Kirim link bot helper
        self.bot.send_message(
            user_id, 
            f"Mulai chat dengan bot helper: {self.helper_bot_link}"
        )

    def start_bot(self):
        print("Bot Autentikasi sedang berjalan...")
        self.bot.polling(none_stop=True)