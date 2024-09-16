from binance.client import Client
import os 
from dotenv import load_dotenv 
from datetime import datetime
import time 

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

asset_names = list_spot_assets()
print("asset_names :", asset_names)


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


#for asset_name in list_spot_assets() : 
#    print( get_price_on_date(symbol="AAVEUSDT", date="2024-09-01") )
#    break 

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
worksheet = spreadsheet.worksheet("History.Price")


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
    


def read_dates_from_gsheet() : 
    # Get all values from column B
    column_b_values = worksheet.col_values(2)  # Column B is the second column

    # Find "2024-04-19" cell (start of DataFrame in gsheet): 
    halving_date_cell = worksheet.find("2024-04-19")
    row_start_index = halving_date_cell.row
    headers_values = worksheet.row_values( row_start_index )

    for j in range(halving_date_cell.col, len(headers_values) ):
        if headers_values[j] != "" : 
            print(headers_values[j], j)
            col_start_index = j+1
            break 

    print( f"start index : ({row_start_index},{col_start_index})" )
    print( halving_date_cell , halving_date_cell.row, halving_date_cell.col)

    # Define the starting row and column (E8 becomes row 8, column 5)
    start_row = row_start_index # 8
    start_col = col_start_index # 5

    # Prepare the data for insertion
    headers = asset_names # list of str ['AAVE', 'ANKR', ... ]

    # Insert keys starting from E8 (row 8, column 5)
    keys_range = f'{gspread.utils.rowcol_to_a1(start_row, start_col)}:{gspread.utils.rowcol_to_a1(start_row, start_col + len(headers) - 1)}'
    worksheet.update(values=[headers], range_name=keys_range, value_input_option='RAW')


    for i, date_str in enumerate(column_b_values) :
        row_index = i+1

        # Check if the input date is in the past, present, or future
        is_empty_date   = (date_str == "") 
        if is_empty_date : 
            is_past_date, is_current_date, is_future_date, is_halving_date = False, False, False, False
        else :
            input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            current_date = datetime.now().date()
            halving_date = datetime.strptime("2024-04-19", "%Y-%m-%d").date()
            #print("input_date :", input_date)
            #print("current_date :", current_date)
            is_halving_date = halving_date == input_date
            is_past_date    = (input_date  < current_date) 
            is_current_date = (input_date == current_date)
            is_future_date  = (input_date  > current_date)
        
        message = "(empty date)" if is_empty_date else (
            "(past date)" if is_past_date else (
                "(current date)" if is_current_date else "(futur date)" 
            )
        )

        print(row_index, date_str, message, end=" ")
        if (not is_empty_date) and is_past_date and (not is_halving_date) : 
            print( f"=> fetching price for date '{date_str}' " )
            row_values_set = set( worksheet.row_values( row_index )[col_start_index-1:]) 
            #print("\t", row_values_set)
            if row_values_set in [ set(), {'', '0,00'},  {''}, {'0,00'} ]:
                print( "\t line to process :" )
                print( "|".join(asset_names) )
                asset_names
                fill_gsheet_row( row_index, col_start_index,  date_str, asset_names )
            else : 
                print( f"\t Skip line {row_index} already filled : { str(list(row_values_set))[:100] }..." )
                time.sleep(0.8)

        elif is_halving_date : print( f"=> skip halving date '{date_str}' " )
        print()

        if is_current_date or is_future_date : 
            print("Stop iterration on date :", date_str)
            break


    # return column_b_values

#print( "get_price_on_date :" , get_price_on_date( symbol="AAVEUSDT", date="2024-05-01") )
print( read_dates_from_gsheet() )