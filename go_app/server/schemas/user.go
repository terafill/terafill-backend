package schemas

import "time"

type User struct {
	ID                    string
	CreatedAt             time.Time
	Email                 string
	Status                string
	EmailVerificationCode int
}
