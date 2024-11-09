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
xlsx_dict = pd.read_excel(convert_xlsx_file, sheet_name=None)  # sheet_name=None loads all sheets

asset_names = ['AAVE', 'ANKR', 'BNB', 'BONK', 'BTC', 'CKB', 'DOGE', 'DOT', 'DUSK', 'ETH', 'FET', 'FLOKI', 'GLM', 'INJ', 'JASMY', 'JUP', 'LINK', 'LPT', 'NEAR', 'OM', 'OP', 'ORDI', 'PENDLE', 'PEPE', 'POL', 'PYTH', 'RENDER', 'SHIB', 'SOL', 'STRAX', 'STX', 'TAO', 'TRU', 'UNI', 'USDT', 'VET']
asset_amount = [0.30620156, 2558.74753862, 0.00001025, 1088251.2, 0.00270077, 3748.34949718, 226.6708859, 8.36434171, 149.79839056, 0.07922216, 49.56149688, 179128.65, 116.1617816, 2.64362674, 7293.20012563, 23.08730232, 6.84456521, 4.97647473, 19.46141792, 31.88929632, 28.6736192, 1.193083, 21.07505291, 12669777.61, 131.39294866, 103.52223832, 11.2736089, 1194671.72, 0.31688397, 0.3, 51.26805358, 0.23508436, 524.71596398, 13.32333563, 18.96, 1071.3606161] 

# Create a dictionary from the two lists
expected_dict = dict(zip(asset_names, asset_amount))

asset_buy_dict = { name:[] for name in asset_names }
asset_sell_dict = { name:[] for name in asset_names }


# If you have multiple sheets and want to loop through them
for sheet_name, sheet_data in xlsx_dict.items():
    print(f"Sheet name: {sheet_name}")
    # Iterate over rows in the current sheet
    for index, row in sheet_data.iterrows():
        # Do your processing here
        for asset_name in asset_names :
            if asset_name in row['Buy'] and asset_name!="USDT": asset_buy_dict[asset_name].append( row )
            if asset_name in row['Sell'] and asset_name!="USDT": asset_sell_dict[asset_name].append( row )
    break

for asset_name in asset_names[1:] : 
    print(asset_name)
    bought = 0 
    for row in asset_buy_dict[asset_name][::-1] : 
        print( row['Date'], row['Buy'], "#", row['Sell'] ) 
        bought += float(row['Buy'].split(" ")[0])
    print("Bought :", bought)
    selled = 0 
    for row in asset_sell_dict[asset_name][::-1] : 
        print( row['Date'], row['Buy'], "#", row['Sell'] )
        selled -= float(row['Sell'].split(" ")[0]) 
    print("Selled :", selled)
    total = bought - selled 
    print(" =>", asset_name , "Total :", bought - selled ) 
    print(" -> expected :", expected_dict[asset_name] )
    print(" error :", total - expected_dict[asset_name])
    print()

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