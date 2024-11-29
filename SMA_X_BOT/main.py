
# nouvelle version de la stratégie précédente 
# utilidation de moyenne mobile simple 
"""
/*****************************\
|*Indicateur utilisé : SMA_X *|
\*****************************/

    * La stratégie repose sur l'utilisation d'une moyenne mobile simple (SMA_X) sur X périodes comme principal indicateur.

    * La SMA_X est utilisée pour déterminer la tendance actuelle du marché : lorsque le prix dépasse cette moyenne,
    cela indique une possible tendance haussière à court terme, favorable à une opportunité d'achat.
"""

import pandas as pd
import ta 
import numpy as np
import uuid
import matplotlib.pyplot as plt


# on récupère la base de donnée 
def downloadDb(filaname):
    print("Start downloading data...")
    global START_DATE, END_DATE
    # on stocke les données dans un data frame on parse les dates et on les indexe
    df = pd.read_csv(filaname, parse_dates=['timestamp'], index_col='timestamp')
    # on filtre les données selon les dates 
    if START_DATE:
        df = df[df.index >= pd.Timestamp(START_DATE)]
    if END_DATE:
        df = df[df.index <= pd.Timestamp(END_DATE)]
    # on vérifie si la db est pas vide
    if df.empty:
        raise ValueError("No data available for the selected date range.")
    return df 

# on vérifie l'intégrité de la base de donnée
def verify_db_integrity(df, freq):
    # Créer un index complet basé sur les limites des timestamps
    complete_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=freq)
    # Identifier les timestamps manquants
    missing_timestamps = complete_index.difference(df.index)
    if missing_timestamps.empty:
        print("No missing timestamps.")
    else:
        print(f"Missing timestamps")

# on subdivise la base de donnée par date
def subdivide_db_by_date(df):
    print("Start subdividing db by name...")
    # grouper les données par jour
    grouped = df.groupby(pd.Grouper(freq='D'))
    # crée un dictionnaire ou chaque clef est une date et chaque valeur est le DataFrame correspondant
    daily_data = {date: data for date, data in grouped}
    return daily_data

# supprime mes jours qui ne ont pas 1440 min ou tout le SMA_X de calculé
def remove_incomplete_days(daily_data):
    print("Start filtering daily_data...")
    filtered_data = {}
    removed_days = []
    for date, data in daily_data.items():
        if len(data) != 1440 or data['SMA_X'].isna().any():
            removed_days.append(date)  # Enregistrer les jours supprimés
        else:
            filtered_data[date] = data  # Conserver les jours complets
    return filtered_data

# vérifie l'intégrité des données et affiche un print 
def verify_daily_data_integrity(daily_data):
    print("🔍 Vérification de l'intégrité des données journalières...")
    issues_found = False  # Indicateur si des problèmes sont détectés
    for date, data in daily_data.items():
        if len(data) == 1440:  # Vérifier les jours complets
            missing_sma = data['SMA_X'].isna().sum()  # Vérifier SMA_X manquant
            if missing_sma > 0:
                #print(f"❌ SMA_X incomplet pour le jour {date.date()} - {missing_sma} valeurs manquantes.")
                issues_found = True
        else:
            #print(f"⚠️ Jour {date.date()} ignoré (données incomplètes, {len(data)} minutes).")
            issues_found = True
    if not issues_found:
        print("✅ Toutes les données journalières sont complètes et valides !")
    else:
        print(f"❌ Problème détecté dans les données")

# on calcul la moyenne mobile simple sur X périodes, et on supprime les période défectueses 
def calculate_sma_x_on_daily_data(daily_data):
    # valeur globale du SMA qu'on à défini 
    global SMA_VALUE
    print("Start calculating SMA_X on daily data...")
    # Données précédentes
    previous_data = pd.DataFrame()
    skipped_days = 0
    processed_days = 0
    filtered_data = {}  # Stocker les jours valides avec SMA_X complet
    for date, data in daily_data.items():
        # Ajouter la colonne SMA_X avec des valeurs NaN par défaut
        data['SMA_X'] = np.nan
        # Vérifier qu'il y a bien 1440 minutes dans la journée
        if len(data) != 1440:
            #print(f"Skipping date {date}: insufficient data ({len(data)} minutes)")
            skipped_days += 1
            continue
        # Combiner les données précédentes avec celles du jour actuel
        combined_data = pd.concat([previous_data, data])
        # Calculer le SMA_X globalement
        combined_data['SMA_X'] = ta.trend.sma_indicator(combined_data['close'], window=SMA_VALUE)
        # Vérifier si toutes les lignes actuelles ont un SMA_X calculé
        if combined_data['SMA_X'].loc[data.index].isna().any():
            #print(f"Skipping date {date}: incomplete SMA_X calculation.")
            skipped_days += 1
            # Mettre à jour les données précédentes pour le prochain jour
            previous_data = data.tail(SMA_VALUE)
            continue
        # Appliquer les valeurs calculées au DataFrame du jour actuel
        data['SMA_X'] = combined_data['SMA_X'].loc[data.index]
        filtered_data[date] = data  # Conserver uniquement les jours valides
        processed_days += 1
        # Mettre à jour les données précédentes (20 dernières minutes)
        previous_data = data.tail(SMA_VALUE)
    print(f"SMA_X calculation completed. Processed days: {processed_days}, ❌ Skipped days: {skipped_days}")
    return filtered_data

