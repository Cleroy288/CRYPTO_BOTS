// main.go
package main

import (
	"fmt"
	"test_crypto_bot/data_loader"
	"test_crypto_bot/logging"
	"test_crypto_bot/portfolio"
	"test_crypto_bot/strategy"
	"time"
)

// main.go

func main() {
	// Initialisation
	initialUSD := 1000.0
	feeRate := 0.001
	symbol := "BETHUSDT"
	interval := "1m"
	startDate := "2017-01-01T00:00:00Z"
	endDate := "2024-11-15T00:00:00Z"
	port := portfolio.NewPortfolio(initialUSD, feeRate)
	strat := strategy.NewStrategy(port, 13, 38) // Périodes EMA courte et longue

	// Simulation du flux de données (exemple avec des données historiques)
	// Chargement des données historiques
	fmt.Println("Chargement des données historiques...")
	data, err := data_loader.LoadData(symbol, interval, startDate, endDate)
	if err != nil {
		fmt.Printf("Erreur lors du chargement des données : %v\n", err)
		return
	}
	fmt.Printf("Nombre de bougies chargées : %d\n", len(data))

	for _, candle := range data {
		// Convertir le timestamp en time.Time
		timestamp := time.Unix(candle.Timestamp/1000, 0) // Diviser par 1000 pour obtenir les secondes
		strat.OnTick(candle.Close, timestamp)
	}

	// Affichage des résultats
	finalValue := port.GetCurrentValue(data[len(data)-1].Close)
	fmt.Printf("Solde final : %.2f USD\n", finalValue)
	fmt.Printf("Performance vs USD : %.2f%%\n", ((finalValue-initialUSD)/initialUSD)*100)
	fmt.Printf("Drawdown maximal : %.2f%%\n", port.MaxDrawdown*100)
	fmt.Printf("Total des frais : %.2f USD\n", port.TotalFees)
	fmt.Printf("Nombre de trades : %d\n", len(port.Trades))

	// Journalisation des trades
	logging.LogTrades(port.Trades, "trades.csv")
}

/*


/*******************\
 EXPLICATION DU CODE
/*******************\

Explication du Code et Fonctionnement
Ce document décrit la structure et le fonctionnement du bot de trading, en expliquant les différentes composantes, leur rôle, et leur interaction.

1. Structure du Code
Le code est organisé en plusieurs modules pour une meilleure lisibilité et maintenance :

models/candle.go
Définit la structure Candle utilisée pour stocker les données des bougies.

indicators/indicators.go
Contient les fonctions nécessaires au calcul des indicateurs techniques, comme les EMAs (Exponential Moving Averages).

portfolio/portfolio.go
Gère les soldes du portefeuille, les transactions, et calcule les métriques de performance (profit, drawdown, etc.).

strategy/strategy.go
Implémente la stratégie de trading basée sur les croisements EMA.

data_loader/data_loader.go
Récupère les données historiques via l’API Binance.

logging/logger.go
Gère l’enregistrement des transactions dans des fichiers CSV pour analyse.

main.go
Le point d’entrée du programme. Ordonne le chargement des données, l’exécution de la stratégie et l’affichage des résultats.

2. Fonctionnement du Code
a) Chargement des Données
Fonction : LoadData dans data_loader.go.
Rôle : Récupère les données historiques depuis l’API Binance pour une période définie.
Les données sont collectées par tranches (maximum de 1000 bougies par requête).
Chaque bougie est convertie en une structure Candle et stockée dans une liste.
b) Initialisation
Dans main.go, les paramètres suivants sont définis :

Capital initial : initialUSD
Frais : feeRate
Symbole de trading : symbol (par exemple, BTC/USDT)
Dates de début et de fin : startDate et endDate
Un portefeuille (Portfolio) est créé avec le capital initial et les frais, ainsi qu'une stratégie (Strategy) paramétrée pour des périodes spécifiques des EMAs.

c) Exécution de la Stratégie
Pour chaque bougie, la méthode OnTick de la stratégie est appelée :
Les EMAs rapide et lente sont mises à jour avec le prix de clôture actuel.
Les croisements des EMAs déterminent les signaux d'achat et de vente.
Achat : L'EMA rapide croise au-dessus de l'EMA lente et des USD sont disponibles.
Vente : L'EMA rapide croise en dessous de l'EMA lente et des cryptos sont détenues.
d) Gestion du Portefeuille
Le portefeuille gère les soldes en USD et en cryptos.
Chaque transaction calcule les frais, les profits, et les pertes, qui sont enregistrés.
e) Affichage des Résultats
Une fois toutes les données traitées, les résultats sont affichés :
Solde final
Performance (par rapport à l'USD)
Drawdown maximal
Total des frais
Nombre total de trades
Les transactions sont enregistrées dans un fichier CSV via LogTrades.
3. Fonctionnalités et Calculs
Calcul des EMAs
Les EMAs sont mises à jour incrémentalement à chaque nouvelle bougie.
Gestion des Trades
Méthodes : Buy et Sell
Rôle : Mettent à jour les soldes, calculent les frais et enregistrent chaque trade.
Analyse des Performances
Le portefeuille suit le solde courant, le drawdown maximal, et le profit net.
Les statistiques comme le pourcentage de profit ou la durée moyenne des trades sont calculées.
4. Comment Utiliser le Code
a) Configuration des Paramètres
Modifiez les paramètres dans main.go selon vos besoins :

Capital initial : initialUSD
Frais : feeRate
Périodes EMA : à définir dans Strategy.
b) Exécution
Compilez le programme avec :
	go build -o trading_bot
Lancez le programme :
	./trading_bot
OU :
	go run main.go

c) Résultats
Les résultats sont affichés dans la console.
Les transactions sont enregistrées dans un fichier CSV (trades.csv).
5. Points à Noter
Gestion des Erreurs
La fonction LoadData gère les erreurs d’API et respecte les limites de requêtes.
Modularité et Testabilité
Chaque composant (indicateurs, portefeuille, stratégie) est modulaire et peut être testé individuellement.
Améliorations possibles
Ajouter des indicateurs complémentaires.
Intégrer des filtres de tendance pour réduire les faux signaux.
Ce projet est un excellent point de départ pour explorer le trading algorithmique et apprendre les bases du traitement de données financières. N’hésitez pas à expérimenter et proposer vos améliorations !


*/
