import os
import telebot
from dotenv import load_dotenv

load_dotenv()

class HelperBot:
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv('HELPER_BOT_TOKEN'))
        
        # Tutorial dari environment variables
        self.tutorials = {
            'tutorial_1': {
                'text': os.getenv('TUTORIAL_1_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_1_IMAGE_FILE_ID')
            },
            'tutorial_2': {
                'text': os.getenv('TUTORIAL_2_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_2_IMAGE_FILE_ID')
            }
        }

        @self.bot.message_handler(commands=list(self.tutorials.keys()))
        def send_tutorial(message):
            command = message.text[1:]
            if command in self.tutorials:
                tutorial = self.tutorials[command]
                
                # Kirim teks tutorial
                if tutorial['text']:
                    self.bot.reply_to(message, tutorial['text'])
                
                # Kirim gambar tutorial
                if tutorial['image_file_id']:
                    self.bot.send_photo(message.chat.id, tutorial['image_file_id'])

        # Handler untuk bantuan
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            help_text = (
                "Perintah tersedia:\n"
                "/tutorial_1 - Tutorial Pertama\n"
                "/tutorial_2 - Tutorial Kedua\n"
                "/help - Daftar Perintah"
            )
            self.bot.reply_to(message, help_text)

        # Handler pesan umum
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            response = (
                "Hai! Saya adalah bot helper. Gunakan perintah tutorial "
                "atau /help untuk melihat daftar perintah yang tersedia."
            )
            self.bot.reply_to(message, response)

    def start_bot(self):
        print("Bot Helper sedang berjalan...")
        self.bot.polling(none_stop=True)