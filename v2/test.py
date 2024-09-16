import pandas as pd 

orders_csv_file = "544931cc-6fc7-11ef-9a3b-0e3291b69067-1.csv"
convert_xlsx_file = "Export Order History-2024-09-10 23_57_42.xlsx"

# Date                    2024-06-24 13:57:37
# Wallet                          Spot Wallet
# Pair                                IOTABTC
# Type                                Instant
# Sell                                39 IOTA
# Buy                          0.00010809 BTC
# Price            1 IOTA = 0.00000277157 BTC
# Inverse Price         1 BTC = 360806.3 IOTA
# Date Updated            2024-06-24 13:57:38
# Status                           Successful

class Asset :
    def __init__(self):
        pass 

class Order : 
    def __init__(self, csv_row ):
        pass 

class Convert : 
    pass 

# Read the Excel file
# You can specify a particular sheet with sheet_name="Sheet1"
df = pd.read_excel(convert_xlsx_file, sheet_name=None)  # sheet_name=None loads all sheets
print(df)

# If you have multiple sheets and want to loop through them
for sheet_name, sheet_data in df.items():
    print(f"Sheet name: {sheet_name}")
    # Iterate over rows in the current sheet
    for index, row in sheet_data.iterrows():
        print(row)  # Do your processing here


