# trading/orders_demo.py
from decimal import Decimal, ROUND_DOWN
import math
import time
import random

# Keep imports for structure; fall back to demo-friendly objects if missing
try:
    import config
except Exception:
    config = None

try:
    import state
except Exception:
    class _State:
        in_position = False
        current_symbol = None
        last_entry_price = None
        last_entry_amount = None
        usdt_before = Decimal('0.0')
        price_history = {}
        symbols_info_dict = {}
        total_profit_loss = Decimal('0.0')
    state = _State()

# Try to import bot helpers for shape parity (but don't call them in demo)
try:
    from boting.keyboard import get_main_keyboard
except Exception:
    def get_main_keyboard():
        return None

try:
    from boting.reporter import send_trade_report
except Exception:
    def send_trade_report(*args, **kwargs):
        print("[DEMO] send_trade_report called with:", args, kwargs)

# Binance exception placeholder (won't be raised in demo)
try:
    from binance.exceptions import BinanceAPIException
except Exception:
    class BinanceAPIException(Exception):
        pass

# ----------------------
# Mock exchange-layer (demo-safe)
# ----------------------
def mock_get_asset_balance(asset='USDT'):
    # Return mimic of many client libraries: a dict with 'free' as string
    demo_balances = {
        'USDT': '1000.0',
        # for base assets e.g. BTC, ETH we return small balances if requested
        'BTC': '0.0015',
        'ETH': '0.02'
    }
    return {'free': demo_balances.get(asset, '0.0')}

def mock_get_symbol_ticker(symbol='BTCUSDT'):
    # Return string price to mimic client response
    if 'BTC' in symbol:
        price = random.uniform(20000, 40000)
    elif 'ETH' in symbol:
        price = random.uniform(1000, 3000)
    else:
        price = random.uniform(10, 500)
    return {'price': f"{price:.2f}"}

def mock_order_market_buy(symbol, quantity):
    """
    Return a fake order dict resembling Binance order response including 'fills'.
    Each fill contains 'price' and 'qty' as strings.
    """
    # Simulate average executed price around mock ticker price
    price = float(mock_get_symbol_ticker(symbol)['price'])
    fills = []
    remaining = float(quantity)
    # create 1-3 fills
    parts = random.randint(1, 3)
    for i in range(parts):
        part_qty = round(remaining / (parts - i), 6)
        part_price = round(price * (1 + random.uniform(-0.0005, 0.0005)), 8)
        fills.append({'price': str(part_price), 'qty': str(part_qty)})
        remaining -= part_qty
    return {'fills': fills}

def mock_order_market_sell(symbol, quantity):
    # similar structure to buy
    price = float(mock_get_symbol_ticker(symbol)['price'])
    fills = []
    remaining = float(quantity)
    parts = random.randint(1, 3)
    for i in range(parts):
        part_qty = round(remaining / (parts - i), 6)
        part_price = round(price * (1 + random.uniform(-0.0005, 0.0005)), 8)
        fills.append({'price': str(part_price), 'qty': str(part_qty)})
        remaining -= part_qty
    return {'fills': fills}

# ----------------------
# Helper: quantize float qty by step_size (keeps same semantics)
# ----------------------
def adjust_quantity(qty, step_size):
    try:
        precision = abs(int(round(-math.log10(step_size))))
    except Exception:
        precision = 6
    return float(Decimal(str(qty)).quantize(Decimal(f'1e-{precision}'), rounding=ROUND_DOWN))

