"""
Copyright (c) 2025 Your Name
All rights reserved.

This software is licensed under the MIT License.
Unauthorized use or redistribution of this code is prohibited.
"""

import config
import state

from boting.keyboard import get_main_keyboard
from boting.reporter import send_daily_report
from trading.orders import current_balance, check_balance, place_market_sell_order

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Helper to restrict access only to authorized chat ID
def is_authorized(message):
    return message.chat.id == int(config.CHAT_ID)

# -----------------------------------
@config.bot.message_handler(commands=['start'])
def handle_start(message):
    if not is_authorized(message):
        return
    config.bot.send_message(config.CHAT_ID, "Hello...", reply_markup=get_main_keyboard())

# Generic handler template for updating float values via command
def handle_update_float_command(command_name, update_function, error_message):
    @config.bot.message_handler(commands=[command_name])
    def handler(message):
        if not is_authorized(message):
            return
        try:
            new_value = float(message.text.split()[1])
            update_function(new_value)
        except Exception as e:
            config.bot.send_message(config.CHAT_ID, f"❌ {error_message}: {str(e)}", reply_markup=get_main_keyboard())
    return handler

# Register float update commands
handle_update_float_command('update_min_usdt', config.updater.update_min_usdt, "Error updating minimum trade amount")
handle_update_float_command('update_max_usdt', config.updater.update_max_usdt, "Error updating maximum trade amount")
handle_update_float_command('update_ema_short', config.updater.update_ema_short, "Error setting short EMA value")
handle_update_float_command('update_ema_long', config.updater.update_ema_long, "Error setting long EMA value")
handle_update_float_command('update_rsi_period', config.updater.update_rsi_period, "Error updating RSI period")
handle_update_float_command('update_rsi_overbought', config.updater.update_rsi_overbought, "Error updating RSI overbought level")
handle_update_float_command('update_rsi_oversell', config.updater.update_rsi_oversell, "Error updating RSI oversell level")
handle_update_float_command('update_price_increase_min', config.updater.update_price_increase_min, "Error updating minimum price increase")
handle_update_float_command('update_price_increase_max', config.updater.update_price_increase_max, "Error updating maximum price increase")

# Integer updates (monitoring minutes, trade interval, max loss)
def handle_update_int_command(command_name, update_function, error_message):
    @config.bot.message_handler(commands=[command_name])
    def handler(message):
        if not is_authorized(message):
            return
        try:
            new_value = int(message.text.split()[1])
            update_function(new_value)
        except Exception as e:
            config.bot.send_message(config.CHAT_ID, f"❌ {error_message}: {str(e)}", reply_markup=get_main_keyboard())
    return handler

handle_update_int_command('update_monitoring_minutes', config.updater.update_monitoring_minutes, "Error updating monitoring minutes")
handle_update_int_command('update_trade_interval', config.updater.update_trade_interval, "Error updating trade interval")
handle_update_int_command('max_loss_per_hour', config.updater.update_max_loss, "Error updating maximum loss per hour")

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "⚡️ Trading Variables")
def trade_vars_handler(message):
    if not is_authorized(message):
        return
    msg_lines = [
        f"RSI_PERIOD: {config.RSI_PERIOD}",
        f"RSI_OVERBOUGHT: {config.RSI_OVERBOUGHT}",
        f"RSI_OVERSELL: {config.RSI_OVERSELL}",
        f"EMA_SHORT: {config.EMA_SHORT}",
        f"EMA_LONG: {config.EMA_LONG}",
    ]
    for line in msg_lines:
        config.bot.send_message(config.CHAT_ID, line)

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "🚀 Start Trading")
def start_trading_handler(message):
    if not is_authorized(message):
        return
    if state.is_trading_active:
        config.bot.send_message(config.CHAT_ID, "⚠️ Trading is already active!", reply_markup=get_main_keyboard())
        return
    state.is_trading_active = True
    config.bot.send_message(config.CHAT_ID, "🔔 Starting trading now...", reply_markup=get_main_keyboard())

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "💰 Account Balance")
def balance_handler(message):
    if not is_authorized(message):
        return
    state.balance = check_balance()
    config.bot.send_message(config.CHAT_ID, f"🔑 Your current USDT balance is: {state.balance} USDT", reply_markup=get_main_keyboard())

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "💰 Current Balance")
def curbalance_handler(message):
    if not is_authorized(message):
        return
    report = current_balance()
    if report:
        config.bot.send_message(config.CHAT_ID, report, reply_markup=get_main_keyboard())
    else:
        config.bot.send_message(config.CHAT_ID, "🚫 No open trades currently.", reply_markup=get_main_keyboard())

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "🗓️ Daily Report")
def daily_report_handler(message):
    if not is_authorized(message):
        return
    send_daily_report()

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "ℹ️ Trading Status")
def trade_status_handler(message):
    if not is_authorized(message):
        return
    config.bot.send_message(message.chat.id, f" Trading is {'Active ✅' if state.is_trading_active else 'Stopped ⛔️'}")
    config.bot.send_message(message.chat.id, f" In Position  {'YES ✅' if state.in_position else 'NO ⛔️'}")
    symbol = state.current_symbol if state.current_symbol else "NO ⛔️"
    config.bot.send_message(message.chat.id, f"Symbol: {symbol} {'✅' if state.current_symbol else ''}")

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "🛑 Stop Trading")
def confirm_stop(message):
    if not is_authorized(message):
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Yes, stop trading"), KeyboardButton("❌ Cancel"))
    config.bot.send_message(message.chat.id, "Are you sure you want to stop trading?", reply_markup=markup)

