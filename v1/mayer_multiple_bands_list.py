import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def get_mayer_multiple_bands(symbol, start_date, end_date):
    crypto = yf.Ticker(symbol)
    df = crypto.history(start=start_date, end=end_date)
    
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Mayer_Multiple'] = df['Close'] / df['MA200']
    
    bands = [0.5, 1, 1.5, 2, 2.5]
    for band in bands:
        df[f'Band_{band}'] = df['MA200'] * band
    
    return df

def get_multiple_crypto_bands(crypto_list, start_date, end_date):
    all_data = {}
    
    for symbol in crypto_list:
        try:
            df = get_mayer_multiple_bands(symbol, start_date, end_date)
            all_data[symbol] = df[['Close', 'MA200', 'Mayer_Multiple', 'Band_0.5', 'Band_1', 'Band_1.5', 'Band_2', 'Band_2.5']]
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {symbol}: {e}")
    
    return all_data

# Liste des crypto-monnaies
crypto_list = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD']

# Dates
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')  # 2 ans de données

# Récupération des données
crypto_data = get_multiple_crypto_bands(crypto_list, start_date, end_date)

# Affichage des résultats
for symbol, df in crypto_data.items():
    print(f"\nDernières valeurs pour {symbol}:")
    print(df.tail())

# Option pour sauvegarder les données dans des fichiers CSV
save_to_csv = input("Voulez-vous sauvegarder les données dans des fichiers CSV? (oui/non): ").lower() == 'oui'

if save_to_csv:
    for symbol, df in crypto_data.items():
        filename = f"{symbol.replace('-', '_')}_mayer_bands.csv"
        df.to_csv(filename)
        print(f"Données sauvegardées dans {filename}")