# ----------------------
# place_market_buy_order (demo)
# ----------------------
def place_market_buy_order(symbol):
    """
    Demo-safe buy: uses mock balance and mock order; no network required.
    Preserves original logic flow but replaces external calls with prints/mocks.
    """
    if getattr(state, "in_position", False) and state.current_symbol == symbol:
        print(f"[DEMO] 🚫 Already in a trade for {symbol}")
        print("[DEMO] Would send bot message: Insufficient USDT balance")
        return

    try:
        # get balance (mock or real if config.client exists)
        if config and hasattr(config, "client"):
            bal = config.client.get_asset_balance(asset='USDT')['free']
        else:
            bal = mock_get_asset_balance('USDT')['free']

        usdt_balance = Decimal(str(bal))
        print(f"[DEMO] USDT balance available: {usdt_balance}")

        if usdt_balance < Decimal('10'):
            print("[DEMO] 🚫 Insufficient USDT balance (demo)")
            return

        notional = (usdt_balance * Decimal('0.999')).quantize(Decimal('0.0001'))
        print(f"[DEMO] Computed notional: {notional}")

        if notional < Decimal('10'):
            print("[DEMO] Notional below exchange minimum (demo)")
            return

        if config and hasattr(config, "client"):
            price = Decimal(config.client.get_symbol_ticker(symbol=symbol)['price'])
        else:
            price = Decimal(str(mock_get_symbol_ticker(symbol)['price']))

        print(f"[DEMO] Market price for {symbol}: {price}")

        qty = (usdt_balance / price)

        if qty >= min_qty:
            print(f"[DEMO] Calculated quantity: {qty} (meets min {min_qty})")
            # place mock order
            if config and hasattr(config, "client"):
                order = config.client.order_market_buy(symbol=symbol, quantity=float(qty))
            else:
                order = mock_order_market_buy(symbol, float(qty))

            state.in_position = True
            state.current_symbol = symbol

            fills = order.get('fills', [])
            if fills:
                total_cost = sum(Decimal(f['price']) * Decimal(f['qty']) for f in fills)
                total_qty = sum(Decimal(f['qty']) for f in fills)
                state.last_entry_price = Decimal(str(avg_price))
                state.last_entry_amount = Decimal(str(total_qty))
                state.usdt_before = Decimal(str(usdt_balance))
                print(f"[DEMO] 📌 New Buy Trade (demo): {symbol} | entry={avg_price} | qty={total_qty}")
                # mimic sending bot message
                print(f"[DEMO] Would send bot message: New Buy Trade for {symbol}")
                return None
            else:
                print(f"[DEMO] ⚠️ No fills returned by mock order for {symbol}")
        else:
            print("[DEMO] Quantity too small for buy order (demo)")
            return None

    except BinanceAPIException as e:
        print(f"[DEMO] ❌ BinanceAPIException in buy: {e}")
        return None
    except Exception as e:
        print(f"[DEMO] ❌ Unexpected error in buy order (demo): {e}")
        return None

# ----------------------
# place_market_sell_order (demo)
# ----------------------
def place_market_sell_order(symbol):
    """
    Demo-safe sell: uses mock balances and mock orders. Resets position without real market activity.
    """
    try:
        base_asset = symbol.replace('USDT', '')
        if config and hasattr(config, "client"):
            bal = config.client.get_asset_balance(asset=base_asset)['free']
        else:
            bal = mock_get_asset_balance(base_asset)['free']

        balance = Decimal(str(bal))
        if balance <= 0:
            print(f"[DEMO] ⚠️ Balance is zero or less for {base_asset} (demo)")
            return

        adjusted_balance = (balance * Decimal('0.999')).quantize(Decimal(f'1e-{precision}'), rounding=ROUND_DOWN)
        qty = adjusted_balance
        if qty < min_qty:
            print(f"[DEMO] ❌ Quantity ({qty}) < min ({min_qty}) for {symbol} (demo)")
            state.in_position = False
            state.current_symbol = None
            return
        else:
            print(f"[DEMO] Placing mock sell for {symbol}, qty={qty}")
            if config and hasattr(config, "client"):
                order = config.client.order_market_sell(symbol=symbol, quantity=float(qty))
            else:
                order = mock_order_market_sell(symbol, float(qty))

            # simulate short delay
            time.sleep(0.5)
            state.in_position = False
            state.current_symbol = None

            fills = order.get('fills', [])
            if fills:
                total_cost = sum(Decimal(f['price']) * Decimal(f['qty']) for f in fills)
                # mock usdt after
                if config and hasattr(config, "client"):
                    usdt_after = Decimal(config.client.get_asset_balance(asset='USDT')['free'])
                else:
                    usdt_after = Decimal(mock_get_asset_balance('USDT')['free'])

                state.last_exit_price = avg_price
                amount_dec = Decimal(str(state.last_entry_amount)) if state.last_entry_amount else Decimal('0')
                entry_price_dec = Decimal(str(state.last_entry_price)) if state.last_entry_price else Decimal('0')
                exit_price_dec = avg_price

                profit_or_loss = ((exit_price_dec - entry_price_dec) / entry_price_dec * 100) if entry_price_dec > 0 else Decimal('0')
                usd_profit_loss = usdt_after - state.usdt_before if hasattr(state, 'usdt_before') else Decimal('0')
                state.total_profit_loss = getattr(state, 'total_profit_loss', Decimal('0')) + usd_profit_loss

                trade_status = "success" if exit_price_dec > entry_price_dec else "failure"
                print(f"[DEMO] 🔻 Sell executed (demo) {symbol} avg_exit={avg_price} profit_usd={usd_profit_loss}")
                # send trade report (demo stub)
                send_trade_report(symbol, amount_dec, entry_price_dec, exit_price_dec, usdt_after, trade_status)
                # small delay similar to original
                time.sleep(0.5)
                return None
            else:
                print(f"[DEMO] ⚠️ No fills data from mock sell for {symbol}")

    except BinanceAPIException as e:
        print(f"[DEMO] ❌ Binance API Error (demo): {e}")
        state.in_position = False
        state.current_symbol = None
        return
    except Exception as e:
        print(f"[DEMO] ❌ Error in sell order (demo): {e}")
        state.in_position = False
        state.current_symbol = None
        return

