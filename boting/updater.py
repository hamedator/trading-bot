import config
from state import *
from boting.keyboard import get_main_keyboard

def send_update_message(message):
    """Helper function to send a message with the main keyboard."""
    try:
        config.bot.send_message(config.CHAT_ID, message, reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"[Telegram Error] Failed to send message: {e}")

def update_take_profit(new_take_profit):
    config.TAKE_PROFIT_PCT = new_take_profit
    send_update_message(f"💰 Take Profit value set to: {config.TAKE_PROFIT_PCT} USDT.")

def update_stop_loss(new_stop_loss):
    config.STOP_LOSS_PCT = new_stop_loss
    send_update_message(f"💰 Stop Loss value set to: {config.STOP_LOSS_PCT} USDT.")

def update_min_usdt(new_min_usdt):
    config.MIN_USDT = new_min_usdt
    send_update_message(f"💰 Minimum trade amount updated to: {config.MIN_USDT} USDT.")

def update_max_usdt(new_max_usdt):
    config.MAX_USDT = new_max_usdt
    send_update_message(f"💰 Maximum trade amount updated to: {config.MAX_USDT} USDT.")

def update_price_increase_min(new_price_increase_min):
    config.MIN_INCREASE = new_price_increase_min
    send_update_message(f"✅ MIN_INCREASE {config.MIN_INCREASE}%")

def update_price_increase_max(new_price_increase_max):
    config.MAX_INCREASE = new_price_increase_max
    send_update_message(f"✅ MAX_INCREASE {config.MAX_INCREASE}%")

def update_monitoring_minutes(new_minutes):
    config.MONITOR_MINUTES = new_minutes
    send_update_message(f"✅ MONITOR_MINUTES {config.MONITOR_MINUTES} minutes")

def update_trade_interval(new_interval):
    config.TRADE_INTERVAL = new_interval
    send_update_message(f"⏱️ Trade interval updated to: {config.TRADE_INTERVAL} seconds.")

def update_max_loss(new_max_loss):
    config.MAX_LOSS_HOUR = new_max_loss
    send_update_message(f"✅ Maximum hourly loss updated to: {config.MAX_LOSS_HOUR}%")

def update_ema_short(new_ema_short):
    config.EMA_SHORT = new_ema_short
    send_update_message(f"💰 Short EMA value updated to: {config.EMA_SHORT} candles.")

def update_ema_long(new_ema_long):
    config.EMA_LONG = new_ema_long
    send_update_message(f"💰 Long EMA value updated to: {config.EMA_LONG} candles.")

def update_rsi_period(new_rsi_period):
    config.RSI_PERIOD = new_rsi_period
    send_update_message(f"📊 RSI period updated to: {config.RSI_PERIOD} candles.")

def update_rsi_overbought(new_rsi_overbought):
    config.RSI_OVERBOUGHT = new_rsi_overbought
    send_update_message(f"💰 RSI Overbought value updated to: {config.RSI_OVERBOUGHT}.")

def update_rsi_oversell(new_rsi_oversell):
    config.RSI_OVERSELL = new_rsi_oversell
    send_update_message(f"💰 RSI Oversell value updated to: {config.RSI_OVERSELL}.")

def update_macd_signal(new_macd_signal):
    config.MACD_SIGNAL = new_macd_signal
    send_update_message(f"📊 MACD_SIGNAL updated to: {config.MACD_SIGNAL} candles.")

def update_macd_short(new_macd_short):
    config.MACD_SHORT = new_macd_short
    send_update_message(f"💰 MACD_SHORT value updated to: {config.MACD_SHORT}.")

def update_macd_long(new_macd_long):
    config.MACD_LONG = new_macd_long
    send_update_message(f"💰 MACD_LONG value updated to: {config.MACD_LONG}.")

def update_chandelier_period(new_chandelier_period):
    config.CHANDELIER_PERIOD = new_chandelier_period
    send_update_message(f"📊 CHANDELIER_PERIOD updated to: {config.CHANDELIER_PERIOD} candles.")

def update_zlsma_period(new_zlsma_period):
    config.ZLSAMA_PERIOD = new_zlsma_period
    send_update_message(f"💰 ZLSAMA_PERIOD value updated to: {config.ZLSAMA_PERIOD}.")

def update_breakout_period(new_breakout_period):
    config.BREAKOUT_PERIOD = new_breakout_period
    send_update_message(f"💰 BREAKOUT_PERIOD value updated to: {config.BREAKOUT_PERIOD}.")

def update_lstm_model(new_lstm_model):
    config.LSTM_MODEL = new_lstm_model
    send_update_message("LSTM_MODEL AI model activation status changed.")

def update_cnn_model(new_cnn_model):
    config.CNN_MODEL = new_cnn_model
    send_update_message("CNN_MODEL AI model activation status changed.")

def update_xgboost_model(new_xgboost_model):
    config.XGBoost_MODEL = new_xgboost_model
    send_update_message("XGBoost_MODEL AI model activation status changed.")

def update_transformer_model(new_transformer_model):
    config.Transformer_MODEL = new_transformer_model
    send_update_message("Transformer_MODEL AI model activation status changed.")
