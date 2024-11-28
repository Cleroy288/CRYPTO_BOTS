import pandas as pd
import asyncio
import aiohttp
from datetime import datetime
from tqdm.asyncio import tqdm
import os
import shutil

# nouvelle version du scripte pour télécharger les données de binance plsu rapidement

# Constantes
MAX_LIMIT = 1000  # Limite de bougies par requête
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

async def fetch_candles(session, symbol, interval, start_ts, end_ts, semaphore):
    """
    Récupère des bougies pour une plage donnée de timestamps.
    Implémente un backoff exponentiel en cas d'erreur.
    """
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ts,
        "endTime": end_ts,
        "limit": MAX_LIMIT,
    }
    tries = 0
    backoff = 0.1  # Temps d'attente initial en secondes

    async with semaphore:
        while tries < 5:  # Limite le nombre de tentatives à 5
            try:
                async with session.get(BINANCE_API_URL, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Erreur {response.status}: {response.reason} pour {start_ts} -> {end_ts}")
                        if response.status in [429, 418]:  # Limite de taux ou blocage temporaire
                            await asyncio.sleep(backoff)
                            backoff *= 2  # Double le temps d'attente à chaque tentative
                        else:
                            return []
            except Exception as e:
                print(f"Exception : {e} pour {start_ts} -> {end_ts}")
                await asyncio.sleep(backoff)
                backoff *= 2
            tries += 1

    print(f"❌ Échec final pour {start_ts} -> {end_ts}")
    return []

async def fetch_all_candles(symbol, start_date, end_date):
    """
    Récupère toutes les bougies 1m pour une paire donnée de manière asynchrone,
    avec une barre de progression.
    """
    start_ts = int(datetime.strptime(start_date, "%d %B %Y").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%d %B %Y").timestamp() * 1000)

    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limite à 10 requêtes simultanées
    async with aiohttp.ClientSession() as session:
        # Crée des tâches pour récupérer les données par lots de MAX_LIMIT
        current_ts = start_ts
        while current_ts < end_ts:
            next_ts = min(current_ts + MAX_LIMIT * 60 * 1000, end_ts)  # Prochain segment
            tasks.append(fetch_candles(session, symbol, "1m", current_ts, next_ts, semaphore))
            current_ts = next_ts + 1  # Passer au segment suivant

        # Barre de progression avec tqdm
        results = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Téléchargement des données"):
            result = await coro
            results.extend(result)

    return results

def save_candles_to_csv(data, filename):
    """
    Sauvegarde les bougies récupérées dans un fichier CSV.
    """
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'
    ])
    # Convertir les colonnes et formater le DataFrame
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df.to_csv(filename)
    print(f"✅ Données enregistrées dans {filename}")

def main():
    symbol = "ETHUSDT"
    start_date = "01 January 2017"
    end_date = "15 November 2024"
    filename = "1_min_eth_candles_01012017_15112024.csv"

    print(f"🔄 Récupération des données pour {symbol} de {start_date} à {end_date}...")
    all_data = asyncio.run(fetch_all_candles(symbol, start_date, end_date))
    print(f"📊 Nombre total de bougies récupérées : {len(all_data)}")
    save_candles_to_csv(all_data, filename)
    print(f"Sauvegarde des données terminée dans BACKUP_ETH.csv")
    shutil.copy("1_min_eth_candles_01012017_15112024.csv", "BACKUP_ETH.csv")
    

if __name__ == "__main__":
    main()

