// logging/logger.go
package logging

import (
	"encoding/csv"
	"os"
	"strconv"
	"test_crypto_bot/portfolio"
)

func LogTrades(trades []portfolio.Trade, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Écrire l'en-tête
	header := []string{"Date", "Type", "Price", "Amount", "Fee", "USD", "Crypto", "Wallet", "Drawdown", "Reason", "Profit", "ProfitPerc"}
	writer.Write(header)

	for _, trade := range trades {
		record := []string{
			trade.Date.Format("2006-01-02 15:04:05"),
			trade.Type,
			formatFloat(trade.Price),
			formatFloat(trade.Amount),
			formatFloat(trade.Fee),
			formatFloat(trade.USD),
			formatFloat(trade.Crypto),
			formatFloat(trade.Wallet),
			formatFloat(trade.Drawdown),
			trade.Reason,
			formatFloat(trade.Profit),
			formatFloat(trade.ProfitPerc),
		}
		writer.Write(record)
	}

	return nil
}

func formatFloat(num float64) string {
	return strconv.FormatFloat(num, 'f', 8, 64)
}
