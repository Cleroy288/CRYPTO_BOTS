// indicators/indicators.go
package indicators

type EMA struct {
	Period int
	Value  float64
	K      float64
}

func NewEMA(period int) *EMA {
	return &EMA{
		Period: period,
		K:      2.0 / float64(period+1),
	}
}

func (e *EMA) Calculate(price float64) float64 {
	if e.Value == 0 {
		e.Value = price
	} else {
		e.Value = (price-e.Value)*e.K + e.Value
	}
	return e.Value
}