# condition de achat 
def buy_condition(data_row):
    # si cette condition est bonne on retourne true, c'est la condition d'achat
    if data_row['close'] > data_row['SMA_X']:
        return True
    # la condition n'est pas bonne on retourne false
    return False

# condition de vente
def sell_condition(data_row, position):
    # temps max entre chaque tarsaction / trade 
    global MAX_WINDOW
    # current_time est la date actuelle
    current_time = data_row.name
    # Vérifier si le prix atteint ou dépasse le target_price
    if data_row['close'] >= position['target_price']:
        return True  # Vente réussie à l'objectif de profit
    # Vérifier si la position est ouverte depuis plus de `window_size` minutes
    if (current_time - position['buy_date']).total_seconds() / 60 > MAX_WINDOW:
        return True  # Vente forcée après 60 minutes
    return False  # Pas de vente

# creation de transaction , à chaque fois que on achète on crée cet élément 
def create_transaction(buy_date, buy_price, quantity, buy_fee, target_price):
    return {
        "id": str(uuid.uuid4()), # ID unique pour chaque transaction
        "buy_date": buy_date,    # Date et heure d'achat
        "buy_price": buy_price,  # Prix d'achat
        "quantity": quantity,    # Quantité achetée
        "target_price": target_price, # prix cible
        "buy_fee": buy_fee,      # Frais d'achat
        "sell_fee": None,        # Frais de vente (sera mis à jour lors de la vente)
        "sell_date": None,       # Date et heure de vente
        "sell_price": None,      # Prix de vente
        "profit": None           # Profit calculé après la vente
    }

# gère la transaction d'achat , donc ce que on avais avant dans la condition d'achat dans trade se retrouve ici 
def treat_buy_transaction(row, invest_amount, fee_rate, min_profit):
    global BALANCE
    #print(f"Buy condition met at {row.name}")
    # Calcul des frais d'achat
    buy_fee = invest_amount * fee_rate
    # Montant net après déduction des frais
    net_investment = invest_amount - buy_fee
    # Quantité calculée en fonction du prix
    quantity = net_investment / row['close']
    # Calcul du prix cible (target_price)
    target_price = row['close'] * (1 + min_profit + 2 * fee_rate)
    # on met à jour le solde
    BALANCE -= invest_amount
    # Création d'une nouvelle transaction
    return create_transaction(row.name, row['close'], quantity, buy_fee, target_price)

# on traite la transaction de vente
def treat_sell_transaction(data_row, transaction, fee_rate):
    global BALANCE
    #print(f"Sell condition met at {data_row.name}")
    # Prix de vente
    sell_price = data_row['close']
    # Calcul des frais de vente
    sell_fee = sell_price * transaction['quantity'] * fee_rate
    # Montant net obtenu après la vente
    net_proceeds = sell_price * transaction['quantity'] - sell_fee
    # Calcul du profit
    profit = net_proceeds - (transaction['buy_price'] * transaction['quantity'] + transaction['buy_fee'])
    # Mise à jour de la transaction
    transaction.update({
        "sell_fee": sell_fee,
        "sell_date": data_row.name,
        "sell_price": sell_price,
        "profit": profit,
    })
    # on met à jour le solde
    BALANCE += net_proceeds

