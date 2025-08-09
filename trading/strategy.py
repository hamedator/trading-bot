# trading/strategy_demo.py
from decimal import Decimal
import time
import random

# note: we still import config/state/indicators to keep structure similar.
# For demo purposes, missing attributes fall back to safe defaults.
try:
    import config
except Exception:
    config = None

try:
    import state
except Exception:
    # Minimal demo state object
    class _State:
        candles = {}
        is_trading_active = False
        in_position = False
        current_symbol = None
        last_entry_price = None
        usdt_before = None
        symbols_info_dict = {}
    state = _State()

# Import indicator function names (assumed present). In demo they will be stubbed if missing.
def _safe_import(name):
    try:
        module = __import__("trading.indicators", fromlist=[name])
        return getattr(module, name)
    except Exception:
        return None

calculate_ema = _safe_import("calculate_ema")
calculate_rsi = _safe_import("calculate_rsi")
price_increased_recently = _safe_import("price_increased_recently")
hit_tp_or_sl = _safe_import("hit_tp_or_sl")
calculate_macd = _safe_import("calculate_macd")
calculate_zlsma = _safe_import("calculate_zlsma")
get_chandelier_exit = _safe_import("get_chandelier_exit")
find_resistance = _safe_import("find_resistance")
detect_rsi_bullish_divergence = _safe_import("detect_rsi_bullish_divergence")
detect_rsi_bearish_divergence = _safe_import("detect_rsi_bearish_divergence")
detect_macd_bearish_divergence = _safe_import("detect_macd_bearish_divergence")
detect_macd_bullish_divergence = _safe_import("detect_macd_bullish_divergence")
is_breakout = _safe_import("is_breakout")
calculate_atr = _safe_import("calculate_atr")

# Placeholder for symbols util
try:
    from utils.symbols import get_symbols
except Exception:
    def get_symbols():
        # demo: return a small list of two symbols with precisions
        return [
            {"symbol": "BTCUSDT", "price_precision": 2, "quantity_precision": 6, "eps": 1e-6},
            {"symbol": "ETHUSDT", "price_precision": 2, "quantity_precision": 5, "eps": 1e-6},
        ]

# Placeholder keyboard/get_main_keyboard just for structural parity
try:
    from boting.keyboard import get_main_keyboard
except Exception:
    def get_main_keyboard():
        return None

# ----------------------
# Demo helper fallbacks
# ----------------------
def demo_get_config(attr, default):
    if config and hasattr(config, attr):
        return getattr(config, attr)
    return default

# Safe demo defaults (used when config is absent)
TRADE_INTERVAL = demo_get_config("TRADE_INTERVAL", 5)  # seconds in demo
EMA_SHORT = demo_get_config("EMA_SHORT", 12)
EMA_LONG = demo_get_config("EMA_LONG", 26)
RSI_PERIOD = demo_get_config("RSI_PERIOD", 14)
ZLSAMA_PERIOD = demo_get_config("ZLSAMA_PERIOD", 21)
LOOK_BACK = demo_get_config("LOOK_BACK", 10)
RSI_OVERSELL = demo_get_config("RSI_OVERSELL", 30)
RSI_OVERBOUGHT = demo_get_config("RSI_OVERBOUGHT", 70)

# Feature flags (demo: keep structure but safe defaults)
USE_BULLISH_CROSS = demo_get_config("USE_BULLISH_CROSS", True)
USE_BELOW_BEFORE = demo_get_config("USE_BELOW_BEFORE", False)
USE_RSI_CRITICAL = demo_get_config("USE_RSI_CRITICAL", False)
USE_PRICE_INCREASES_RECENTLY = demo_get_config("USE_PRICE_INCREASES_RECENTLY", False)
USE_EMA_SLOPE = demo_get_config("USE_EMA_SLOPE", False)
USE_PRICE_ABOVE_ZLSMA = demo_get_config("USE_PRICE_ABOVE_ZLSMA", False)
USE_MACD_BULLISH = demo_get_config("USE_MACD_BULLISH", False)
USE_BREAKOUT_CROSS = demo_get_config("USE_BREAKOUT_CROSS", False)
USE_RSI_BULLISH_DIVERGENCE = demo_get_config("USE_RSI_BULLISH_DIVERGENCE", False)
USE_MACD_BULLISH_DIVERGENCE = demo_get_config("USE_MACD_BULLISH_DIVERGENCE", False)
USE_TPORSL_CROSS = demo_get_config("USE_TPORSL_CROSS", True)
USE_CHANDELIER_CROSS = demo_get_config("USE_CHANDELIER_CROSS", False)
USE_MACD_BEARISH = demo_get_config("USE_MACD_BEARISH", False)
USE_PRICE_BELOW_ZLSMA = demo_get_config("USE_PRICE_BELOW_ZLSMA", False)