# ----------------------
# check_balance (demo)
# ----------------------
def check_balance():
    """
    Returns a float balance for USDT. In demo reads from mock_get_asset_balance.
    """
    try:
        if config and hasattr(config, "client"):
            bal = float(config.client.get_asset_balance(asset='USDT')['free'])
        else:
            bal = float(mock_get_asset_balance('USDT')['free'])
        print(f"[DEMO] check_balance -> {bal}")
        return bal
    except Exception as e:
        print(f"[DEMO] ❌ Unable to retrieve balance: {e}")
        return 0.0

# ----------------------
# current_balance (demo)
# ----------------------
def current_balance():
    """
    Compute a human-readable report of the current open trade (demo). Returns string or None.
    """
    try:
        if not getattr(state, "in_position", False) or not getattr(state, "current_symbol", None):
            print("[DEMO] 🚫 No active trade at the moment.")
            return None

        if config and hasattr(config, "client"):
            current_price = Decimal(config.client.get_symbol_ticker(symbol=state.current_symbol)['price'])
        else:
            current_price = Decimal(str(mock_get_symbol_ticker(state.current_symbol)['price']))

        current_amount = Decimal(str(state.last_entry_amount)) if state.last_entry_amount else Decimal('0')
        profit_or_loss = ((current_price - state.last_entry_price) / state.last_entry_price * 100) if state.last_entry_price else Decimal('0')
        usd_profit_loss = current_value - (state.usdt_before if hasattr(state, 'usdt_before') else Decimal('0'))

        report = (
            f"⚡️ Current Trade (DEMO)\n"
            f"🔹 Symbol: {state.current_symbol}\n"
            f"💸 Entry Price: {state.last_entry_price}\n"
            f"💰 Current Price: {current_price}\n"
            f"📈 Current Balance: {current_value} USDT\n"
            f"📈 Current P/L (%): {profit_or_loss:.2f}%\n"
            f"💵 Current Profit: {usd_profit_loss:.2f} USDT\n"
        )
        print(f"[DEMO] Current value for {state.current_symbol}: {current_value} USDT")
        return report
    except Exception as e:
        print(f"[DEMO] ❌ Error while calculating current value (demo): {e}")
        return None

# If run as script, demonstrate buy -> current -> sell flow (safe)
if __name__ == "__main__":
    # prepare demo symbol info
    state.symbols_info_dict['BTCUSDT'] = {'quantity_precision': 6, 'price_precision': 2, 'min_qty': '0.000001', 'step_size': 0.000001}
    print("[DEMO] Running small demo sequence: BUY -> CURRENT -> SELL")
    place_market_buy_order('BTCUSDT')
    time.sleep(0.5)
    print(current_balance())
    time.sleep(0.5)
    place_market_sell_order('BTCUSDT')