@config.bot.message_handler(func=lambda message: message.text == "✅ Yes, stop trading")
def confirmed_stop(message):
    if not is_authorized(message):
        return
    if state.in_position and state.current_symbol:
        state.is_trading_active = False
        place_market_sell_order(state.current_symbol)
    else:
        config.bot.send_message(config.CHAT_ID, "🚫 No open trades currently.", reply_markup=get_main_keyboard())

@config.bot.message_handler(func=lambda message: message.text == "❌ Cancel")
def cancel_stop(message):
    if not is_authorized(message):
        return
    config.bot.send_message(message.chat.id, "Trading is active ✅", reply_markup=get_main_keyboard())

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "🛑 Stop Bot")
def confirm_stopp(message):
    if not is_authorized(message):
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Yes, stop bot"), KeyboardButton("❌ Cancel"))
    config.bot.send_message(message.chat.id, "Are you sure you want to stop the bot?", reply_markup=markup)

@config.bot.message_handler(func=lambda message: message.text == "✅ Yes, stop bot")
def confirmed_stopp(message):
    if not is_authorized(message):
        return
    state.is_trading_active = False
    config.bot.send_message(message.chat.id, "Bot stopped ✅", reply_markup=get_main_keyboard())

@config.bot.message_handler(func=lambda message: message.text == "❌ Cancel")
def cancel_stopp(message):
    if not is_authorized(message):
        return
    config.bot.send_message(message.chat.id, "Bot is running ✅", reply_markup=get_main_keyboard())

# -----------------------------------
@config.bot.message_handler(func=lambda message: message.text == "⚙️ Edit Variables")
def settings_handler(message):
    if not is_authorized(message):
        return
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("MIN_INCREASE 🚀", callback_data="update_price_increase_min"),
        InlineKeyboardButton("MAX_INCREASE 🚀", callback_data="update_price_increase_max"),
        InlineKeyboardButton("MONITOR_MINUTES ⏳", callback_data="update_monitoring_minutes"),
        InlineKeyboardButton("TRADE_INTERVAL ⏳", callback_data="update_trade_interval"),
        InlineKeyboardButton("MAX_LOSS_HOUR 💰", callback_data="update_max_loss"),
        InlineKeyboardButton("MIN_TRADE_USDT 💰", callback_data="update_min_usdt"),
        InlineKeyboardButton("MAX_TRADE_USDT 💵", callback_data="update_max_usdt"),
        InlineKeyboardButton("EMA_SHORT 💰", callback_data="update_ema_short"),
        InlineKeyboardButton("EMA_LONG 💵", callback_data="update_ema_long"),
        InlineKeyboardButton("RSI_PERIOD 💵", callback_data="update_rsi_period"),
        InlineKeyboardButton("RSI_OVERBOUGHT 💵", callback_data="update_rsi_overbought"),
        InlineKeyboardButton("RSI_OVERSELL 💵", callback_data="update_rsi_oversell"),
    )
    config.bot.send_message(config.CHAT_ID, "🔧 Select the variable you want to edit:", reply_markup=markup)

@config.bot.callback_query_handler(func=lambda call: True)
def handle_setting_buttons(call):
    if call.message.chat.id != int(config.CHAT_ID):
        return
    msg = config.bot.send_message(config.CHAT_ID, f"📝 Send the new value for: {call.data}")
    config.bot.register_next_step_handler(msg, lambda m: process_setting_value(call.data, m.text))

def process_setting_value(setting, value):
    try:
        value = float(value)
        if setting == "update_min_usdt":
            config.updater.update_min_usdt(value)
        elif setting == "update_max_usdt":
            config.updater.update_max_usdt(value)
        elif setting == "update_ema_short":
            config.updater.update_ema_short(value)
        elif setting == "update_ema_long":
            config.updater.update_ema_long(value)
        elif setting == "update_rsi_period":
            config.updater.update_rsi_period(value)
        elif setting == "update_rsi_overbought":
            config.updater.update_rsi_overbought(value)
        elif setting == "update_rsi_oversell":
            config.updater.update_rsi_oversell(value)
        else:
            config.bot.send_message(config.CHAT_ID, "❌ Unknown setting.")
    except Exception as e:
        config.bot.send_message(config.CHAT_ID, f"❌ Input error: {str(e)}")