# ----------------------
# Mock exchange helpers (no network)
# ----------------------
def mock_get_asset_balance(asset='USDT'):
    # returns a dict-like with free balance as string to mimic client libs
    return {'free': '1000.0'}

def mock_get_symbol_ticker(symbol='BTCUSDT'):
    # return price as string
    price = random.uniform(100.0, 60000.0) if "BTC" in symbol else random.uniform(10.0, 4000.0)
    return {'price': f"{price:.2f}"}

# ----------------------
# Strategy loop (demo-safe)
# ----------------------
def strategy_loop():
    try:
        symbols_info = get_symbols()
        state.symbols_info_dict = {s['symbol']: s for s in symbols_info}

        # Prepare simple mock candles in state if empty
        for s in symbols_info:
            sym = s['symbol']
            if sym not in state.candles or len(state.candles[sym]) < EMA_LONG:
                # create mock OHLC close prices as floats
                mock_closes = [round(random.uniform(100, 200), 2) for _ in range(EMA_LONG + 5)]
                # store as list of numbers or dicts depending on other code expectations
                state.candles[sym] = mock_closes

        # Activate trading in demo so the loop proceeds once
        state.is_trading_active = True

        while True:
            print(f"SYMBOLS: {len(symbols_info)}")
            # accept both list-of-floats or list-of-candle-dicts
            candle_counts = sum(len(state.candles[s['symbol']]) for s in symbols_info)
            print(f"CANDLES (total across symbols): {candle_counts}")

            if not state.is_trading_active:
                print("⛔ Trading stopped")
                time.sleep(TRADE_INTERVAL)
                continue

            valid_symbols = [
                s for s in symbols_info
                if s['symbol'] in state.candles and len(state.candles[s['symbol']]) >= max(EMA_LONG, RSI_PERIOD)
            ]

            if not valid_symbols:
                print("No symbols to check...")
                time.sleep(TRADE_INTERVAL)
                continue

            print(f'\n[{time.strftime("%H:%M:%S")}] Checking {len(valid_symbols)} symbols...')

            for s in valid_symbols:
                symbol = s['symbol']

                # obtain closes (ensure numeric list)
                closes = state.candles[symbol]
                if not closes:
                    continue
                # If closes are dicts with 'close' key, extract
                if isinstance(closes[0], dict):
                    closes = [float(c.get('close', 0)) for c in closes]

                # Use stubbed indicator outputs if indicator functions missing
                if calculate_macd:
                    macd_line, signal_line, macd_hist = calculate_macd(closes)
                else:
                    # create mock arrays aligned with len(closes)
                    macd_line = [0.0] * len(closes)
                    signal_line = [0.0] * len(closes)
                    macd_hist = [0.0] * len(closes)

                if calculate_zlsma:
                    zlsma_list = calculate_zlsma(closes, period=ZLSAMA_PERIOD)
                else:
                    zlsma_list = [sum(closes)/len(closes)] * len(closes)

                if calculate_ema:
                    ema_short = calculate_ema(closes, EMA_SHORT)
                    ema_long = calculate_ema(closes, EMA_LONG)
                else:
                    ema_short = [sum(closes)/len(closes)] * len(closes)
                    ema_long = [sum(closes)/len(closes)] * len(closes)

                ema_slope = ema_long[-1] > ema_long[-4] if len(ema_long) >= 4 else False

                if calculate_rsi:
                    rsi = calculate_rsi(closes, RSI_PERIOD)
                else:
                    rsi = [50.0] * len(closes)

                macd_bullish_divergence = detect_macd_bullish_divergence(closes, macd_line) if detect_macd_bullish_divergence else False
                has_rsi_bullish_divergence = detect_rsi_bullish_divergence(closes, rsi) if detect_rsi_bullish_divergence else False
                has_rsi_bearish_divergence = detect_rsi_bearish_divergence(closes, rsi) if detect_rsi_bearish_divergence else False
                macd_bearish_divergence = detect_macd_bearish_divergence(closes, macd_line) if detect_macd_bearish_divergence else False
                macd_bullish = prev_macd <= prev_signal and curr_macd > curr_signal
                macd_bearish = prev_macd >= prev_signal and curr_macd < curr_signal

                # ---------- ENTRY ----------
                if not state.in_position:
                    if len(ema_short) < LOOK_BACK + 2:
                        continue
                    prev_short = ema_short[-(LOOK_BACK + 2):-2]
                    prev_long = ema_long[-(LOOK_BACK + 2):-2]
                    short_below_long_before = all(sv < lv for sv, lv in zip(prev_short, prev_long))
                    price_above_zlsma = closes[-1] > zlsma_list[-1]
                    rsi_critical = RSI_OVERSELL <= rsi[-1] <= RSI_OVERBOUGHT
                    buy_reasons = []
                    buy_conditions = []

                    # Keep conditions in place, but in demo only a subset is required
                    if USE_BULLISH_CROSS:
                        buy_conditions.append(bullish_cross)
                        if bullish_cross:
                            buy_reasons.append("📈 Bullish Cross")

                    if USE_BELOW_BEFORE:
                        buy_conditions.append(short_below_long_before)
                        if short_below_long_before:
                            buy_reasons.append("🔻 Short Below Long Before")

                    if USE_RSI_CRITICAL:
                        buy_conditions.append(rsi_critical)
                        if rsi_critical:
                            buy_reasons.append(f"💡 RSI Critical ({rsi[-1]:.2f})")

                    # demo price increase check uses stub or fallback
                    if USE_PRICE_INCREASES_RECENTLY and price_increased_recently:
                        value = price_increased_recently(symbol)
                        buy_conditions.append(value)
                        if value:
                            buy_reasons.append("📊 Price Increased Recently")

                    if USE_EMA_SLOPE:
                        buy_conditions.append(ema_slope)
                        if ema_slope:
                            buy_reasons.append("📐 EMA Slope Positive")

                    # Final decision in demo: require only that at least one active condition is True
                    if buy_conditions and any(buy_conditions):
                        message = f"✅ Demo Buy Signal for {symbol}\nReasons:\n" + "\n".join(buy_reasons)
                        # demo: print instead of sending to a bot
                        print("[DEMO MESSAGE]", message)

                        print(f"✅ [DEMO] Buy signal detected for {symbol} | RSI = {rsi[-1]:.2f}")
                        # demo: record mock entry state but DO NOT execute real order
                        state.in_position = True
                        state.current_symbol = symbol
                        state.last_entry_price = Decimal(closes[-1])
                        state.usdt_before = Decimal(mock_get_asset_balance(asset='USDT')['free'])
                        print(f"[DEMO] Would place market buy order for {symbol} at {closes[-1]}")
                        # break to simulate single trade handling like original code
                        break

                # ---------- EXIT ----------
                elif state.in_position and symbol == state.current_symbol:
                    print(f"🕒 [DEMO] Still in position: {state.current_symbol}...")
                    live_price = Decimal(mock_get_symbol_ticker(symbol=symbol)['price'])
                    tporsl_cross = False
                    if hit_tp_or_sl:
                        try:
                            tporsl_cross = hit_tp_or_sl(state.last_entry_price, live_price)
                        except Exception:
                            tporsl_cross = False

                    price_below_zlsma = closes[-1] < zlsma_list[-1]
                    chandelier_cross = False
                    if len(closes) > 30 and get_chandelier_exit:
                        chandelier_exit_list = get_chandelier_exit([], [], closes)
                    sell_reasons = []
                    con_tpsl = USE_TPORSL_CROSS and tporsl_cross
                    if con_tpsl:
                        sell_reasons.append("🎯 Take Profit / Stop Loss Cross")

                    cond_chandelier = USE_CHANDELIER_CROSS and chandelier_cross
                    cond_macd = USE_MACD_BEARISH and macd_bearish
                    cond_zlsma = USE_PRICE_BELOW_ZLSMA and price_below_zlsma

                    if cond_chandelier and cond_macd and cond_zlsma:
                        if cond_chandelier:
                            sell_reasons.append("💡 Chandelier Exit")
                        if cond_macd:
                            sell_reasons.append("📉 MACD Bearish")
                        if cond_zlsma:
                            sell_reasons.append("⬇️ Price Below ZLSMA")

                    # demo exit: if tp/sl triggered or all three exit flags active
                    if con_tpsl or (cond_chandelier and cond_macd and cond_zlsma):
                        message = f"🔻 Demo Sell Signal for {symbol}\nReasons:\n" + "\n".join(sell_reasons)
                        print("[DEMO MESSAGE]", message)

                        print(f"🔻 [DEMO] Confirmed sell signal for {symbol}")
                        # demo: reset position (no real sell)
                        state.in_position = False
                        state.current_symbol = None
                        state.last_entry_price = None
                        print(f"[DEMO] Would place market sell order for {symbol} at {closes[-1]}")
                        break

            # In demo we run once-through or sleep briefly and then exit loop to avoid infinite background in examples
            time.sleep(TRADE_INTERVAL)
            # For demo purposes, break after one full iteration to avoid infinite demo loop
            print("[DEMO] One iteration complete — stopping demo loop.")
            break

    except Exception as e:
        print(f"❌ Error in strategy loop (demo): {e}")

# -------------------
def start_trading():
    if getattr(state, "is_trading_active", False):
        print("⚠️ Trading is already active! (demo)")
        return

    state.is_trading_active = True
    print("🔔 [DEMO] Starting trading now...")

# ------    
def stop_trading():
    if getattr(state, "in_position", False) and getattr(state, "current_symbol", None):
        state.is_trading_active = False
        # in demo we simply reset
        print(f"[DEMO] Closing position for {state.current_symbol} (demo, no real order).")
        state.in_position = False
        state.current_symbol = None
    else:
        print("🚫 No open trades currently. (demo)")