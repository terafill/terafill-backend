package schemas

import "time"

type Session struct {
	ID                   string
	UserId               string
	SessionToken         string
	SessionPrivateKey    string
	ClientId             string
	PlatformClientId     string
	ClientType           string
	SessionEncryptionKey string
	SrpServerPrivateKey  string
	SrpClientPublicKey   string
	Activated            bool
	CreatedAt            time.Time
	ExpiryAt             time.Time
}
