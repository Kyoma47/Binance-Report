import os 
from binance.client import Client
from dotenv import load_dotenv 
load_dotenv() #read file from local .env



api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

symbol = "DOT"

client = Client(api_key, api_secret)

# Specify the trading pair symbol, e.g., 'DOT' for Polkadot
symbol = 'DOT'

# Define trading pairs for the specific coin (e.g., 'DOTUSDT', 'DOTBTC', etc.)
trading_pairs = [f'{symbol}USDT', f'{symbol}BTC', f'{symbol}ETH', f'{symbol}BNB']

total_cost_usd = 0
total_quantity = 0

for pair in trading_pairs:
    try:
        trades = client.get_my_trades(symbol=pair)
        for trade in trades:
            qty = float(trade['qty'])
            price = float(trade['price'])
            quote_asset = pair.replace(symbol, '')

            if quote_asset == 'USDT':
                trade_cost_usd = price * qty
            else:
                # Convert non-USDT trades to USD
                conversion_pair = f'{quote_asset}USDT'
                trade_time = trade['time']
                historical_rate = client.get_historical_klines(conversion_pair, Client.KLINE_INTERVAL_1DAY, trade_time, trade_time)[0]
                conversion_rate = float(historical_rate[4])  # Closing price on the day of the trade
                trade_cost_usd = price * qty * conversion_rate

            total_cost_usd += trade_cost_usd
            total_quantity += qty

    except Exception as e:
        print(f"Error fetching trades for {pair}: {e}")

print(f"Total USD spent on {symbol}: ${total_cost_usd:.2f}")
print(f"Total {symbol} bought: {total_quantity:.6f}")