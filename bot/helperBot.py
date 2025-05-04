import os
import telebot
from telebot import types
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
            'tutorial_1': {
                'text': os.getenv('TUTORIAL_1_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_1_IMAGE_FILE_ID'),
                'title': 'Tutorial Pertama'
            },
            'tutorial_2': {
                'text': os.getenv('TUTORIAL_2_TEXT'),
                'image_file_id': os.getenv('TUTORIAL_2_IMAGE_FILE_ID'),
                'title': 'Tutorial Kedua'
            }
        }

        @self.bot.message_handler(commands=['start'])
        @check_login
        def send_welcome(message):
            welcome_text = (
                "Selamat datang di Bot Helper! 🤖\n\n"
                "Silakan pilih tutorial yang ingin Anda lihat:"
            )
            self.show_tutorial_menu(message.chat.id, welcome_text)

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
        @self.bot.message_handler(commands=['help', 'menu'])
        @check_login
        def send_help(message):
            help_text = "Silakan pilih tutorial yang ingin Anda lihat:"
            self.show_tutorial_menu(message.chat.id, help_text)
            pass

        # Handler untuk callback dari inline keyboard
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            if call.data in self.tutorials:
                tutorial = self.tutorials[call.data]
                
                # Kirim pesan tutorial
                if tutorial['text']:
                    self.bot.send_message(call.message.chat.id, tutorial['text'])
                
                # Kirim gambar tutorial jika ada
                if tutorial['image_file_id']:
                    self.bot.send_photo(call.message.chat.id, tutorial['image_file_id'])
                
                # Menampilkan menu kembali setelah menampilkan tutorial
                back_text = "Ingin melihat tutorial lainnya?"
                self.show_tutorial_menu(call.message.chat.id, back_text)
                
                # Hapus tanda loading pada tombol yang diklik
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
                "Simpan file ID ini di environment variable Anda:\n"
                "TUTORIAL_1_IMAGE_FILE_ID atau TUTORIAL_2_IMAGE_FILE_ID"
            )
            self.bot.reply_to(message, response)

    def show_tutorial_menu(self, chat_id, text):
        # Buat markup untuk inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Tambahkan tombol untuk setiap tutorial
        tutorial_buttons = []
        for tutorial_id, tutorial_info in self.tutorials.items():
            tutorial_buttons.append(
                types.InlineKeyboardButton(
                    text=tutorial_info['title'], 
                    callback_data=tutorial_id
                )
            )
        
        markup.add(*tutorial_buttons)
        
        self.bot.send_message(chat_id, text, reply_markup=markup)

    def start_bot(self):
        print("Bot Helper sedang berjalan...")
        self.bot.polling(none_stop=True)