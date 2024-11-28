
"""
import pandas as pd
from binance.client import Client
import ta

# Configuration de l'API Binance (assurez-vous d'avoir vos clés si nécessaire)
client = Client()

# Ajustement des dates de début et de fin
start_date = "01 January 2017"
end_date = "15 November 2024"

#fileName = 'historical_data_eth.csv'
fileName = "historical_data_eth_1M.csv"

# Récupération des données historiques
def fetch_and_save_data(symbol="ETHUSDT", interval=Client.KLINE_INTERVAL_1MIN, start=start_date, end=end_date, filename=fileName):
    
    # Récupère les données historiques depuis Binance et les enregistre dans un fichier CSV.

    print("Téléchargement des données en cours...")
    
    # Récupération des données historiques
    klinesT = client.get_historical_klines(symbol, interval, start, end)

    # Conversion des données en DataFrame
    df = pd.DataFrame(klinesT, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
    ])
    
    # Conversion des colonnes numériques
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

    # Conversion du timestamp et définition de l'index
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Suppression des colonnes inutiles
    df = df[['open', 'high', 'low', 'close', 'volume']]

    # Calcul des indicateurs techniques
    print("Calcul des indicateurs techniques...")
    df['EMA1'] = ta.trend.ema_indicator(close=df['close'], window=13)
    df['EMA2'] = ta.trend.ema_indicator(close=df['close'], window=38)

    # Sauvegarde des données dans un fichier CSV
    print(f"Enregistrement des données dans {filename}...")
    df.to_csv(filename)
    print("Téléchargement et traitement terminés.")
    return df

# Appel de la fonction pour télécharger et stocker les données
historical_data = fetch_and_save_data()
"""

import pandas as pd
import asyncio
import aiohttp
from datetime import datetime
from tqdm.asyncio import tqdm
import shutil
import ta

# Constantes
MAX_LIMIT = 1000  # Limite de bougies par requête
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

async def fetch_candles(session, symbol, interval, start_ts, end_ts, semaphore):
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ts,
        "endTime": end_ts,
        "limit": MAX_LIMIT,
    }
    tries = 0
    backoff = 0.1

    async with semaphore:
        while tries < 5:
            try:
                async with session.get(BINANCE_API_URL, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status in [429, 418]:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                    else:
                        return []
            except Exception as e:
                print(f"Erreur : {e} pour {start_ts} -> {end_ts}")
                await asyncio.sleep(backoff)
                backoff *= 2
            tries += 1
    return []

async def fetch_all_candles(symbol, start_date, end_date):
    start_ts = int(datetime.strptime(start_date, "%d %B %Y").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%d %B %Y").timestamp() * 1000)
    tasks = []
    semaphore = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        current_ts = start_ts
        while current_ts < end_ts:
            next_ts = min(current_ts + MAX_LIMIT * 60 * 1000, end_ts)
            tasks.append(fetch_candles(session, symbol, "1m", current_ts, next_ts, semaphore))
            current_ts = next_ts + 1

        results = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Téléchargement des données"):
            result = await coro
            results.extend(result)

    return results

def save_candles_with_indicators(data, filename):
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]

    print("Calcul des indicateurs techniques...")
    df['EMA1'] = ta.trend.ema_indicator(close=df['close'], window=13)
    df['EMA2'] = ta.trend.ema_indicator(close=df['close'], window=38)

    print(f"Enregistrement des données dans {filename}...")
    df.to_csv(filename)
    print("✅ Données avec indicateurs enregistrées dans", filename)

def main():
    symbol = "ETHUSDT"
    start_date = "01 January 2017"
    end_date = "15 November 2024"
    filename = "historical_data_eth_1M.csv"

    print(f"🔄 Récupération des données pour {symbol} de {start_date} à {end_date}...")
    all_data = asyncio.run(fetch_all_candles(symbol, start_date, end_date))
    print(f"📊 Nombre total de bougies récupérées : {len(all_data)}")
    save_candles_with_indicators(all_data, filename)
    #shutil.copy(filename, "BACKUP_ETH.csv")
    print("🚀 Sauvegarde terminée.")

if __name__ == "__main__":
    main()
