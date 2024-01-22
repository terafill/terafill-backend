package crud

import (
	"context"
	"database/sql"
	"fmt"
)

func CreateEncryptionKey(ctx context.Context, db *sql.DB, itemId string, userId string, encryptedEncryptionKey string) error {
	_, err := db.ExecContext(ctx, "INSERT INTO encryption_keys (item_id, user_id, encrypted_encryption_key) VALUES (?, ?, ?)",
		itemId,
		userId,
		encryptedEncryptionKey,
	)
	if err != nil {
		return fmt.Errorf("CreateEncryptionKey: %v", err)
	}
	return nil
}
