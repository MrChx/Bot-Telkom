import os
import telebot
import requests
from telebot import types
from dotenv import load_dotenv
from app.database import UserDatabase

load_dotenv()

class HelperBot:
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv('HELPER_BOT_TOKEN'))
        self.db = UserDatabase()
        self.api_base_url = os.getenv('WEB_LOGIN_URL', '').rstrip('/') 
        
        def check_login(func):
            def wrapper(message):
                if not self.db.is_login_valid(message.from_user.id):
                    self.bot.reply_to(
                        message,
                        "Silakan login terlebih dahulu melalui bot auth untuk menggunakan layanan ini.\n\n"
                        f"Login di: {os.getenv('WEB_LOGIN_URL')}?telegram_id={message.from_user.id}"
                    )
                    return
                return func(message)
            return wrapper

        @self.bot.message_handler(commands=['start'])
        @check_login
        def send_welcome(message):
            welcome_text = (
                "Selamat datang di Bot Helper! 🤖\n\n"
                "Silakan pilih tutorial yang ingin Anda lihat:"
            )
            self.show_tutorial_menu(message.chat.id, welcome_text)

        @self.bot.message_handler(commands=['help', 'menu'])
        @check_login
        def send_help(message):
            help_text = "Silakan pilih tutorial yang ingin Anda lihat:"
            self.show_tutorial_menu(message.chat.id, help_text)

        # Handler untuk callback dari inline keyboard
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            response = requests.get(f"{self.api_base_url}/api/tutorials/{call.data}")
            
            if response.status_code == 200:
                data = response.json()
                if data['berhasil']:
                    tutorial = data['tutorial']
                    
                    if tutorial['text_content']:
                        self.bot.send_message(call.message.chat.id, tutorial['text_content'])
                    
                    if tutorial['image_file_id']:
                        self.bot.send_photo(call.message.chat.id, tutorial['image_file_id'])
                    
                    back_text = "Ingin melihat tutorial lainnya?"
                    self.show_tutorial_menu(call.message.chat.id, back_text)
            
            self.bot.answer_callback_query(call.id)
            
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            response = (
                "Hai! Saya adalah bot helper. Pilih tutorial yang ingin Anda lihat:"
            )
            self.show_tutorial_menu(message.chat.id, response)
            
        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            file_id = message.photo[-1].file_id
            
            response = (
                f"File ID foto: {file_id}\n\n"
                "Silakan tambahkan foto ini ke tutorial di dashboard admin."
            )
            self.bot.reply_to(message, response)

    def show_tutorial_menu(self, chat_id, text):
        response = requests.get(f"{self.api_base_url}/api/tutorials")
        
        if response.status_code != 200:
            self.bot.send_message(chat_id, "Gagal mengambil daftar tutorial.")
            return
            
        data = response.json()
        if not data['berhasil'] or not data['tutorials']:
            self.bot.send_message(chat_id, "Tidak ada tutorial tersedia saat ini.")
            return
            
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        tutorial_buttons = []
        for tutorial in data['tutorials']:
            tutorial_buttons.append(
                types.InlineKeyboardButton(
                    text=tutorial['title'], 
                    callback_data=tutorial['command']
                )
            )
        
        markup.add(*tutorial_buttons)
        
        self.bot.send_message(chat_id, text, reply_markup=markup)

    def start_bot(self):
        print("Bot Helper sedang berjalan...")
        self.bot.polling(none_stop=True)