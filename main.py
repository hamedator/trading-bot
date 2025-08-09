import time
import threading

import config
from state import *

# Trading functions
from trading.strategy import strategy_loop
from trading.streaming import bootstrap_history, start_socket_for_group, chunk_list
from boting.reporter import daily_report_scheduler
import boting.handlers  # import handlers to register commands/events
from utils.symbols import get_symbols

# Telegram bot and chat_id are imported from config which should load from environment variables
from config import bot, CHAT_ID, TELEGRAM_BOT_TOKEN

# -----------------------------------------
if __name__ == '__main__':
    # Load trading symbols and their info
    symbols_info = get_symbols()
    all_symbols = [s['symbol'] for s in symbols_info]

    # Split symbols into groups to open separate websocket connections
    symbol_groups = list(chunk_list(all_symbols, config.SYMBOLS_PER_SOCKET))
    for group in symbol_groups:
        start_socket_for_group(group)

    # Start the main trading strategy loop in a background thread
    threading.Thread(target=strategy_loop, daemon=True).start()

    def run_bot_forever():
        print("🔁 Bot polling started")  # <-- Important to log start
        while True:
            try:
                # Start Telegram bot polling; this blocks until an exception occurs
                config.bot.infinity_polling()
            except Exception as e:
                print(f"[Polling Error] {e} - Restarting after 5 seconds")
                try:
                    config.bot.send_message(CHAT_ID, f"🚫 Polling error occurred: {e}")
                except Exception:
                    # Avoid crash if sending message fails (e.g., network issues)
                    pass
                time.sleep(5)

    # Start bot polling in a separate daemon thread
    threading.Thread(target=run_bot_forever, daemon=True).start()

    # Keep the main thread alive indefinitely
    while True:
        time.sleep(60)
