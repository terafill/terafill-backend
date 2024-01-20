package schemas

import "time"

type Vault struct {
	ID          string
	Name        string
	Description string `default:""`
	UserID      string
	CreatedAt   time.Time
	Tags        []string
	IsDefault   bool `default:"false"`
}
