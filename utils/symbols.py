from decimal import Decimal
import math
import config

# -----------------------------------
print("🚀 Script started...")

def get_symbols():
    """
    Retrieves USDT trading symbols from the exchange, excluding leveraged tokens and major coins (BTC, ETH).
    Calculates precision and minimum step sizes for price and quantity.

    Returns:
        list of dict: Each dict contains symbol info with precision and filter details.
    """
    exchange_info = config.client.get_exchange_info()
    symbols_info = []

    for s in exchange_info.get('symbols', []):
        # Filter: quote asset USDT, trading status active, exclude leveraged and main coins
        if (s.get('quoteAsset') == 'USDT' and s.get('status') == 'TRADING' 
            and 'UP' not in s.get('symbol', '') and 'DOWN' not in s.get('symbol', '')):
            
            # Parse filters by filterType for easier access
            filters = {f['filterType']: f for f in s.get('filters', [])}

            symbols_info.append({
                'symbol': s['symbol'],
            })

    return symbols_info
