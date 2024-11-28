// strategy/strategy.go
package strategy

import (
	"test_crypto_bot/indicators"
	"test_crypto_bot/portfolio"
	"time"
)

type Strategy struct {
	EMAFast        *indicators.EMA
	EMASlow        *indicators.EMA
	Portfolio      *portfolio.Portfolio
	PreviousSignal string
}

func NewStrategy(port *portfolio.Portfolio, fastPeriod, slowPeriod int) *Strategy {
	return &Strategy{
		EMAFast:   indicators.NewEMA(fastPeriod),
		EMASlow:   indicators.NewEMA(slowPeriod),
		Portfolio: port,
	}
}

func (s *Strategy) OnTick(price float64, date time.Time) {
	emaFastValue := s.EMAFast.Calculate(price)
	emaSlowValue := s.EMASlow.Calculate(price)

	if emaFastValue == 0 || emaSlowValue == 0 {
		return // Pas assez de données pour calculer les EMA
	}

	if emaFastValue > emaSlowValue && s.Portfolio.USD > 0 && s.PreviousSignal != "Buy" {
		s.Portfolio.Buy(date, price)
		s.PreviousSignal = "Buy"
	} else if emaFastValue < emaSlowValue && s.Portfolio.Crypto > 0 && s.PreviousSignal != "Sell" {
		s.Portfolio.Sell(date, price)
		s.PreviousSignal = "Sell"
	}
}
