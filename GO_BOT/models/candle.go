// models/candle.go
package models

type Candle struct {
	Timestamp int64   // Horodatage de la bougie
	Open      float64 // Prix d'ouverture
	High      float64 // Prix le plus haut
	Low       float64 // Prix le plus bas
	Close     float64 // Prix de clôture
	Volume    float64 // Volume de la période
}
