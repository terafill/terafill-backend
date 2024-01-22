package schemas

import "time"

type Item struct {
	ID                     string    `json:"id"`
	VaultID                string    `json:"vaultId"`
	UserID                 string    `json:"userId"`
	Title                  string    `name:"title"`
	Description            string    `default:"" json:"description"`
	Username               string    `name:"username"`
	Password               string    `name:"password"`
	Website                string    `name:"website"`
	Tags                   []string  `json:"tags"`
	Type                   string    `json:"type"`
	EncryptedEncryptionKey string    `json:"encryptedEncryptionKey"`
	IsFavorite             bool      `default:"false" json:"isFavorite"`
	CreatedAt              time.Time `json:"createdAt"`
}
