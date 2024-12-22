import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def get_yesterday_mayer_multiple(symbol):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=201)  # 201 jours pour assurer une MA200 valide
    
    crypto = yf.Ticker(symbol)
    df = crypto.history(start=start_date, end=end_date)
    
    if df.empty:
        return None

    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Mayer_Multiple'] = df['Close'] / df['MA200']
    
    bands = [0.5, 1, 1.5, 2, 2.5]
    for band in bands:
        df[f'Band_{band}'] = df['MA200'] * band
    
    yesterday_data = df.iloc[-1]  # -1 pour obtenir les données d'hier
    
    return {
        'Date': str( yesterday_data.name.date() ),
        'Close':  yesterday_data['Close'] ,
        'MA200':  yesterday_data['MA200'] ,
        'Mayer_Multiple':  yesterday_data['Mayer_Multiple'] ,
        'Band_0.5':  yesterday_data['Band_0.5'] ,
        'Band_1':  yesterday_data['Band_1'] ,
        'Band_1.5':  yesterday_data['Band_1.5'] ,
        'Band_2':  yesterday_data['Band_2'] ,
        'Band_2.5':  yesterday_data['Band_2.5'],
    }

def get_multiple_crypto_yesterday_data(crypto_list):
    all_data = {}
    
    for symbol in crypto_list:
        try:
            data = get_yesterday_mayer_multiple(symbol)
            if data:
                all_data[symbol] = data
            else:
                print(f"Pas de données disponibles pour {symbol}")
                all_data[symbol] ={
                    'Date': None,
                    'Close': None,
                    'MA200': None,
                    'Mayer_Multiple': None,
                    'Band_0.5': None,
                    'Band_1': None,
                    'Band_1.5': None,
                    'Band_2': None,
                    'Band_2.5': None,
                }
         
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {symbol}: {e}")
    
    return all_data

# Liste des crypto-monnaies
crypto_list = [
	"AAVE", "ANKR", "BNB", "BONK", "BTC", 
    #"CKB", "DOGE", 
    "DOT", "DUSK", 
	"ETH", "FET", "FLOKI", "GLM", 
	"INJ", "JASMY", "JUP", "LINK", "LPT", 
	"NEAR", 
    "OM", 
    "OP", 
    #"ORDI", 
    "PENDLE", "PEPE", "POL", "PYTH", 
	"RENDER", "SHIB", "SOL", 
    #"STRAX", 
    "STX", "TAO", "TON", "TRU", 
	"UNI", "VET",
]
crypto_list = [ crypto +'-USD' for crypto in crypto_list ] # ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD']

# Récupération des données
crypto_data = get_multiple_crypto_yesterday_data(crypto_list)

# Création d'un DataFrame avec les résultats
results_df = pd.DataFrame.from_dict(crypto_data, orient='index')
results_df.index.name = 'Symbol'

# Affichage des résultats
print(results_df)

# Option pour sauvegarder les données dans un fichier CSV
'''
save_to_csv = input("Voulez-vous sauvegarder les données dans un fichier CSV? (oui/non): ").lower() == 'oui'
if save_to_csv:
    filename = "crypto_mayer_bands_yesterday.csv"
    results_df.to_csv(filename)
    print(f"Données sauvegardées dans {filename}")
'''



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

# Ouvrir la Google Sheet
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


# DataFrame à écrire
crypto_df = results_df

# Ajouter l'index comme colonne dans le DataFrame
crypto_df.reset_index(inplace=True)  # 'Symbol' devient une colonne

# Remplacer les valeurs NaN par des chaînes vides ou 0
crypto_df = crypto_df.fillna("")  # Remplace NaN par des chaînes vides (vous pouvez utiliser 0 si nécessaire)

# Convertir le DataFrame en liste de listes (incluant l'index en colonne)
df_list = [crypto_df.columns.tolist()] + crypto_df.reset_index().values.tolist()

# Obtenir la position initiale (C5 correspond à la position [4, 2] car les index commencent à 0)
row_start = 4  # C5 correspond à la ligne 5
col_start = 2  # C correspond à la 3ème colonne

# Select the worksheet by name
worksheet = spreadsheet.worksheet("Mayer")

# Find "Crypto" cell (start of Dataframe in gsheet): 
date_cell = worksheet.find("Crypto")
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
