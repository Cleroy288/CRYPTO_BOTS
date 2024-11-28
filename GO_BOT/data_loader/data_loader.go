// data_loader/data_loader.go
package data_loader

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/adshao/go-binance/v2"
	"test_crypto_bot/models"
)

func LoadData(symbol string, interval string, startDate string, endDate string) ([]models.Candle, error) {
	// Vérifier si le fichier CSV existe
	filename := "./DB_S/historical_data_eth_1H.csv"
	if _, err := os.Stat(filename); err == nil {
		fmt.Println("Fichier de données historique trouvé. Chargement des données depuis le fichier CSV...")
		return loadDataFromCSV(filename, startDate, endDate)
	} else {
		fmt.Println("Fichier de données historique non trouvé. Chargement des données depuis l'API Binance...")
		return loadDataFromAPI(symbol, interval, startDate, endDate)
	}
}

// Fonction pour charger les données depuis le fichier CSV
func loadDataFromCSV(filename string, startDate string, endDate string) ([]models.Candle, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("erreur lors de l'ouverture du fichier CSV : %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("erreur lors de la lecture du fichier CSV : %v", err)
	}

	var allKlines []models.Candle
	layout := "2006-01-02 15:04:05"
	startTime, _ := time.Parse(time.RFC3339, startDate)
	endTime, _ := time.Parse(time.RFC3339, endDate)

	// Parcourir les enregistrements et les convertir en modèles Candle
	for i, record := range records {
		if i == 0 {
			// Ignorer l'en-tête
			continue
		}
		timestampStr := record[0]
		openStr := record[1]
		highStr := record[2]
		lowStr := record[3]
		closeStr := record[4]
		volumeStr := record[5]

		timestamp, err := time.Parse(layout, timestampStr)
		if err != nil {
			continue
		}

		if timestamp.Before(startTime) || timestamp.After(endTime) {
			continue
		}

		open, _ := strconv.ParseFloat(openStr, 64)
		high, _ := strconv.ParseFloat(highStr, 64)
		low, _ := strconv.ParseFloat(lowStr, 64)
		closePrice, _ := strconv.ParseFloat(closeStr, 64)
		volume, _ := strconv.ParseFloat(volumeStr, 64)

		candle := models.Candle{
			Timestamp: timestamp.Unix() * 1000, // Convertir en millisecondes
			Open:      open,
			High:      high,
			Low:       low,
			Close:     closePrice,
			Volume:    volume,
		}
		allKlines = append(allKlines, candle)
	}

	return allKlines, nil
}

// Fonction pour charger les données depuis l'API Binance
func loadDataFromAPI(symbol string, interval string, startDate string, endDate string) ([]models.Candle, error) {
	// 1. Convertir les dates en timestamps Unix
	layout := "2006-01-02T15:04:05Z"
	startTime, err := time.Parse(layout, startDate)
	if err != nil {
		return nil, fmt.Errorf("format de date invalide pour startDate: %v", err)
	}
	endTime, err := time.Parse(layout, endDate)
	if err != nil {
		return nil, fmt.Errorf("format de date invalide pour endDate: %v", err)
	}

	if startTime.After(endTime) {
		return nil, fmt.Errorf("startDate est après endDate")
	}

	// 2. Initialiser le client Binance
	client := binance.NewClient("", "") // Pas besoin de clés API pour les données publiques

	var allKlines []models.Candle
	limit := 1000 // Nombre maximum de bougies par requête

	ctx := context.Background()
	currentTime := startTime

	for {
		// 3. Récupérer les données par tranches de temps
		klines, err := client.NewKlinesService().
			Symbol(symbol).
			Interval(interval).
			Limit(limit).
			StartTime(currentTime.UnixNano() / int64(time.Millisecond)).
			EndTime(endTime.UnixNano() / int64(time.Millisecond)).
			Do(ctx)
		if err != nil {
			log.Printf("Erreur lors de la récupération des données : %v", err)
			time.Sleep(1 * time.Second) // Attendre avant de réessayer en cas d'erreur
			continue
		}

		if len(klines) == 0 {
			break // Plus de données à récupérer
		}

		// 4. Mapper les données API vers des structures Candle
		for _, k := range klines {
			open, _ := strconv.ParseFloat(k.Open, 64)
			high, _ := strconv.ParseFloat(k.High, 64)
			low, _ := strconv.ParseFloat(k.Low, 64)
			closePrice, _ := strconv.ParseFloat(k.Close, 64)
			volume, _ := strconv.ParseFloat(k.Volume, 64)

			candle := models.Candle{
				Timestamp: k.OpenTime,
				Open:      open,
				High:      high,
				Low:       low,
				Close:     closePrice,
				Volume:    volume,
			}
			allKlines = append(allKlines, candle)
		}

		// 5. Préparer la prochaine tranche de temps
		lastKline := klines[len(klines)-1]
		currentTime = time.Unix(0, lastKline.CloseTime*int64(time.Millisecond)*int64(time.Nanosecond))
		currentTime = currentTime.Add(1 * time.Millisecond)

		// Vérifier si on a atteint la fin
		if currentTime.After(endTime) {
			break
		}

		// Gérer les limites de taux de l'API
		time.Sleep(500 * time.Millisecond) // Attendre pour éviter de dépasser les limites de l'API
	}

	return allKlines, nil
}
