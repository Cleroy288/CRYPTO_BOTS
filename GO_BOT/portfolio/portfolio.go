// portfolio/portfolio.go
package portfolio

import (
	"time"
)

type Portfolio struct {
	USD          float64
	Crypto       float64
	FeeRate      float64
	InitialUSD   float64
	Trades       []Trade
	LastATH      float64
	CurrentValue float64
	MaxDrawdown  float64
	TotalFees    float64
}

type Trade struct {
	Date       time.Time
	Type       string // "Buy" or "Sell"
	Price      float64
	Amount     float64
	Fee        float64
	USD        float64
	Crypto     float64
	Wallet     float64
	Drawdown   float64
	Reason     string
	Profit     float64
	ProfitPerc float64
}

func NewPortfolio(initialUSD, feeRate float64) *Portfolio {
	return &Portfolio{
		USD:        initialUSD,
		InitialUSD: initialUSD,
		FeeRate:    feeRate,
		LastATH:    initialUSD,
	}
}

func (p *Portfolio) Buy(date time.Time, price float64) {
	if p.USD <= 0 {
		return
	}
	fee := p.USD * p.FeeRate
	netInvestment := p.USD - fee
	amount := netInvestment / price
	p.Crypto += amount
	p.USD = 0
	p.CurrentValue = p.Crypto * price
	p.TotalFees += fee // Ajouter cette ligne
	p.updateATH()
	drawdown := p.calculateDrawdown()
	trade := Trade{
		Date:     date,
		Type:     "Buy",
		Price:    price,
		Amount:   amount,
		Fee:      fee,
		USD:      p.USD,
		Crypto:   p.Crypto,
		Wallet:   p.CurrentValue,
		Drawdown: drawdown,
		Reason:   "EMA Cross Over",
	}
	p.Trades = append(p.Trades, trade)
}

func (p *Portfolio) Sell(date time.Time, price float64) {
	if p.Crypto <= 0 {
		return
	}
	grossProceeds := p.Crypto * price
	fee := grossProceeds * p.FeeRate
	netProceeds := grossProceeds - fee
	profit := netProceeds - (p.Crypto * p.Trades[len(p.Trades)-1].Price)
	profitPerc := (profit / (p.Crypto * p.Trades[len(p.Trades)-1].Price)) * 100
	p.USD += netProceeds
	p.Crypto = 0
	p.CurrentValue = p.USD
	p.TotalFees += fee // Ajouter cette ligne
	p.updateATH()
	drawdown := p.calculateDrawdown()
	trade := Trade{
		Date:       date,
		Type:       "Sell",
		Price:      price,
		Amount:     -p.Crypto,
		Fee:        fee,
		USD:        p.USD,
		Crypto:     p.Crypto,
		Wallet:     p.CurrentValue,
		Drawdown:   drawdown,
		Reason:     "EMA Cross Under",
		Profit:     profit,
		ProfitPerc: profitPerc,
	}
	p.Trades = append(p.Trades, trade)
}

func (p *Portfolio) updateATH() {
	if p.CurrentValue > p.LastATH {
		p.LastATH = p.CurrentValue
	}
}

func (p *Portfolio) calculateDrawdown() float64 {
	if p.LastATH == 0 {
		return 0
	}
	drawdown := (p.CurrentValue - p.LastATH) / p.LastATH
	if drawdown < p.MaxDrawdown {
		p.MaxDrawdown = drawdown
	}
	return drawdown
}

func (p *Portfolio) GetCurrentValue(price float64) float64 {
	return p.USD + p.Crypto*price
}
