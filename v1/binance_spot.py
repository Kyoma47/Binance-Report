import pandas as pd 
from dotenv import load_dotenv 

import os 
# Specify the path to the .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# load_dotenv() #read file from local .env
# Load the .env file
load_dotenv(dotenv_path)


from binance.client import Client
from datetime import datetime


api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

def simple_python_example() :
    client = Client(api_key, api_secret, testnet=True)
    # For US users : 
    # client = Client(api_key, api_secret, tld='us')
    tickers = client.get_all_tickers() 
    df = pd.DataFrame( tickers )
    df.head()
    print("tickers :", df )  


def make_spot_df () :
    # print( "api_key :", api_key )
    # print( "api_secret :", api_secret )
    client = Client(api_key, api_secret, testnet=False)
    
    # Fetch account balances
    account = client.get_account()
    balances = account['balances']
    L = [ e for e in balances if float( e["free"] )]

    asset_names = []
    for e in L : 
        symbol = e["asset"]
        pair_symbol = symbol + 'USDT'
        asset_names.append( symbol )
        # print(client.get_asset_balance(asset=symbol))
        if e["asset"] != "USDT" :
            tricker = client.get_symbol_ticker(symbol=pair_symbol)
            e.update( tricker )   
        else :
            e.update( {'symbol': 'N/A', 'price': 1} )

        
        # Get current date and time
        e["date"] = datetime.now().strftime("%Y-%m-%d")
        e["time"] = datetime.now().strftime("%H:%M:%S")
        print( e )

    # Initialize an empty DataFrame with the required columns
    df_table = pd.DataFrame(L, columns=[
        "date", "time", "asset", "free", "locked", "symbol", "price" 
    ])
    df_table_sorted = df_table.sort_values(by=['asset'])
    return df_table_sorted 

crypto_df = make_spot_df ()
print(crypto_df)


import gspread
# from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
import pandas as pd


# Define the scope :
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("../gcp-credentials.json", scopes=scopes)

# Authorize the client :
client = gspread.authorize(credentials=credentials)

# Crypto 2 gsheet : 
sheet_url = "https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=286369727#gid=286369727"
sheet_id = sheet_url.split("/")[5] #"1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8"
print("sheet_id :", sheet_id)

# Open the spreadsheet by key :
try:
    # Attempt to open the spreadsheet by key
    spreadsheet = client.open_by_key(sheet_id)
    # Add your logic to work with the spreadsheet
    print("Spreadsheet opened successfully!")
except gspread.exceptions.APIError as e:
    if "403" in str(e):
        print("APIError: Permission denied. Please check your credentials and access permissions.")
    else:
        print(f"An API error occurred: {e}")
except PermissionError:
    print("PermissionError: You do not have permission to access this spreadsheet.")
    print("Please provide 'editor' access to this email :", credentials.service_account_email)
    print("for this googlesheet :", sheet_url)
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")



# Convert DataFrame to list of lists (for gspread)
data = [crypto_df.columns.values.tolist()] + crypto_df.values.tolist()

# Select the worksheet by name
worksheet = spreadsheet.worksheet("Binance.Spot")

# Find "date" cell (start of Dataframe in gsheet): 
date_cell = worksheet.find("date")
print(date_cell, date_cell.row, date_cell.col)

# Define the starting row and column
start_row = date_cell.row + 1  # start_row = 5
start_col = date_cell.col      # start_col = 11  

# Set the cell range where the DataFrame will be inserted
print("crypto_df.shape[0] :", crypto_df.shape[0])
print("crypto_df.shape[1] :", crypto_df.shape[1])
cell_list = worksheet.range(start_row, start_col, start_row + crypto_df.shape[0] - 1, start_col + crypto_df.shape[1] - 1)

# Flatten the DataFrame to a list
flat_df = crypto_df.values.flatten()

# Populate cell_list with the DataFrame values
print("populating cells ...")
for i, cell in enumerate(cell_list):
    cell.value = flat_df[i]

# Update the Google Sheet with the new values
print("Updating worksheet cells ...")
worksheet.update_cells(cell_list)

print("Done : program complete.")
