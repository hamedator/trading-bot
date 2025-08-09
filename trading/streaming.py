# trading/streaming_demo.py
from decimal import Decimal
from collections import deque
import time
import threading
import random
import json

# The original project imports (kept for structure). If your repo exposes them,
# they'll be used; otherwise demo fallbacks below will take over.
try:
    import config
except Exception:
    config = None

try:
    import state
except Exception:
    # minimal demo state object to mirror your original state
    class _State:
        candles = {}
        price_history = {}
    state = _State()

# -------------------------
# Demo-safe helpers / fallbacks
# -------------------------
def demo_get_config(attr, default):
    if config and hasattr(config, attr):
        return getattr(config, attr)
    return default

# demo defaults (safe)
MAX_CANDLE_STORE = demo_get_config("MAX_CANDLE_STORE", 500)
REQUIRED_BARS = demo_get_config("REQUIRED_BARS", 300)
STEP_SEC = demo_get_config("STEP_SEC", 60)
MONITOR_MINUTES = demo_get_config("MONITOR_MINUTES", 60)
KLINE_INTERVAL = demo_get_config("KLINE_INTERVAL", "1m")

# -------------------------
# Mock exchange client (no network)
# -------------------------
def mock_get_klines(symbol, interval, limit):
    """
    Return mock klines as Binance-style lists where index 4 is close price.
    Each kline: [open_time, open, high, low, close, ...]
    """
    base_price = 100.0 if "BTC" not in symbol else 20000.0
    klines = []
    for i in range(limit):
        # small random walk
        price = base_price + random.uniform(-5, 5) * (1 + 0.01 * i)
        open_p = price + random.uniform(-1, 1)
        high_p = max(open_p, price) + random.uniform(0, 2)
        low_p = min(open_p, price) - random.uniform(0, 2)
        close_p = round(price, 2)
        k = [int(time.time()) - (limit - i) * STEP_SEC, str(open_p), str(high_p), str(low_p), str(close_p)]
        klines.append(k)
    return klines

# -------------------------
# 1. Bootstrap history (demo)
# -------------------------
def bootstrap_history(symbols, interval=KLINE_INTERVAL, limit=100):
    """
    Demo-safe bootstrap: uses mock_get_klines if real client unavailable.
    Mirrors the original function's behavior but without external API calls.
    """
    for sym in symbols:
        try:
            if config and hasattr(config, "client"):
                # original (real) client call commented out in demo
                # klines = config.client.get_klines(symbol=sym, interval=interval, limit=limit)
                klines = mock_get_klines(sym, interval, limit)
            else:
                klines = mock_get_klines(sym, interval, limit)

            closes = [Decimal(k[4]) for k in klines]
            state.candles[sym] = deque(closes, maxlen=MAX_CANDLE_STORE)

            # price_history (timestamp, price) pairs
            now = time.time()
            start_ts = now - STEP_SEC * (len(closes) - 1)
            state.price_history[sym] = deque(
                [(start_ts + i * STEP_SEC, closes[i]) for i in range(len(closes))],
                maxlen=REQUIRED_BARS
            )

            print(f"[DEMO] Bootstrapped {sym}: {len(closes)} bars")
            time.sleep(0.05)  # small delay
        except Exception as e:
            print(f"[DEMO] Bootstrap error {sym}: {e}")

# -------------------------
# 2. Handle kline message (same logic, safe)
# -------------------------
def handle_kline_message(msg):
    """
    msg expects a dict similar to Binance kline event payload.
    For demo, we only process closed klines (k['x'] == True).
    """
    try:
        # Demo message sanity: ensure kline structure exists
        if not isinstance(msg, dict):
            return

        # support both full 'data' wrapper and raw kline dict for demo
        data = msg.get('data', msg)
        if data.get('e') and data['e'] != 'kline':
            return

        k = data.get('k', data)
        is_closed = k.get('x', True)
        if not is_closed:
            return

        symbol = data.get('s', k.get('s', 'DEMOSYM'))
        close_price = Decimal(str(k.get('c', k.get('close', random.uniform(100, 200)))))

        # initialize candle deque if needed
        if symbol not in state.candles:
            state.candles[symbol] = deque(maxlen=MAX_CANDLE_STORE)
        state.candles[symbol].append(close_price)

        # update price_history
        now = time.time()
        if symbol not in state.price_history:
            state.price_history[symbol] = deque(maxlen=REQUIRED_BARS)
        state.price_history[symbol].append((now, close_price))

        # prune old entries beyond MONITOR_MINUTES
        cutoff = MONITOR_MINUTES * 60
        while state.price_history[symbol] and now - state.price_history[symbol][0][0] > cutoff:
            state.price_history[symbol].popleft()

        print(f"[DEMO] Kline closed for {symbol} -> {close_price}")
    except Exception as e:
        print(f"[DEMO] WebSocket msg error: {e}")

# -------------------------
# 3. Chunking utility (unchanged)
# -------------------------
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# -------------------------
# 4. Demo socket / stream runner (no external WebSocket)
# -------------------------
def start_socket_for_group(symbol_group, simulate_rate_sec=1.0):
    """
    In the real project this opens a WebSocket per group. In demo we spawn
    a thread that generates fake kline messages periodically and calls
    handle_kline_message to mimic incoming data.
    """

    def run_simulator():
        try:
            print(f"[DEMO] Starting simulated socket for group: {symbol_group}")
            while True:
                for sym in symbol_group:
                    # create a demo kline-like payload
                    close_price = round(random.uniform(100, 200), 2)
                    k_payload = {
                        'e': 'kline',
                        's': sym,
                        'k': {
                            't': int(time.time() * 1000),
                            'o': str(close_price + random.uniform(-1, 1)),
                            'h': str(close_price + random.uniform(0, 2)),
                            'l': str(close_price - random.uniform(0, 2)),
                            'c': str(close_price),
                            'x': True  # mark as closed candle
                        }
                    }
                    handle_kline_message(k_payload)
                    time.sleep(simulate_rate_sec)
                # small pause between group cycles
                time.sleep(0.1)
        except Exception as e:
            print(f"[DEMO] Simulator stopped due to: {e}")

    t = threading.Thread(target=run_simulator, daemon=True)
    t.start()
    return t

# -------------------------
# Demo usage helper
# -------------------------
def demo_run_all():
    """
    Example driver to demonstrate bootstrapping and simulated streaming.
    This is safe to run locally and shows how state.candles and price_history
    get populated.
    """
    symbols = ["BTCUSDT_DEMO", "ETHUSDT_DEMO"]
    bootstrap_history(symbols, limit=50)
    # start simulators in 1 or 2 groups
    start_socket_for_group(symbols, simulate_rate_sec=0.5)

    # run demo for a short period and then print a summary
    run_seconds = 5
    print(f"[DEMO] Running streaming demo for {run_seconds} seconds...")
    time.sleep(run_seconds)

    for s in symbols:
        c = state.candles.get(s, [])
        ph = state.price_history.get(s, [])
        print(f"[DEMO] Summary {s}: candles={len(c)}, price_history={len(ph)}")

# Run demo driver when executed directly
if __name__ == "__main__":
    demo_run_all()