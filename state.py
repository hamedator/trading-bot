from collections import defaultdict, deque
from decimal import Decimal

# ========== Trading states ==========
is_trading_active = False  # Flag to indicate if trading is currently active
in_position = False        # Flag to indicate if currently holding a trade position
current_symbol = None      # Symbol currently being traded

# ========== Entry and exit data ==========
last_entry_price = Decimal("0.00")   # Last trade entry price
last_exit_price = Decimal("0.00")    # Last trade exit price
last_entry_amount = Decimal("0.00")  # Last trade entry quantity
last_usdt_amount = Decimal("0.00")   # USDT amount related to last trade

# ========== Profit and loss tracking ==========
total_profit_loss = Decimal('0')     # Total P/L across trades
usdt_before = 0.0                    # USDT balance before trade
balance = 0.0                       # Current account balance (USDT)
successful_trades = 0               # Count of successful trades
failed_trades = 0                   # Count of failed trades
total_trades_today = 0              # Total trades done today
recent_losses = deque()             # Recent loss amounts for tracking

# ========== Price data ==========
oldest_price = None                 # Oldest price in tracked history
newest_price = None                 # Most recent price in tracked history
price_change = None                # Calculated price change percentage

# ========== Market data storage ==========
symbols_info_dict = {}              # Dictionary storing info about trading symbols
candles = defaultdict(lambda: deque(maxlen=120))  # Candle close prices per symbol, maxlen adjustable
price_history = {}                 # Price history tuples (timestamp, price) per symbol
