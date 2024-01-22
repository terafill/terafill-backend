package schemas

type EncryptionKey struct {
	ItemID                 string `json:"id"`
	UserID                 string `json:"userId"`
	EncryptedEncryptionKey string `json:"encryptedEncryptionKey"`
}
