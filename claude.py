import os
from binance.client import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd

#
from datetime import datetime, timedelta
import pytz
import time

from dotenv import load_dotenv 
load_dotenv() #read file from local .env

# Binance API credentials
api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

# Google Sheets API credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'gcp-credentials.json'

def get_binance_data():
    client = Client(api_key, api_secret)
    account = client.get_account()
    balances = account['balances']
    
    # Filter out zero balances
    non_zero_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
    
    # Get current prices and average costs
    portfolio = []
    for balance in non_zero_balances:
        asset = balance['asset']
        free = float(balance['free'])
        locked = float(balance['locked'])
        total = free + locked
        
        # Get current price (assuming USDT market)
        try:
            ticker = client.get_symbol_ticker(symbol=f"{asset}USDT")
            current_price = float(ticker['price'])
        except:
            current_price = 0  # Set to 0 if price not available
        
        # Get average cost
        try:
            trades = client.get_my_trades(symbol=f"{asset}USDT")
            total_cost = sum(float(trade['price']) * float(trade['qty']) for trade in trades)
            total_quantity = sum(float(trade['qty']) for trade in trades)
            avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
        except:
            avg_cost = 0  # Set to 0 if average cost not available
        
        portfolio.append({
            'Asset': asset,
            'Free': free,
            'Locked': locked,
            'Total': total,
            'Current Price': current_price,
            'Average Cost': avg_cost,
            'Total Value (USDT)': total * current_price,
            'Profit/Loss': (current_price - avg_cost) * total if avg_cost > 0 else 0
        })
    
    df = pd.DataFrame(portfolio)
    
    # Format numeric columns
    numeric_columns = ['Free', 'Locked', 'Total', 'Current Price', 'Average Cost', 'Total Value (USDT)', 'Profit/Loss']
    for col in numeric_columns:
        df[col] = df[col].apply(lambda x: f'{x:.8f}')
    
    return df

def update_google_sheet(df):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    
    # Specify your Google Sheet ID and range
    SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
    RANGE_NAME = 'Sheet1!A1'
    
    # Convert DataFrame to list of lists for Google Sheets
    values = [df.columns.tolist()] + df.values.tolist()
    
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    
    print(f"{result.get('updatedCells')} cells updated.")

def main():
    df = get_binance_data()
    
    # Set display options for pandas
    pd.set_option('display.float_format', lambda x: f'{x:.8f}')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    print(df)  # Display DataFrame in console
    update_google_sheet(df)

def get_wallet_history(start_date):
    client = Client(api_key, api_secret)
    
    end_date = datetime.now(pytz.UTC).date()
    current_date = start_date.date()
    
    wallet_history = {}
    assets = set()

    while current_date <= end_date:
        wallet_history[current_date] = {}
        
        # Get list of all assets
        account_info = client.get_account()
        all_assets = [balance['asset'] for balance in account_info['balances']]
        print("all_assets :", all_assets)

        # Filter out zero balances
        balances = client.get_account()['balances']
        non_zero_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
        print("Non Zero balance :", non_zero_balances)

        non_empty_assets = [ b["asset"] for b in non_zero_balances ]

        for asset in non_empty_assets :
            print(asset, end=" ")
            try:
                balance = client.get_asset_balance(asset=asset)
                total = float(balance['free']) + float(balance['locked'])
                
                if total > 0:
                    wallet_history[current_date][asset] = total
                    assets.add(asset)
            except Exception as e:
                print(f"Error fetching balance for {asset} on {current_date}: {e}")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(0.1)
        
        print(f"Processed date: {current_date}")
        current_date += timedelta(days=1)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(wallet_history, orient='index')
    
    # Ensure all assets are included in the DataFrame
    for asset in assets:
        if asset not in df.columns:
            df[asset] = 0
    
    # Fill NaN values with 0
    df = df.fillna(0)
    
    # Sort columns alphabetically
    df = df.sort_index().sort_index(axis=1)
    
    return df

def main():
    # Set start date to June 6, 2023
    # start_date = datetime(2023, 6, 6, tzinfo=pytz.UTC)
    start_date = datetime(2024, 6, 6, tzinfo=pytz.UTC)

    df = get_wallet_history(start_date)
    
    # Set display options
    pd.set_option('display.float_format', lambda x: f'{x:.8f}')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    print(df)

    # Optionally, save to CSV
    df.to_csv('binance_wallet_history.csv')


def get_historical_price(client, symbol, date):
    # Convert date to milliseconds
    timestamp = int(date.timestamp() * 1000)
    
    # Get daily kline (candlestick) data
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, startTime=timestamp, limit=1)
    
    if klines:
        # Return the closing price
        return float(klines[0][4])
    else:
        return None

def get_wallet_history_with_prices(start_date):
    client = Client(api_key, api_secret)
    
    end_date = datetime.now(pytz.UTC).date()
    current_date = start_date.date()
    
    wallet_history = {}
    assets = set()

    while current_date <= end_date:
        wallet_history[current_date] = {}
        
        # Get list of all assets
        account_info = client.get_account()
        all_assets = [balance['asset'] for balance in account_info['balances']]

        # Filter out zero balances
        # balances = client.get_account()['balances']
        # non_zero_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
        # print("Non Zero balance :", non_zero_balances)
        
        for asset in all_assets:
            print(asset, end=" ")
            try:
                balance = client.get_asset_balance(asset=asset)
                total = float(balance['free']) + float(balance['locked'])
                
                if total > 0:
                    wallet_history[current_date][f'{asset}_balance'] = total
                    assets.add(asset)
                    
                    # Get historical price
                    if asset != 'USDT':  # Assume USDT price is always 1
                        price = get_historical_price(client, f'{asset}USDT', datetime.combine(current_date, datetime.min.time(), tzinfo=pytz.UTC))
                        if price:
                            wallet_history[current_date][f'{asset}_price'] = price
                    else:
                        wallet_history[current_date][f'{asset}_price'] = 1.0
                    
            except Exception as e:
                print(f"Error fetching data for {asset} on {current_date}: {e}")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(0.1)
        
        print(f"Processed date: {current_date}")
        current_date += timedelta(days=1)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(wallet_history, orient='index')
    
    # Ensure all assets are included in the DataFrame
    for asset in assets:
        if f'{asset}_balance' not in df.columns:
            df[f'{asset}_balance'] = 0
        if f'{asset}_price' not in df.columns:
            df[f'{asset}_price'] = None
    
    # Fill NaN values with 0 for balances and forward fill for prices
    balance_columns = [col for col in df.columns if col.endswith('_balance')]
    price_columns = [col for col in df.columns if col.endswith('_price')]
    df[balance_columns] = df[balance_columns].fillna(0)
    df[price_columns] = df[price_columns].fillna(method='ffill')
    
    # Sort columns
    df = df.sort_index().sort_index(axis=1)
    
    return df

def main():
    # Set start date to June 6, 2023
    #start_date = datetime(2023, 6, 6, tzinfo=pytz.UTC)
    start_date = datetime(2024, 9, 7, tzinfo=pytz.UTC)
    
    df = get_wallet_history_with_prices(start_date)
    
    # Set display options
    pd.set_option('display.float_format', lambda x: f'{x:.8f}')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    print(df)

    # Optionally, save to CSV
    df.to_csv('binance_wallet_history_with_prices.csv')

if __name__ == '__main__':
    main()
