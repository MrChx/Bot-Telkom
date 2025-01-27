import os
import telebot
from dotenv import load_dotenv
from app.database import UserDatabase

load_dotenv()

class HelperBot:
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv('HELPER_BOT_TOKEN'))
        self.db = UserDatabase()
        
        def check_login(func):
            def wrapper(message):
                if not self.db.is_login_valid(message.from_user.id):
                    self.bot.reply_to(
                        message,
                        "Silakan login terlebih dahulu melalui bot auth untuk menggunakan layanan ini.\n"
                        f"Login di: {os.getenv('WEB_LOGIN_URL')}?telegram_id={message.from_user.id}"
                    )
                    return
                return func(message)
            return wrapper
        
        self.tutorials = {
            'kabel_fiber': {
                'text': os.getenv('TUTORIAL_1_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_1_IMAGE_FILE_ID')
            },
            'tutorial_2': {
                'text': os.getenv('TUTORIAL_2_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_2_IMAGE_FILE_ID')
            }
        }

        @self.bot.message_handler(commands=list(self.tutorials.keys()))
        @check_login
        def send_tutorial(message):
            command = message.text[1:]
            if command in self.tutorials:
                tutorial = self.tutorials[command]
                
                if tutorial['text']:
                    self.bot.reply_to(message, tutorial['text'])
                
                if tutorial['image_file_id']:
                    self.bot.send_photo(message.chat.id, tutorial['image_file_id'])
            pass

        # Handler untuk bantuan
        @self.bot.message_handler(commands=['help'])
        @check_login
        def send_help(message):
            help_text = (
                "Perintah tersedia:\n"
                "/tutorial_1 - Tutorial Pertama\n"
                "/tutorial_2 - Tutorial Kedua\n"
                "/help - Daftar Perintah"
            )
            self.bot.reply_to(message, help_text)
            pass


        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            response = (
                "Hai! Saya adalah bot helper. Gunakan perintah tutorial "
                "atau /help untuk melihat daftar perintah yang tersedia."
            )
            self.bot.reply_to(message, response)
            
        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):

            file_id = message.photo[-1].file_id
            
            response = (
                f"File ID foto: {file_id}\n\n"
                "Simpan file ID ini di environment variable Anda:\n"
                "TUTORIAL_1_IMAGE_FILE_ID atau TUTORIAL_2_IMAGE_FILE_ID"
            )
            self.bot.reply_to(message, response)

    def start_bot(self):
        print("Bot Helper sedang berjalan...")
        self.bot.polling(none_stop=True)