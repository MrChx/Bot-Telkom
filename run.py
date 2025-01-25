import threading
from bot.authBot import AuthBot
from bot.asistenBot import AssistantBot
from bot.helperBot import HelperBot
from app.routes import app

def jalankan_bot_auth():
    bot_auth = AuthBot()
    bot_auth.start_bot()

def jalankan_bot_asisten():
    bot_asisten = AssistantBot()
    bot_asisten.start_bot()

def jalankan_bot_helper():
    bot_helper = HelperBot()
    bot_helper.start_bot()

def jalankan_web():
    app.run(debug=True, port=5002)

def main():
    # Thread untuk bot autentikasi
    thread_auth = threading.Thread(target=jalankan_bot_auth)
    thread_auth.start()

    # Thread untuk bot asisten
    thread_asisten = threading.Thread(target=jalankan_bot_asisten)
    thread_asisten.start()

    # Thread untuk bot helper
    thread_helper = threading.Thread(target=jalankan_bot_helper)
    thread_helper.start()

    # Jalankan aplikasi web
    jalankan_web()

if __name__ == '__main__':
    main()