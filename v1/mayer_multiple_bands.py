import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def get_mayer_multiple_bands(symbol, start_date, end_date):
    # Télécharger les données historiques
    crypto = yf.Ticker(symbol)
    df = crypto.history(start=start_date, end=end_date)

    # Calculer la moyenne mobile sur 200 jours
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # Calculer le Mayer Multiple
    df['Mayer_Multiple'] = df['Close'] / df['MA200']

    # Définir les bandes du Mayer Multiple
    bands = [0.5, 1, 1.5, 2, 2.5]
    for band in bands:
        df[f'Band_{band}'] = df['MA200'] * band

    # Visualisation optionnelle
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Prix')
    plt.plot(df.index, df['MA200'], label='MA200')
    for band in bands :
        plt.plot(df.index, df[f'Band_{band}'], label=f'Band {band}', linestyle='--')
    plt.legend()
    plt.title(f"Mayer Multiple Bands pour {symbol}")
    plt.yscale('log')
    plt.show()

    return df

def get_tradingview_mayer_multiple_bands(symbol, start_date, end_date):
    # Télécharger les données historiques
    crypto = yf.Ticker(symbol)
    df = crypto.history(start=start_date, end=end_date)

    # Calculer la moyenne mobile sur 200 jours
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # Calculer le Mayer Multiple
    df['Mayer_Multiple'] = df['Close'] / df['MA200']

    # Définir les bandes du Mayer Multiple
    mm1 = 0.45 # input(0.45, minval=0.1, title="About 3 Stdev Below")
    mm2 = 0.75 # input(0.75, minval=0.1, title="About 2 Stdev Below")
    mm3 = 1.05 # input(1.05, minval=0.1, title="About 1 Stdev Below")
    mm4 = 1.45 # input(1.45, minval=0.1, title="Mean Mayer Multiple")
    mm5 = 1.95 # input(1.95, minval=0.1, title="About 1 Stdev Above")
    mm6 = 3.85 # input(3.85, minval=0.1, title="About 2 Stdev Above")
    mm7 = 6.35 # input(6.35, minval=0.1, title="About 3 Stdev Above")
    bands = [ mm1, mm2, mm3, mm4, mm5, mm6, mm7 ]
    for band in bands:
        df[f'Band_{band}'] = df['MA200'] * band
    
    # Visualisation optionnelle
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Prix')
    plt.plot(df.index, df['MA200'], label='MA200')
    for band in bands :
        plt.plot(df.index, df[f'Band_{band}'], label=f'Band {band}', linestyle='--')
    plt.legend()
    plt.title(f"Mayer Multiple Bands pour {symbol}")
    plt.yscale('log')
    plt.show()

    return df




# Exemple d'utilisation
'''
symbol = "BTC-USD"  # Bitcoin
start_date = "2020-01-01"
end_date = "2024-10-14"  # Date actuelle

df = get_mayer_multiple_bands(symbol, start_date, end_date)
#df = get_tradingview_mayer_multiple_bands(symbol, start_date, end_date)
print(df.tail())
'''

# Liste des crypto-monnaies
crypto_list = [
	"AAVE", "ANKR", "BNB", "BONK", "BTC", "CKB", "DOGE", "DOT", "DUSK", 
	"ETH", "FET", "FLOKI", "GLM", 
	"INJ", "JASMY", "JUP", "LINK", "LPT", 
	"NEAR", "OM", "OP", "ORDI", "PENDLE", "PEPE", "POL", "PYTH", 
	"RENDER", "SHIB", "SOL", "STRAX", "STX", "TAO", "TON", "TRU", 
	"UNI", "VET",
]
crypto_list = [ crypto +'-USD' for crypto in crypto_list ] # ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD']

for symbol in crypto_list : 
    start_date = "2020-01-01"
    end_date = "2024-10-14"  # Date actuelle
    #df = get_mayer_multiple_bands(symbol, start_date, end_date)
    df = get_tradingview_mayer_multiple_bands(symbol, start_date, end_date)