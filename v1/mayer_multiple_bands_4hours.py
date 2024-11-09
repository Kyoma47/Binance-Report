import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def get_crypto_data(symbol, interval="1h"):
    end_date = datetime.now()
    if interval == "1h":
        start_date = end_date - timedelta(days=35)  # ~840 heures pour 200 périodes de 1h avec marge
    else:  # Pour l'intervalle journalier
        start_date = end_date - timedelta(days=220)  # 220 jours pour avoir 200 périodes avec marge
    
    try:
        crypto = yf.Ticker(symbol)
        df = crypto.history(start=start_date, end=end_date, interval=interval)
        
        if df.empty:
            return None

        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {symbol} avec l'intervalle {interval}: {e}")
        return None

def calculate_mayer_multiple(df):
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Mayer_Multiple'] = df['Close'] / df['MA200']
    
    bands = [0.5, 1, 1.5, 2, 2.5]
    for band in bands:
        df[f'Band_{band}'] = df['MA200'] * band
    
    last_data = df.iloc[-1]
    
    return {
        'Date': last_data.name,
        'Close': last_data['Close'],
        'MA200': last_data['MA200'],
        'Mayer_Multiple': last_data['Mayer_Multiple'],
        'Band_0.5': last_data['Band_0.5'],
        'Band_1': last_data['Band_1'],
        'Band_1.5': last_data['Band_1.5'],
        'Band_2': last_data['Band_2'],
        'Band_2.5': last_data['Band_2.5']
    }

def get_mayer_multiple(symbol):
    df = get_crypto_data(symbol, interval="1h")
    if df is None or len(df) < 200:
        print(f"Tentative avec l'intervalle journalier pour {symbol}")
        df = get_crypto_data(symbol, interval="1d")
    
    if df is not None and len(df) >= 200:
        return calculate_mayer_multiple(df)
    else:
        print(f"Pas assez de données disponibles pour {symbol}")
        return None

def get_multiple_crypto_data(crypto_list):
    all_data = {}
    
    for symbol in crypto_list:
        data = get_mayer_multiple(symbol)
        if data:
            all_data[symbol] = data
    
    return all_data

# Liste des crypto-monnaies
crypto_list = [
    'BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD',
    'PEPE1-USD', 'POLYX-USD', 'RNDR-USD', 'AGIX-USD'
]

# Récupération des données
crypto_data = get_multiple_crypto_data(crypto_list)

# Création d'un DataFrame avec les résultats
results_df = pd.DataFrame.from_dict(crypto_data, orient='index')
results_df.index.name = 'Symbol'

# Affichage des résultats
if not results_df.empty:
    pd.set_option('display.float_format', '{:.6f}'.format)
    print(results_df)
else:
    print("Aucune donnée valide n'a été récupérée.")

# Option pour sauvegarder les données dans un fichier CSV
save_to_csv = input("Voulez-vous sauvegarder les données dans un fichier CSV? (oui/non): ").lower() == 'oui'

if save_to_csv and not results_df.empty:
    filename = "crypto_mayer_bands_data.csv"
    results_df.to_csv(filename)
    print(f"Données sauvegardées dans {filename}")
elif save_to_csv:
    print("Aucune donnée à sauvegarder.")