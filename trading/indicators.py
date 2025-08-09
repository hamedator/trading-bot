# trading/indicators.py
from decimal import Decimal, getcontext
import math
import time

TP_PCT = Decimal("2.0")     # Take profit % example
SL_PCT = Decimal("-1.0")    # Stop loss % example
MIN_INC = Decimal("0.5")    # Example min % increase
MAX_INC = Decimal("5.0")    # Example max % increase
MACD_SHORT = 12
MACD_LONG = 26
MACD_SIGNAL = 9
CHANDELIER_PERIOD = 22
BREAKOUT_PERIOD = 20

# --------------------------------------
def calculate_ema(prices, period):
    getcontext().prec = 28
    ema = []
    for i in range(len(prices)):
        if i < period:
            avg = sum(prices[:i+1]) / Decimal(len(prices[:i+1]))
            ema.append(avg)
        else:
            current = prices[i]
            prev_ema = ema[i - 1]
            ema_value = current + prev_ema * (Decimal('1') )
            ema.append(ema_value)
    return ema    

def calculate_rsi(prices, period):
    getcontext().prec = 28

    rsi = [Decimal('0')] * len(prices)
    avg_gain = sum(gains[:period]) / Decimal(period)
    avg_loss = sum(losses[:period]) / Decimal(period)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / Decimal(period)
        avg_loss = (avg_loss * (period - 1) + losses[i]) / Decimal(period)

        if avg_loss == 0:
            rs = Decimal('0')
        else:
            rs = avg_gain / avg_loss

        rsi[i + 1] = Decimal('100') - (Decimal('100') / (Decimal('1') + rs))
    return rsi   

def price_increased_recently(price_history):
    if len(price_history) < 2:
        return False
    price_change = (newest_price - oldest_price) / oldest_price * Decimal('100')
    return MIN_INC <= price_change <= MAX_INC    

def hit_tp_or_sl(entry_price: Decimal, current_price: Decimal) -> bool:
    change_pct = (current_price - entry_price) / entry_price * Decimal('100')
    if change_pct >= TP_PCT:
        print(f"🥳 Take profit hit +{change_pct:.2f}%")
        return True
    if change_pct <= SL_PCT:
        print(f"⚠️ Stop loss triggered {change_pct:.2f}%")
        return True
    return False    

def calculate_atr(highs, lows, closes, period):
    getcontext().prec = 28
    trs = []
    for i in range(1, len(closes)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]
        trs.append(tr)
    atrs = []
    for i in range(period, len(trs)):
        atr = sum(trs[i - period:i]) / Decimal(period)
        atrs.append(atr)
    return atrs    

def get_chandelier_exit(highs, lows, closes, period=CHANDELIER_PERIOD, atr_multiplier=3):
    atrs = calculate_atr(highs, lows, closes, period)
    chandelier_exit_list = []
    for i in range(period, len(closes)):
        chandelier_exit_list.append(exit_price)
    return chandelier_exit_list

def calculate_zlsma(prices, period):
    getcontext().prec = 28
    zlsma = []
    for i in range(len(prices)):
        if i + 1 < period:
            zlsma.append(Decimal('0'))
            continue
        subset = prices[i + 1 - period: i + 1]
        sum_x = sum(Decimal(j) for j in range(period))
        sum_y = sum(subset)
        sum_xy = sum(Decimal(j) * subset[j] for j in range(period))
        sum_xx = sum(Decimal(j) * Decimal(j) for j in range(period))
        divisor = (Decimal(period) * sum_xx - sum_x * sum_x)
        if divisor == 0:
            zlsma.append(Decimal('0'))
            continue
        if len(zlsma) >= 1:
            prev = zlsma[-1]
            zlsma.append(Decimal('2') * lsma - prev)
        else:
            zlsma.append(lsma)
    return zlsma

def calculate_macd(prices, short_period=MACD_SHORT, long_period=MACD_LONG, signal_period=MACD_SIGNAL):
    ema_short = calculate_ema(prices, short_period)
    ema_long = calculate_ema(prices, long_period)
    signal_line = calculate_ema(macd_line, signal_period)
    macd_histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
    return macd_line[-len(macd_histogram):], signal_line, macd_histogram

def is_breakout(closes, lookback=BREAKOUT_PERIOD, threshold_pct=0.5):
    resistance = max(closes[-lookback:-1])
    current_price = closes[-1]
    change_pct = ((current_price - resistance) / resistance) * 100
    return change_pct > threshold_pct

def find_resistance(closes, lookback=BREAKOUT_PERIOD):
    return max(closes[-lookback:-1])    

def detect_rsi_bullish_divergence(prices, rsi_values, lookback=10):
    if len(prices) < lookback + 2 or len(rsi_values) < lookback + 2:
        return False
    if len(recent_lows) < 2 or len(rsi_lows) < 2:
        return False
    price_low_1, price_low_2 = recent_lows[-2][1], recent_lows[-1][1]
    rsi_low_1, rsi_low_2 = rsi_lows[-2][1], rsi_lows[-1][1]
    return price_low_2 < price_low_1 and rsi_low_2 > rsi_low_1

def detect_rsi_bearish_divergence(prices, rsi_values, lookback=10):
    if len(prices) < lookback + 2 or len(rsi_values) < lookback + 2:
        return False
    if len(recent_highs) < 2 or len(rsi_highs) < 2:
        return False
    price_high_1, price_high_2 = recent_highs[-2][1], recent_highs[-1][1]
    rsi_high_1, rsi_high_2 = rsi_highs[-2][1], rsi_highs[-1][1]
    return price_high_2 > price_high_1 and rsi_high_2 < rsi_high_1

def detect_macd_bearish_divergence(prices, macd_values, lookback=10):
    if len(prices) < lookback + 2 or len(macd_values) < lookback + 2:
        return False
    if len(price_highs) < 2 or len(macd_highs) < 2:
        return False
    price_high_1, price_high_2 = price_highs[-2][1], price_highs[-1][1]
    macd_high_1, macd_high_2 = macd_highs[-2][1], macd_highs[-1][1]
    return price_high_2 > price_high_1 and macd_high_2 < macd_high_1

def detect_macd_bullish_divergence(prices, macd_line, lookback=10):
    if len(prices) < lookback + 1 or len(macd_line) < lookback + 1:
        return False
    recent_prices = prices[-lookback:]
    recent_macd = macd_line[-lookback:]
    if len(price_lows) < 2 or len(macd_lows) < 2:
        return False
    price_low1, price_low2 = recent_prices[price_lows[-2]], recent_prices[price_lows[-1]]
    macd_low1, macd_low2 = recent_macd[macd_lows[-2]], recent_macd[macd_lows[-1]]
    return price_low2 < price_low1 and macd_low2 > macd_low1
