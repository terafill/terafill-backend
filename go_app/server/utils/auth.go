package utils

import (
	"context"
	"database/sql"
	"log"
	"time"

	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"

	"encoding/json"

	"gopkg.in/square/go-jose.v2"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"terafill.com/m/server/crud"
	"terafill.com/m/server/schemas"
)

func GetSessionPrivateKey(alg string) (string, error) {
	var privateKeyBytes []byte
	var err error

	if alg == "ec" {
		privateKey, err := ecdsa.GenerateKey(elliptic.P521(), rand.Reader)
		if err != nil {
			return "", err
		}
		privateKeyBytes, err = x509.MarshalECPrivateKey(privateKey)
	} else {
		privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
		if err != nil {
			return "", err
		}
		privateKeyBytes = x509.MarshalPKCS1PrivateKey(privateKey)
	}

	if err != nil {
		return "", err
	}

	privateKeyPem := pem.EncodeToMemory(&pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: privateKeyBytes,
	})
	return string(privateKeyPem), nil
}

func GetSessionPublicKey(privateKeyPem string) (string, error) {
	block, _ := pem.Decode([]byte(privateKeyPem))
	if block == nil {
		return "", fmt.Errorf("failed to parse PEM block containing the key")
	}

	privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		return "", err
	}

	publicKey := &privateKey.PublicKey
	publicKeyBytes, err := x509.MarshalPKIXPublicKey(publicKey)
	if err != nil {
		return "", err
	}

	publicKeyPem := pem.EncodeToMemory(&pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: publicKeyBytes,
	})
	return string(publicKeyPem), nil
}

// SessionPayload represents the payload to be encoded in the token
type SessionPayload struct {
	UserID           string `json:"userId"`
	SessionID        string `json:"sessionId"`
	ClientID         string `json:"clientId"`
	PlatformClientID string `json:"platformClientId"`
	Tier             string `json:"tier"`
}

func GetSessionToken(payload SessionPayload, privateKeyPem string, alg string) (string, error) {
	privateKey, err := parseRSAPrivateKeyFromPEM(privateKeyPem)
	if err != nil {
		return "", err
	}

	var algJose jose.KeyAlgorithm
	switch alg {
	case "ec":
		algJose = jose.ECDH_ES_A256KW
	case "RSA-OAEP-256":
		algJose = jose.RSA_OAEP_256
	default:
		algJose = jose.RSA_OAEP
	}

	encrypter, err := jose.NewEncrypter(jose.A256GCM, jose.Recipient{Algorithm: algJose, Key: &privateKey.PublicKey}, nil)
	if err != nil {
		return "", err
	}

	marshaledPayload, err := json.Marshal(payload)
	if err != nil {
		return "", err
	}

	object, err := encrypter.Encrypt(marshaledPayload)
	if err != nil {
		return "", err
	}

	serialized, err := object.CompactSerialize()
	if err != nil {
		return "", err
	}

	return serialized, nil
}

func GetSessionDetails(token string, privateKeyPem string) (SessionPayload, error) {
	var payload SessionPayload

	privateKey, err := parseRSAPrivateKeyFromPEM(privateKeyPem)
	if err != nil {
		return payload, err
	}

	object, err := jose.ParseEncrypted(token)
	if err != nil {
		return payload, err
	}

	decrypted, err := object.Decrypt(privateKey)
	if err != nil {
		return payload, err
	}

	err = json.Unmarshal(decrypted, &payload)
	if err != nil {
		return payload, err
	}

	return payload, nil
}

func parseRSAPrivateKeyFromPEM(privateKeyPem string) (*ecdsa.PrivateKey, error) {
	block, _ := pem.Decode([]byte(privateKeyPem))
	if block == nil {
		return nil, fmt.Errorf("failed to parse PEM block")
	}

	// privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	privateKey, err := x509.ParseECPrivateKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	return privateKey, nil
}

// Function to create details required for user's login session"""
func BuildSession(ctx context.Context, db *sql.DB, userId string, clientId string, sessionEncryptionKey string, srpClientPublicKey string, srpServerPrivateKey string) (*schemas.Session, error) {
	// if platformClientId == nil {
	platformClientId := uuid.Must(uuid.NewRandom()).String()
	// }
	sessionId := uuid.Must(uuid.NewRandom()).String()

	// if sessionPrivateKey == nil {
	sessionPrivateKey, _ := GetSessionPrivateKey("ec")
	// }

	payload := SessionPayload{
		UserID:           userId,
		SessionID:        sessionId,
		ClientID:         clientId,
		PlatformClientID: platformClientId,
		Tier:             "pro",
	}

	sessionToken, err := GetSessionToken(payload, sessionPrivateKey, "ec")
	if err != nil {
		log.Fatal("Session token generation failed", err.Error())
		return nil, err
	}

	// fmt.Printf("Session token: %v", sessionToken)

	// Update user status and profile data
	session := &schemas.Session{
		ID:                   sessionId,
		UserId:               userId,
		SessionPrivateKey:    sessionPrivateKey,
		SessionToken:         sessionToken,
		ClientId:             clientId,
		PlatformClientId:     platformClientId,
		Activated:            false,
		SessionEncryptionKey: sessionEncryptionKey, //srp session key
		SrpServerPrivateKey:  srpServerPrivateKey,
		SrpClientPublicKey:   srpClientPublicKey,
	}
	crud.CreateSession(ctx, db, session)

	return session, nil
}

func GetCurrentUser(c *fiber.Ctx, ctx context.Context, db *sql.DB, sessionId string, sessionToken string, userId string) (string, error) {
	session, err := crud.GetSession(ctx, db, sessionId)

	if userId == "" {
		return userId, fmt.Errorf("User id missing")
	}

	if sessionId == "" {
		return userId, fmt.Errorf("Session Id missing")
	}

	if sessionToken == "" {
		return userId, fmt.Errorf("Session token missing")
	}

	if err == nil { // A valid session is found
		if session.ID != sessionId {
			return userId, fmt.Errorf("Invalid Session. Please login again.")
		}

		if session.SessionToken != sessionToken {
			return userId, fmt.Errorf("Invalid Session Token. Token has expired or is inactive.")
		}

		if time.Now().UTC().After(session.ExpiryAt) {
			fmt.Printf("time.Now().UTC().After(session.ExpiryAt) got triggered!!!\n")

			_, err = crud.ExpireActiveSessions(ctx, db, session.PlatformClientId, sessionId)
			if err != nil {
				log.Fatal("Session Activation not successful", err.Error())
				return userId, fmt.Errorf("Session Activation not successful")
			}
			c.ClearCookie("sessionToken")
			c.ClearCookie("sessionId")
			c.ClearCookie("userId")
		}
	} else { // No session found
		if err != nil {
			return userId, err
		}
	}
	return userId, nil
}
