package crud

import (
	"context"
	"database/sql"
	"fmt"

	"terafill.com/m/server/schemas"
)

func GetKeyWrappingKey(ctx context.Context, db *sql.DB, userId string) (*schemas.KeyWrappingKey, error) {
	var keyWrappingKey schemas.KeyWrappingKey

	row := db.QueryRowContext(ctx, "SELECT user_id, encrypted_private_key, public_key FROM key_wrapping_keys WHERE user_id = ?", userId)
	if err := row.Scan(&keyWrappingKey.UserID, &keyWrappingKey.EncryptedPrivateKey, &keyWrappingKey.PublicKey); err != nil {
		if err == sql.ErrNoRows {
			return &keyWrappingKey, fmt.Errorf("GetKeyWrappingKey %v: no such user found", userId)
		}
		return &keyWrappingKey, fmt.Errorf("GetKeyWrappingKey %v: %v", userId, err)
	}
	return &keyWrappingKey, nil
}

func CreateKeyWrappingKey(ctx context.Context, db *sql.DB, userId string, encryptedPrivateKey string) error {
	_, err := db.ExecContext(ctx, "INSERT INTO key_wrapping_keys (user_id, encrypted_private_key) VALUES (?, ?)", userId, encryptedPrivateKey)
	if err != nil {
		return fmt.Errorf("CreateKeyWrappingKey: %v", err)
	}
	return nil
}
