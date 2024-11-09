from binance.client import Client
from datetime import datetime, timedelta

def get_amount_on_date(symbol, date):
    # Initialize the Binance client
    client = Client(
        "4MfT0dG3hwRU9NQYUiL7KdZHAAoMR8wlX3kP2g1VE2lOOXb44dnaVzfwvdJfn2cg", # your_api_key
        "XhdwhZ4lxI4zA80cOrZZymf0rsNs9MlOJu1bHT8qkxV8P9G6aEf3GrMczZTaWQ0i", # your_api_secret
    )
    
    # Convert the date string to a datetime object
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    # Set the end time to the end of the target date
    end_time = target_date + timedelta(days=1) - timedelta(seconds=1)
    
    # Get the account trades up to the target date
    trades = client.get_my_trades(symbol=symbol, endTime=int(end_time.timestamp() * 1000))
    
    # Calculate the total amount based on trades
    total_amount = 0
    for trade in trades:
        if trade['isBuyer']:
            total_amount += float(trade['qty'])
        else:
            total_amount -= float(trade['qty'])
    
    return total_amount

# Usage
print("get_amount_on_date:", get_amount_on_date(symbol="AAVEUSDT", date="2024-05-01"))