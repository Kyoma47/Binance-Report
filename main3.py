import gspread
# from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
import json

# Define the scope :
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("gcp-credentials.json", scopes=scopes)

# Authorize the client :
client = gspread.authorize(credentials=credentials)

# https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=520047181#gid=520047181
#sheet_id = "13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs"

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


# Select the worksheet by name
worksheet = spreadsheet.worksheet("Table")

# Find "Crypto ID" cell : 
crypto_id_cell = worksheet.find("Crypto ID")
print(crypto_id_cell, crypto_id_cell.row, crypto_id_cell.col)

# Get all values in column :
crypto_ids = worksheet.col_values(crypto_id_cell.col)[crypto_id_cell.row:]  

# Print the values
print(crypto_ids)



def get_current_usdt_price(currency):
  # Define the API endpoint
  api_endpoint = "https://api.kucoin.com/api/v1/market/stats?symbol={}-USDT".format(currency)
  
  # data = {
  # "code":"200000",
  # "data":{
  #  "time":1719005648624,
  #  "symbol":"TAO-USDT",
  #  "buy":"285.13",
  #  "sell":"285.4",
  #  "changeRate":"-0.0532",
  #  "changePrice":"-16.05",
  #  "high":"301.97",
  #  "low":"282.11",
  #  "vol":"4530.1893",
  #  "volValue":"1322177.811894",
  #  "last":"285.09",
  #  "averagePrice":"295.5437731",
  #  "takerFeeRate":"0.001",
  #  "makerFeeRate":"0.001",
  #  "takerCoefficient":"2",
  #  "makerCoefficient":"2"
  # }
  #}
  try:
      response = requests.get(api_endpoint) # Make a GET request to the API endpoint
      response.raise_for_status() # Raise an exception if the request was unsuccessful
      data = response.json() # Parse the JSON response
      row = data['data']
      
      date_time = pd.to_datetime(row['time'], unit='ms') # Convert to datetime 
      date_str, time_str = str(date_time).split(" ")
      row['date'] = date_str
      row['time'] = time_str[:5]
      return row
  
  except requests.exceptions.RequestException as e: print("An error occurred: {}".format(e))
  except json.JSONDecodeError: print("Failed to parse JSON response")



def make_dataframe(currency_ids) : 
   # Append each currency data to the DataFrame
    df_rows = []
    for currency_id in currency_ids:
        df_rows.append( get_current_usdt_price(currency=currency_id) )  
    
    # Initialize an empty DataFrame with the required columns
    df = pd.DataFrame(df_rows, columns=[
        "date", "time", "symbol", "buy", "sell", "changeRate", "changePrice",
        "high", "low", "vol", "volValue", "last", "averagePrice",
        "takerFeeRate", "makerFeeRate", "takerCoefficient", "makerCoefficient"
    ])
    print( df )
    return df 


crypto_df = make_dataframe(crypto_ids)
# Convert DataFrame to list of lists (for gspread)
data = [crypto_df.columns.values.tolist()] + crypto_df.values.tolist()

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
for i, cell in enumerate(cell_list):
    cell.value = flat_df[i]

# Update the Google Sheet with the new values
worksheet.update_cells(cell_list)