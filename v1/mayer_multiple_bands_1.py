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
    
    result = {
        'Date': yesterday_data.name.date(),
        'Close': yesterday_data['Close'],
        'MA200': yesterday_data['MA200'],
        'Mayer_Multiple': yesterday_data['Mayer_Multiple'],
    }
    
    for band in bands:
        result[f'Band_{band}'] = yesterday_data[f'Band_{band}']
    
    return result, len(df)

def get_multiple_crypto_yesterday_data(crypto_list):
    all_data = {}
    
    for symbol in crypto_list:
        try:
            data, days_available = get_yesterday_mayer_multiple(symbol)
            if data:
                all_data[symbol] = data
                all_data[symbol]['Days_Available'] = days_available
                if days_available < 200:
                    print(f"Attention: {symbol} n'a que {days_available} jours de données disponibles.")
            else:
                print(f"Pas de données disponibles pour {symbol}")
                all_data[symbol] = {
                    'Date': None,
                    'Close': None,
                    'MA200': None,
                    'Mayer_Multiple': None,
                    'Band_0.5': None,
                    'Band_1': None,
                    'Band_1.5': None,
                    'Band_2': None,
                    'Band_2.5': None,
                    'Days_Available': 0
                }
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {symbol}: {e}")
            all_data[symbol] = {
                'Date': None,
                'Close': None,
                'MA200': None,
                'Mayer_Multiple': None,
                'Band_0.5': None,
                'Band_1': None,
                'Band_1.5': None,
                'Band_2': None,
                'Band_2.5': None,
                'Days_Available': 0
            }
    
    return all_data

# Liste des crypto-monnaies
crypto_list = [
    "AAVE", "ANKR", "BNB", "BONK", "BTC", "CKB", "DOGE", "DOT", "DUSK", 
    "ETH", "FET", "FLOKI", "GLM", 
    "INJ", "JASMY", "JUP", "LINK", "LPT", 
    "NEAR", "OM", "OP", "ORDI", "PENDLE", "PEPE", "POL", "PYTH", 
    "RENDER", "SHIB", "SOL", "STRAX", "STX", "TAO", "TON", "TRU", 
    "UNI", "VET",
]
crypto_list = [crypto + '-USD' for crypto in crypto_list]

# Récupération des données
crypto_data = get_multiple_crypto_yesterday_data(crypto_list)

# Création d'un DataFrame avec les résultats
results_df = pd.DataFrame.from_dict(crypto_data, orient='index')
results_df.index.name = 'Symbol'

# Affichage des résultats
print(results_df)

# Option pour sauvegarder les données dans un fichier CSV
save_to_csv = input("Voulez-vous sauvegarder les données dans un fichier CSV? (oui/non): ").lower() == 'oui'
if save_to_csv:
    filename = "crypto_mayer_bands_yesterday.csv"
    results_df.to_csv(filename)
    print(f"Données sauvegardées dans {filename}")