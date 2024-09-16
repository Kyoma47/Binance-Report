import gspread
from google.oauth2.service_account import Credentials

# Define the scope :
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Provide the path to your service account key file :
credentials = Credentials.from_service_account_file("gcp-credentials.json", scopes=scopes)

# Authorize the client :
client = gspread.authorize(credentials=credentials)


# sheet_url = "https://docs.google.com/spreadsheets/d/1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8/edit?gid=0#gid=0" # Crypto 3
sheet_url = "https://docs.google.com/spreadsheets/d/13qBnldQcoPsPLIinNIlhnkHj45wYzCu-J_J5iPsWBBs/edit?gid=680550515#gid=680550515" # Crypto 2
sheet_id = sheet_url.split("/")[5] #"1p83ovDFyHYboZBZ0K_9jPdnF1Fri6vvUjWtkEatllS8"
print("sheet_id :", sheet_id)

# Attempt to open the spreadsheet by key
spreadsheet = client.open_by_key(sheet_id)

# Select the worksheet by name
worksheet = spreadsheet.worksheet("History.Amount")

# Get all values from column B
column_b_values = worksheet.col_values(2)  # Column B is the second column

# Find "date" cell (start of DataFrame in gsheet): 
date_cell = worksheet.find("date")
print(column_b_values)


from binance.client import Client
import pandas as pd

import os 
from dotenv import load_dotenv 

# Specify the path to the .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')

# Load the .env file
load_dotenv(dotenv_path)
#load_dotenv() #read file from local .env

# Initialize the Binance client
api_key = os.environ["BINANCE_API_KEY"]
api_secret = os.environ["BINANCE_SERCET_KEY"]

client = Client(api_key, api_secret)

# Get historical account snapshot (savings, spot, or margin)
def get_account_snapshot(date, type="spot"):
    # Date format: yyyy-mm-dd
    snapshot = client.get_account_snapshot(type=type, startTime=date)
    return snapshot


print( get_account_snapshot("2024-06-09") )