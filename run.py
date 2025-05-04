import threading
import signal
import sys
import time
import os
from bot.authBot import AuthBot
from bot.asistenBot import AssistantBot
from bot.helperBot import HelperBot
from app.routes import app

# Event untuk signaling thread shutdown
stop_event = threading.Event()

def jalankan_bot_auth():
    try:
        bot_auth = AuthBot()
        while not stop_event.is_set():
            bot_auth.start_bot()
    except Exception as e:
        print(f"Error bot auth: {e}")

def jalankan_bot_asisten():
    try:
        bot_asisten = AssistantBot()
        while not stop_event.is_set():
            bot_asisten.start_bot()
    except Exception as e:
        print(f"Error bot asisten: {e}")

def jalankan_bot_helper():
    try:
        bot_helper = HelperBot()
        while not stop_event.is_set():
            bot_helper.start_bot()
    except Exception as e:
        print(f"Error bot helper: {e}")

def jalankan_web():
    try:
        port = int(os.getenv('PORT', 5002))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error web server: {e}")

def signal_handler(sig, frame):
    print("\nMenghentikan semua proses...")
    stop_event.set()
    sys.exit(0)

def main():
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Thread untuk bot-bot
    thread_auth = threading.Thread(target=jalankan_bot_auth)
    thread_asisten = threading.Thread(target=jalankan_bot_asisten)
    thread_helper = threading.Thread(target=jalankan_bot_helper)
    thread_web = threading.Thread(target=jalankan_web)

    # Mulai semua thread
    thread_auth.start()
    thread_asisten.start()
    thread_helper.start()
    thread_web.start()

    # Tunggu semua thread selesai
    thread_auth.join()
    thread_asisten.join()
    thread_helper.join()
    thread_web.join()

if __name__ == '__main__':
    main()