# print de compte rendu
def print_report(archived_transactions, transactions):
    # Valeur du portefeuille
    global BALANCE
    print(f"/Start de print de compte rendu.\\")
    # Frais
    total_buy_fee = archived_transactions['buy_fee'].sum()
    total_sell_fee = archived_transactions['sell_fee'].sum()
    total_fees = total_buy_fee + total_sell_fee
    print(f"Total frais d'achat : {total_buy_fee:.2f}")
    print(f"Total frais de vente : {total_sell_fee:.2f}")
    print(f"Total frais : {total_fees:.2f}")
    # Profits et soldes
    total_profit = archived_transactions['profit'].sum()
    print(f"Profit total : {total_profit:.2f}")
    print(f"Solde final : {BALANCE:.2f}")
    print(f"Nombre de transactions : {len(archived_transactions)}")

    # Transactions par année
    if 'sell_date' in archived_transactions:
        archived_transactions['sell_date'] = pd.to_datetime(archived_transactions['sell_date'])
        years = archived_transactions['sell_date'].dt.year.unique()
        avg_transactions_per_year = len(archived_transactions) / len(years)
        print(f"Transactions par année en moyenne : {avg_transactions_per_year:.2f}")
    else:
        print("Pas de dates de vente disponibles pour calculer les transactions par année.")

    # Calcul du temps moyen d'un trade
    archived_transactions['trade_duration'] = (
        (pd.to_datetime(archived_transactions['sell_date']) - 
         pd.to_datetime(archived_transactions['buy_date']))
        .dt.total_seconds() / 60
    )
    avg_trade_duration = archived_transactions['trade_duration'].mean()
    avg_days = int(avg_trade_duration // (24 * 60))
    avg_hours = int((avg_trade_duration % (24 * 60)) // 60)
    avg_minutes = int(avg_trade_duration % 60)
    print(f"Durée moyenne d'un trade : {avg_days} jours, {avg_hours} heures, {avg_minutes} minutes ({avg_trade_duration:.2f} minutes)")

    # Temps moyen par année
    print("\nTemps moyen d'un trade par année :")
    archived_transactions['year'] = archived_transactions['buy_date'].dt.year
    for year, group in archived_transactions.groupby('year'):
        avg_duration_year = group['trade_duration'].mean()
        days = int(avg_duration_year // (24 * 60))
        hours = int((avg_duration_year % (24 * 60)) // 60)
        minutes = int(avg_duration_year % 60)
        print(f"  {year}: {days} jours, {hours} heures, {minutes} minutes ({avg_duration_year:.2f} minutes)")

    # Taux de réussite
    winning_trades = archived_transactions[archived_transactions['profit'] > 0].copy()
    losing_trades = archived_transactions[archived_transactions['profit'] <= 0].copy()
    success_rate = len(winning_trades) / len(archived_transactions) * 100
    print(f"\nTaux de réussite : {success_rate:.2f}% ({len(winning_trades)} gagnants, {len(losing_trades)} perdants)")

    # Gain moyen par transaction
    avg_profit_per_trade = archived_transactions['profit'].mean()
    print(f"Gain moyen par transaction : {avg_profit_per_trade:.2f} EUR")

    # Temps moyen des trades gagnants et perdants
    winning_trades['trade_duration'] = (
        (pd.to_datetime(winning_trades['sell_date']) - 
         pd.to_datetime(winning_trades['buy_date']))
        .dt.total_seconds() / 60
    )
    losing_trades['trade_duration'] = (
        (pd.to_datetime(losing_trades['sell_date']) - 
         pd.to_datetime(losing_trades['buy_date']))
        .dt.total_seconds() / 60
    )

    avg_winning_duration = winning_trades['trade_duration'].mean() if not winning_trades.empty else 0
    avg_losing_duration = losing_trades['trade_duration'].mean() if not losing_trades.empty else 0

    def format_duration(minutes):
        days = int(minutes // (24 * 60))
        hours = int((minutes % (24 * 60)) // 60)
        mins = int(minutes % 60)
        return f"{days} jours, {hours} heures, {mins} minutes"

    if not winning_trades.empty:
        print(f"Temps moyen des trades gagnants : {format_duration(avg_winning_duration)} ({avg_winning_duration:.2f} minutes)")
    else:
        print("Pas de trades gagnants.")

    if not losing_trades.empty:
        print(f"Temps moyen des trades perdants : {format_duration(avg_losing_duration)} ({avg_losing_duration:.2f} minutes)")
    else:
        print("Pas de trades perdants.")

    # Nombre de trades gagnants et perdants par année
    print("\nNombre de trades gagnants et perdants par année :")
    for year, group in archived_transactions.groupby('year'):
        wins = len(group[group['profit'] > 0])
        losses = len(group[group['profit'] <= 0])
        print(f"  {year}: {wins} gagnants, {losses} perdants")


# fonction de trading c'est ici on vas faire le backtest 
def trade(daily_data):
    # on utilise les variables globales
    global BALANCE, INVEST_AMOUNT, FEE, MAX_TRANSACTION, TARGET_PROFIT
    # print de début de trading
    print("Start of trading...")
    # investement par trade
    invest_amount = INVEST_AMOUNT
    # buy and sell fee of 0.1% 
    fee_rate = FEE
    #min profit
    min_profit = TARGET_PROFIT
    # on vas stocker chaque transaction dans cette liste
    transactions = []  # Liste des transactions
    # transactions archivés 
    archived_transactions = []  # Liste des transactions archivées
    # on parcours les données
    for date, data in daily_data.items():
        # on parcour chaque ligne de la data
        for i, row in data.iterrows():
            # condition d'achat , si elle est vrai + on à assez de cash + on a pas le max de transaction, on achète 
            if len(transactions) < MAX_TRANSACTION and BALANCE >= INVEST_AMOUNT and buy_condition(row):
                # on crée une nouvelle transaction
                new_transaction = treat_buy_transaction(row, invest_amount, fee_rate, min_profit)
                # si la nouvelle transaction est vrai on l'ajoute à la liste des transactions
                if new_transaction:
                    transactions.append(new_transaction)
            # on passe à travers chaque transaction
            for transaction in transactions[:]:
                # si la condition de vente est vrai 
                if sell_condition(row, transaction):
                    # on traite la transaction de vente
                    treat_sell_transaction(row, transaction, fee_rate)
                    # on ajoute la transaction à la liste des transactions archivées
                    archived_transactions.append(transaction)
                    # on retire la transaction de la liste des transactions
                    transactions.remove(transaction)
    # Clôturer les transactions ouvertes restantes
    if transactions:
        print(f"Clôture de {len(transactions)} transactions ouvertes restantes au dernier prix disponible.")
        last_date = sorted(daily_data.keys())[-1]
        last_data = daily_data[last_date]
        last_row = last_data.iloc[-1]
        for transaction in transactions:
            treat_sell_transaction(last_row, transaction, fee_rate)
            archived_transactions.append(transaction)
        transactions.clear()

    # on converti les transactions archivés en DataFrame, ceci sera plus facile à manipuler plus tard 
    df_archived_transactions = pd.DataFrame(archived_transactions)
    print_report(df_archived_transactions, transactions)
    return 

# valeur du portefeuille
BALANCE = 100
# montant d'investissment systématique
INVEST_AMOUNT = (BALANCE / 100) * 50
# frais de achat et de vente 
FEE = 0.001
# nombre de transaction maximum à la fois
MAX_TRANSACTION = 6 
# profit recherché 
TARGET_PROFIT = 0.030
# temps max entre chaque tarsaction / trade
MAX_WINDOW = (60 * 24 * 90)
# valeur du SMA_X
SMA_VALUE = 650
# date de ébut 
START_DATE = "2020-01-01"
# date de fin
END_DATE = "2024-11-15"
# nom du fichier de la base de donnée
FILE_NAME = "1_min_eth_candles_01012017_15112024.csv"

def main():
    # on download la base de donnée 
    df = downloadDb(FILE_NAME)
    # verifier la db
    verify_db_integrity(df, '1min')
    # devide by name 
    daily_data = subdivide_db_by_date(df)
    # calculer la moyenne mobile simple sur 20 périodes
    daily_data = calculate_sma_x_on_daily_data(daily_data)
    # on trade
    trade(daily_data)
    
if __name__ == "__main__":
    main()

"""
                    <<<<<***********************>>>>>
                    <<<<< Remarques importantes >>>>>
                    <<<<<***********************>>>>>

* Remarques importantes :

* Je vous conseille de mettre le code dans un fichier jupiter notebook pour une meilleur visualisation.

* Les valeur actuelles des variables sont le résultat de mes propre test. 

* Je ne vous conseille en aucun cas de les utiliser tel quel, il faut les tester et les ajuster selon vos besoins.

* De plus je ne vous conseille pas non plus de les utiliser en production, c'est juste un exemple de backtest.

* Je ne conseille pas non plus de utiliser le bot en production, il n'a pas été testé en production et il n'est pas sécurisé + la
stratégie n'est pas optimisé et n'est pas garantie de fonctionner.

!! Ne utilisez pas se bot, ou cette stratégie elle ne sont en rien fondé, ce projet est juste un passe temps et un projet personnel.!!

(Si vous avez des suggestions n'hésitez pas à me les partager)

"""