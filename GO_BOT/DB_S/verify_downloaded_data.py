# part 1 

import pandas as pd

def validate_data_integrity(file_name, symbol, interval, expected_currency):
    """
    Valide l'intégrité des données dans un fichier CSV.
    
    :param file_name: Nom du fichier CSV contenant les données.
    :param symbol: Le symbole attendu (ex: "ETHUSDT").
    :param interval: Intervalle attendu des timestamps (ex: "1min").
    :param expected_currency: Monnaie attendue (ex: "ETH").
    :return: Un dictionnaire contenant les résultats des vérifications.
    """
    print(f"🔍 Vérification des données pour {file_name}...")

    # Chargement des données
    try:
        df = pd.read_csv(file_name, parse_dates=['timestamp'], index_col='timestamp')
        print(f"✅ Données chargées : {len(df)} lignes.")
    except FileNotFoundError:
        return {"status": "error", "message": f"Fichier introuvable : {file_name}"}
    except pd.errors.EmptyDataError:
        return {"status": "error", "message": f"Fichier vide ou mal formaté : {file_name}"}

    results = {"status": "success", "issues": []}

    # Vérification de la monnaie (optionnelle si incluse dans les données)
    if "symbol" in df.columns and not all(df["symbol"] == symbol):
        results["issues"].append("Currency mismatch: Le symbole ne correspond pas aux données.")
        print(f"❌ Currency mismatch : {symbol} attendu, mais les données contiennent d'autres symboles.")

    # Vérification des doublons
    if df.index.duplicated().any():
        results["issues"].append("Duplicate timestamps: Les données contiennent des doublons.")
        print("❌ Doublons détectés dans les données.")

    # Vérification de l'ordre
    if not df.index.is_monotonic_increasing:
        results["issues"].append("Unsorted data: Les données ne sont pas triées.")
        print("❌ Les données ne sont pas triées.")

    # Vérification des timestamps manquants
    start_date = df.index.min()
    end_date = df.index.max()
    complete_index = pd.date_range(start=start_date, end=end_date, freq=interval)
    missing_timestamps = complete_index.difference(df.index)

    if len(missing_timestamps) > 0:
        results["issues"].append(f"Missing data: {len(missing_timestamps)} timestamps manquants.")
        print(f"❌ {len(missing_timestamps)} timestamps manquants détectés.")
    else:
        print("✅ Aucun timestamp manquant détecté.")

    # Vérification du timestamp correct
    if len(df) > 0:
        first_timestamp = df.index.min()
        last_timestamp = df.index.max()

        if first_timestamp != complete_index[0] or last_timestamp != complete_index[-1]:
            results["issues"].append("Timestamp mismatch: Les timestamps ne correspondent pas à l'intervalle attendu.")
            print(f"❌ Les timestamps des données ({first_timestamp} -> {last_timestamp}) ne correspondent pas à l'intervalle attendu.")

    if not results["issues"]:
        print("✅ Toutes les vérifications ont été passées avec succès.")
    else:
        print("\n--- Résumé des problèmes détectés ---")
        for issue in results["issues"]:
            print(f"  - {issue}")

    return results

file_name = "historical_data_eth_1M.csv"
symbol = "ETHUSDT"
interval = "1min"
expected_currency = "ETH"

results = validate_data_integrity(file_name, symbol, interval, expected_currency)

if results["status"] == "success":
    print("\n✅ Validation terminée. Aucun problème majeur détecté.")
else:
    print("\n❌ Validation échouée.")

# part 2 
import pandas as pd
from tqdm import tqdm

"""
code utilisé pour trier la base de donnée 
"""

