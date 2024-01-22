package schemas

import "time"

type Vault struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `default:"" json:"description"`
	UserID      string    `json:"userId"`
	CreatedAt   time.Time `json:"createdAt"`
	Tags        []string  `json:"tags"`
	IsDefault   bool      `default:"false" json:"isDefault"`
}
