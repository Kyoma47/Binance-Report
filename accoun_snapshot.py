import datetime
import os 
from binance.client import Client
from dotenv import load_dotenv 

import pandas as pd 

load_dotenv() #read file from local .env


api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

client = Client(api_key, api_secret, testnet=True)

# Fetch latest available account snapshot
snapshots = client.get_account_snapshot(type='SPOT')
#
#print("code :", snapshots['code'])
#print("message :", snapshots['msg'])

print( snapshots ) 
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
    balance_dict['date'] = datetime.datetime.fromtimestamp(date / 1000).strftime('%Y-%m-%d')
    balance_dict['totalAssetOfBtc'] = snapshot['data']['totalAssetOfBtc'] 
    balances.append( balance_dict )
    
# Convert to DataFrame for analysis
df_balances = pd.DataFrame(balances, columns=["date", "totalAssetOfBtc"] + sorted( list(asset_names) ))

# Display the data
print(df_balances)

#exit()

import gspread
from google.oauth2.service_account import Credentials

# Define the scope :
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("gcp-credentials.json", scopes=scopes)

# Authorize the client :
client = gspread.authorize(credentials=credentials)

sheet_url = "https://docs.google.com/spreadsheets/d/1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8/edit?gid=0#gid=0"
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


crypto_df = df_balances

# Convert DataFrame to list of lists (for gspread)
# Add the headers (column names) as the first row in the data list
data = [crypto_df.columns.values.tolist()] + crypto_df.values.tolist()

# Select the worksheet by name
worksheet = spreadsheet.worksheet("Binance.Snapshot")

# Find "date" cell (start of DataFrame in gsheet): 
date_cell = worksheet.find("date")
print(date_cell, date_cell.row, date_cell.col)

# Define the starting row and column
start_row = date_cell.row + 1  # Adjust start_row to the position below "date"
start_col = date_cell.col      # start_col should be the column where "date" is located

# Write the headers into the first row (right after the "date" cell)
header_row = start_row - 1  # Place headers above the data
header_cell_list = worksheet.range(header_row, start_col, header_row, start_col + len(crypto_df.columns) - 1)

# Populate header_cell_list with the column names
for i, cell in enumerate(header_cell_list):
    cell.value = crypto_df.columns[i]

# Update the sheet with the headers
worksheet.update_cells(header_cell_list)
print("Headers updated.")

# Now set the range for the data values
print("crypto_df.shape[0] :", crypto_df.shape[0])
print("crypto_df.shape[1] :", crypto_df.shape[1])
cell_list = worksheet.range(start_row, start_col, start_row + crypto_df.shape[0] - 1, start_col + crypto_df.shape[1] - 1)

# Replace NaN with 0 or any other value
crypto_df = crypto_df.fillna(0)
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


'J-6'