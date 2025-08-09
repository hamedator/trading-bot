from dotenv import load_dotenv
import os
from decimal import Decimal

load_dotenv()  # Load sensitive info from .env file (not included in repo)

# ---- Sensitive credentials should only be stored in .env, NOT hardcoded here ----
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))  # Chat ID should be integer

# Binance client and Telegram bot instances should be created in runtime code, not here
# client = Client(API_KEY, API_SECRET)
# bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ======= Technical indicators settings =======
LOOK_BACK = 5
RSI_PERIOD = 10
RSI_OVERBOUGHT = 75
RSI_OVERSOLD = 25
REQUIRED_BARS = 100
MAX_CANDLE_STORE = 120
ZLSAMA_PERIOD = 30
CHANDELIER_PERIOD = 22
MACD_SIGNAL = 9
MACD_SHORT = 12
MACD_LONG = 26
EMA_SHORT = 8
EMA_LONG = 30  # Changed to int for consistency
BREAKOUT_PERIOD = 20
LSTM_MODEL = True
CNN_MODEL = True
XGBOOST_MODEL = True
TRANSFORMER_MODEL = True

# ======= Trading strategy conditions =======
MIN_INCREASE = 7
MAX_INCREASE = 12
MIN_INC = Decimal(str(MIN_INCREASE))
MAX_INC = Decimal(str(MAX_INCREASE))

TAKE_PROFIT_PCT = 1       # Exit at 1% profit
STOP_LOSS_PCT = -3        # Exit at 3% loss
TP_PCT = Decimal(str(TAKE_PROFIT_PCT))
SL_PCT = Decimal(str(STOP_LOSS_PCT))

MONITOR_MINUTES = 1440
TRADE_INTERVAL = 6  # seconds between each check
STEP_SEC = 900      # duration of each candle in seconds (15 minutes)

SYMBOLS_PER_SOCKET = 40
KLINE_INTERVAL = '15m'

# ======= Account settings =======
MIN_USDT = 10
MAX_USDT = 10000
MAX_LOSS_HOUR = 10

# --- Buy conditions ---
USE_BELOW_BEFORE = True
USE_PRICE_INCREASES_RECENTLY = True
USE_EMA_SLOPE = True
USE_RSI_CRITICAL = True
USE_BULLISH_CROSS = True
USE_MACD_BULLISH = True
USE_PRICE_ABOVE_ZLSMA = True
USE_BREAKOUT_CROSS = True

# Disabled buy conditions
USE_RSI_BULLISH_DIVERGENCE = False
USE_MACD_BULLISH_DIVERGENCE = False

# --- Sell conditions ---
USE_TPORSL_CROSS = True
USE_CHANDELIER_CROSS = True
USE_MACD_BEARISH = True
USE_PRICE_BELOW_ZLSMA = True

# Disabled sell conditions
USE_HISTOGRAM_WEAKNESS = False
USE_BEARISH_CROSS = False
USE_RSI_BEARISH_DIVERGENCE = False
USE_MACD_BEARISH_DIVERGENCE = False
USE_BREAKOUT_FAILED = False

MAX_TRADE_USDT = 5000
MIN_TRADE_USDT = 11
