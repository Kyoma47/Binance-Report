from binance.client import Client
import os 
from dotenv import load_dotenv 
from datetime import datetime
import time 
import pandas as pd 

# Specify the path to the .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# Load the .env file
load_dotenv(dotenv_path)
#load_dotenv() #read file from local .env

# Initialize the Binance client
api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

binance_client = Client(api_key, api_secret)


def list_spot_assets() :
    # Fetch account balances
    account = binance_client.get_account()
    balances = account['balances']
    L = [ e["asset"] for e in balances if float( e["free"] )]
    L = sorted( L , key=str.casefold )
    return L

L = list_spot_assets()
print("L :", L)
print()


def get_price_on_date(symbol, date): 
    start_str, end_str = f"{date} 00:00:00" , f"{date} 23:59:59"
    start_ts = int(datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    end_ts = int(datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

    # Fetch kline data (interval 1 day)
    klines = binance_client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_ts, end_ts)
    
    if klines:
        # Return the closing price of the day
        return float(klines[0][4])  # Closing price is at index 4
    else:
        return None

def get_balance_df () :
    # Fetch latest available account snapshot
    snapshots = binance_client.get_account_snapshot(type='SPOT')
    #
    #print("code :", snapshots['code'])
    #print("message :", snapshots['msg'])

    # print( snapshots ) 
    
    #balances = snapshots['snapshotVos']
    #for balance in balances : 
    #    print(balance)
    balances = []
    asset_names = set()

    for snapshot in snapshots['snapshotVos']:
        date = snapshot['updateTime']
        balance_info = snapshot['data']['balances']
        asset_names = asset_names.union( set( [coin_balance['asset'] for coin_balance in balance_info] ) )

        balance_dict = { coin_balance['asset'] : coin_balance['free'] for coin_balance in balance_info }
        balance_dict['date'] = datetime.fromtimestamp(date / 1000).strftime('%Y-%m-%d')
        balance_dict['totalAssetOfBtc'] = snapshot['data']['totalAssetOfBtc'] 
        balance_dict = { k: str(balance_dict[k]).replace('.', ',')  for k in balance_dict }
        balances.append( balance_dict )
        
    # Convert to DataFrame for analysis
    columns = sorted( list(asset_names) )
    df_balances = pd.DataFrame(balances, columns= columns + ["date", "totalAssetOfBtc"] )

    
    L1, L2 = L, list(columns)
    print("current assets :" , L1 )
    print("df columns :" , L2 )
    print()
    
    # Trouver les éléments dans L2 mais pas dans L1
    difference = list(set(L2) - set(L1))
    print("Hiding removed coins :", difference )
    for name in difference :
        print("-> Removing", name )
        df_balances.pop( name )

    # Display the data
    print(df_balances)
    return df_balances


crypto_amount_df = get_balance_df()
oldest_date = crypto_amount_df['date'][0]
print("Oldest date :", oldest_date)

import gspread
from google.oauth2.service_account import Credentials

# Define the scope :
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("../gcp-credentials.json", scopes=scopes)

# Authorize the client :
gspread_client = gspread.authorize(credentials=credentials)

sheet_url = "https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=680550515#gid=680550515" # Crypto 2
sheet_id = sheet_url.split("/")[5] #"1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8"
print("sheet_id :", sheet_id)

# Attempt to open the spreadsheet by key
spreadsheet = gspread_client.open_by_key(sheet_id)

# Select the worksheet by name
worksheet = spreadsheet.worksheet("History.Amount")

# Find "2024-04-19" cell (start of DataFrame in gsheet): 
halving_date_cell = worksheet.find("2024-04-19")
row_start_index = halving_date_cell.row
headers_values = worksheet.row_values( row_start_index )

for j in range(halving_date_cell.col, len(headers_values) ):
    if headers_values[j] == crypto_amount_df.columns[0] : 
        print(headers_values[j], j)
        col_start_index = j+1
        break 

# Define the starting row and column
date_column = worksheet.col_values( halving_date_cell.col ) 
start_row =  date_column.index( oldest_date ) +1 
start_col =  col_start_index
print( f"start indexes : ( {start_row} , {start_col})" )

# Convert DataFrame to list of lists (for gspread)
# Add the headers (column names) as the first row in the data list
data = [crypto_amount_df.columns.values.tolist()] + crypto_amount_df.values.tolist()

# Now set the range for the data values
print("crypto_df.shape[0] :", crypto_amount_df.shape[0])
print("crypto_df.shape[1] :", crypto_amount_df.shape[1])
cell_list = worksheet.range(start_row, start_col, start_row + crypto_amount_df.shape[0] - 1, start_col + crypto_amount_df.shape[1] - 1)

# Replace NaN with 0 or any other value
crypto_df = crypto_amount_df.fillna(0)
print(crypto_df)

# Flatten the DataFrame to a list (for updating the data cells)
flat_df = crypto_df.values.flatten()

# Populate cell_list with the DataFrame values
print("populating cells ...")
for i, cell in enumerate(cell_list):
    cell.value = flat_df[i]

# Update the Google Sheet with the data
print("Updating worksheet cells ...")
worksheet.update_cells(cell_list)

print("Done: program complete.")

exit()
########################################################################################################################
import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials

# Define the scope :
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("../gcp-credentials.json", scopes=scopes)

# Authorize the client :
gspread_client = gspread.authorize(credentials=credentials)

sheet_url = "https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=680550515#gid=680550515" # Crypto 2
sheet_id = sheet_url.split("/")[5] #"1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8"
print("sheet_id :", sheet_id)

# Attempt to open the spreadsheet by key
spreadsheet = gspread_client.open_by_key(sheet_id)

# Select the worksheet by name
worksheet = spreadsheet.worksheet("History.Amount")

# Find "2024-04-19" cell (start of DataFrame in gsheet): 
halving_date_cell = worksheet.find("2024-04-19")
row_start_index = halving_date_cell.row
headers_values = worksheet.row_values( row_start_index )

for j in range(halving_date_cell.col, len(headers_values) ):
    if headers_values[j] == df.columns[2] : 
        print(headers_values[j], j)
        col_start_index = j+1
        break 

print( f"start index : ({row_start_index},{col_start_index})" )
print( halving_date_cell , halving_date_cell.row, halving_date_cell.col)

exit() 

def fill_gsheet_row( row_index, col_index, date_str, asset_names ):
    row_dict = {}
    for asset_name in asset_names :
        if asset_name == 'USDT' : price_at_date = 1
        else :  
            symbol = (asset_name + "USDT")
            print( f"\t get_price_on_date( symbol='{symbol}', date='{date_str}') ")
            price_at_date = get_price_on_date(symbol=symbol, date=date_str) 

        # Retreived price by binance API :    
        print(f"\t {asset_name.ljust(6)} ({ type(price_at_date) }) : {price_at_date}" )
        
        # Converting Scientific Notation to Regular Float (values like 3.312e-05)
        price_at_date = f'{price_at_date:.8f}' if isinstance(price_at_date, float) else price_at_date
        print(f"\t {asset_name.ljust(6)} ({ type(price_at_date) }) : {price_at_date}" )

        # Add value to row dict :
        row_dict[asset_name] = price_at_date
        print()
    print(row_dict)

    # Define the starting cell (E8)
    row = row_index
    col = col_index  # E is the 5th column

    print()
    print("Inserting row at :", (row, col) )

    # Prepare the data for insertion :
    # values = list(row_dict.values()) # List without headers order.
    values = [str(row_dict.get(key, '')) for key in asset_names]  # Use empty string if key not in data
    values = [str(value) if value is not None else '' for value in row_dict.values()]
    values = [ v.replace('.', ',') for v in values ] # Converting '83.67000000' to gsheet french format '83,67000000'

    # Insert values starting from E8 (row 8, column 5)
    print("values :", values) 
    values_range = f'{rowcol_to_a1(row, col)}:{rowcol_to_a1(row, col + len(values) - 1)}'
    print("values_range =>", values_range )
    worksheet.update(values=[values], range_name=values_range, value_input_option='RAW')

    print("Data inserted successfully.")
    return row_dict
    
#print( "get_price_on_date :" , get_price_on_date( symbol="AAVEUSDT", date="2024-05-01") )
print( "get_price_on_date :" , get_amount_on_date( symbol="AAVEUSDT", date="2024-05-01") )
