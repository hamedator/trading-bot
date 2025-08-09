"""
Copyright (c) 2025 Your Name
All rights reserved.

This software is licensed under the MIT License.
Unauthorized use, reproduction, or redistribution of this code is prohibited.
"""

import time
from decimal import Decimal

import config
import state
from boting.keyboard import get_main_keyboard

def send_trade_report(symbol, amount, entry_price, exit_price, usdt_after, trade_status):
    """
    Sends a detailed trade report message via Telegram bot.
    """
    now = time.time()
    profit_or_loss = ((exit_price - entry_price) / entry_price) * 100
    usd_profit_loss = usdt_after - state.usdt_before
    
    report = (
        f"⚡️ New Sell Trade\n"
        f"🔹 Symbol: {symbol}\n"
        f"💸 Entry Price: {entry_price}\n"
        f"💰 Exit Price: {exit_price}\n"
        f"📈 Change: {profit_or_loss:.2f}%\n"
        f"💵 Profit / Loss: {usd_profit_loss:.2f} USDT\n"
        f"💼 Balance Before Trade: {state.usdt_before:.2f} USDT\n"
        f"💼 Balance After Trade: {usdt_after:.2f} USDT\n"
        f"🕒 Exit Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    TAKE_PROFIT_THRESHOLD = config.TP_PCT
    STOP_LOSS_THRESHOLD = config.SL_PCT
    
    if profit_or_loss <= STOP_LOSS_THRESHOLD:
        reason = "Stop Loss"
    elif profit_or_loss >= TAKE_PROFIT_THRESHOLD:
        reason = "Take Profit"
    else:
        reason = "MA Crossover"

    report += f"🔖 Exit Reason: {reason}\n"

    if trade_status == "success":
        state.successful_trades += 1
        state.total_trades_today += 1
        report += "✅ Winning Trade\n"
    else:
        state.failed_trades += 1
        state.total_trades_today += 1
        report += "❌ Losing Trade\n"

        # Track recent losses to stop trading if limit exceeded
        state.recent_losses.append((now, abs(profit_or_loss)))
        one_hour_ago = now - 3600

        loss_sum = sum(loss for _, loss in state.recent_losses)
        if loss_sum >= config.MAX_LOSS_HOUR:
            state.is_trading_active = False
            report += f"⚠️ Trading stopped automatically due to losses exceeding {config.MAX_LOSS_HOUR}% in the past hour.\n"

    try:
        config.bot.send_message(config.CHAT_ID, report, reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"[Telegram Error] Failed to send trade report: {e}")

def send_daily_report():
    """
    Sends a daily summary report via Telegram bot.
    """
    report = (
        f"📊 Daily Report:\n"
        f"✅ Total Trades: {state.total_trades_today}\n"
        f"✔️ Winning Trades: {state.successful_trades}\n"
        f"❌ Losing Trades: {state.failed_trades}\n"
        f"💰 Total Profit / Loss: {state.total_profit_loss:.2f} USDT\n"
        f"📅 Report Date: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    try:
        config.bot.send_message(config.CHAT_ID, report, reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"[Telegram Error] Failed to send daily report: {e}")

def daily_report_scheduler():
    """
    Runs continuously and sends a daily report at 20:59 local time.
    """
    while True:
        now = time.localtime()
        if now.tm_hour == 20 and now.tm_min == 59:
            send_daily_report()
            time.sleep(65)  # Avoid sending multiple reports in the same minute
        time.sleep(30)