def sort_csv_in_place(file_name):
    """
    Trie un fichier CSV par colonne de timestamp, de la plus ancienne à la plus récente,
    et réécrit le fichier d'origine avec les données triées.

    :param file_name: Nom du fichier CSV à trier.
    """
    print(f"🔄 Tri des données dans {file_name}...")

    # Chargement des données
    try:
        df = pd.read_csv(file_name, parse_dates=['timestamp'])
        print(f"✅ Données chargées : {len(df)} lignes.")
    except FileNotFoundError:
        raise ValueError(f"Fichier introuvable : {file_name}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"Fichier vide ou mal formaté : {file_name}")
    
    # Vérification de la colonne de timestamp
    if 'timestamp' not in df.columns:
        raise ValueError("La colonne 'timestamp' est manquante dans le fichier.")
    
    # Barre de progression pour simuler le tri
    tqdm.pandas(desc="🔍 Tri des données")
    df.sort_values(by='timestamp', inplace=True)
    print("✅ Tri effectué.")
    
    # Réécrire les données triées dans le même fichier
    print(f"💾 Réécriture des données triées dans {file_name}...")
    df.to_csv(file_name, index=False)
    print("✅ Réécriture terminée.")

file_name = "historical_data_eth_1M.csv"

sort_csv_in_place(file_name)

print(f"✅ Fichier trié et réécrit : {file_name}")

# part 3 
import pandas as pd
from tqdm import tqdm

"""
on supprime les doublons, il analyse les timestamp et supprime les doublons
"""

def remove_duplicates(file_name):
    """
    Analyse et supprime les doublons dans un fichier CSV basé sur l'index (timestamp).
    Modifie directement le fichier fourni.

    :param file_name: Chemin du fichier CSV à analyser et modifier.
    """
    print(f"🔍 Analyse du fichier {file_name} pour détecter les doublons...")
    
    try:
        # Charger les données
        df = pd.read_csv(file_name, parse_dates=['timestamp'], index_col='timestamp')
        print(f"✅ Données chargées : {len(df)} lignes.")

        # Identifier les doublons
        duplicated = df.index.duplicated(keep='first')
        num_duplicates = duplicated.sum()

        if num_duplicates == 0:
            print("✅ Aucun doublon détecté.")
            return
        else:
            print(f"❌ {num_duplicates} doublons détectés.")
        
        # Suppression des doublons avec une barre de progression
        print("🔄 Suppression des doublons en cours...")
        df = df[~duplicated]
        
        # Réécrire le fichier original
        print("💾 Mise à jour du fichier CSV...")
        df.to_csv(file_name)
        print(f"✅ Doublons supprimés. Fichier mis à jour : {file_name}")
    
    except FileNotFoundError:
        print(f"❌ Fichier introuvable : {file_name}")
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")

file_name = "historical_data_eth_1M.csv"
remove_duplicates(file_name)

# part 4
###############################
# Verificer l'intégrité de la base de donnée
###############################

file_path = 'historical_data_eth_1M.csv'  # Chemin vers votre fichier CSV
df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')

#############################
# vérification de l'entièreté de la base de donnée 
############################
expeted_interval = pd.Timedelta('1min')
timestamp_diff = df.index.to_series().diff()

anomalies = timestamp_diff[timestamp_diff != expeted_interval]

# on exclus la première ligne comme une anomalie 
anomalies = timestamp_diff[1:][timestamp_diff[1:] != expeted_interval]

# Afficher le résultat
if anomalies.empty:
    print("✅ La base de données est complète. Tous les timestamps respectent l'intervalle de 1 minute.")
else:
    print(f"❌ La base de données a {len(anomalies)} anomalies.")
    print("Premières anomalies détectées :")
    print(anomalies.head())

#############################
# afficher l'entièreté de la base de donnée en % 
#############################
# plage complete attendue
expected_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='1min')
# calculer les stat 
total_expected = len(expected_index)
total_present = len(df)
total_missing = total_expected - total_present
# ccalculer le pourcentage de complétude 
completeness_percentage = (total_present / total_expected) * 100
# Afficher les résultats
print(f"🔍 Vérification de la complétude des données...")
print(f"📊 Total attendu : {total_expected} timestamps")
print(f"📊 Total présent : {total_present} timestamps")
print(f"📊 Total manquant : {total_missing} timestamps")
print(f"📊 Complétude des données : {completeness_percentage:.2f}%")

#############################
# afficher le temps quil nous manque au totale 
#############################
missing_timestamps = expected_index.difference(df.index)
# Calculer le temps total manquant
if not missing_timestamps.empty:
    total_missing_time = missing_timestamps[-1] - missing_timestamps[0]
    total_minutes_missing = len(missing_timestamps)  # Nombre total de minutes manquantes
    days, remainder = divmod(total_minutes_missing, 1440)  # 1 jour = 1440 minutes
    hours, minutes = divmod(remainder, 60)

    # Afficher les résultats
    print(f"⏳ Temps total manquant : {days} jours, {hours} heures, {minutes} minutes.")
    print(f"📊 Total manquant en minutes : {total_minutes_missing}")
else:
    print("✅ Aucune donnée manquante. Le fichier est complet.")

