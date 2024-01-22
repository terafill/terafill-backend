package crud

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/google/uuid"
	"terafill.com/m/server/schemas"
)

// func GetVault(ctx context.Context, db *sql.DB, userId string, vaultId string) (*schemas.Vault, error) {
// 	var vault schemas.Vault

// 	row := db.QueryRowContext(ctx, "SELECT id, name, description, user_id, created_at, tags, is_default FROM vaults WHERE user_id = ? and vault_id = ?", userId, vaultId)
// 	if err := row.Scan(&vault.ID, &vault.Name, &vault.Description, &vault.UserID, &vault.CreatedAt, &vault.Tags, &vault.IsDefault); err != nil {
// 		if err == sql.ErrNoRows {
// 			return &vault, fmt.Errorf("GetVault %v: no such vault found", vaultId)
// 		}
// 		return &vault, fmt.Errorf("GetVault %v: %v", userId, err)
// 	}
// 	return &vault, nil
// }

func GetItemsFull(ctx context.Context, db *sql.DB, userId string, vaultId string) ([]schemas.Item, error) {
	var items []schemas.Item

	// Construct your SQL query
	query := `SELECT items.id, items.vault_id, items.user_id, title, description, username, password, website, tags, type, is_favorite, encryption_keys.encrypted_encryption_key
				FROM items
				JOIN encryption_keys ON encryption_keys.item_id = items.id AND encryption_keys.user_id = items.user_id
				WHERE items.vault_id = ? AND items.user_id = ?`

	// Execute the query
	rows, err := db.QueryContext(ctx, query, vaultId, userId)
	if err != nil {
		return items, fmt.Errorf("GetVaults userId-%v vaultId-%v: %v", userId, vaultId, err)
	}
	defer rows.Close()

	for rows.Next() {
		var item schemas.Item
		var encryptedKey schemas.EncryptionKey
		var tags interface{}

		// Scan the row into the Item and EncryptionKey structs
		if err := rows.Scan(
			&item.ID,
			&item.VaultID,
			&item.UserID,
			&item.Title,
			&item.Description,
			&item.Username,
			&item.Password,
			&item.Website,
			&tags,
			&item.Type,
			&item.IsFavorite,
			&encryptedKey.EncryptedEncryptionKey); err != nil {
			return nil, err
		}

		var tagsBytes = tags.([]byte)
		json.Unmarshal(tagsBytes, &item.Tags)
		// Process or add item to result slice as necessary
		items = append(items, item)
	}

	// Check for errors from iterating over rows
	if err = rows.Err(); err != nil {
		return items, fmt.Errorf("GetVaults userId-%v vaultId-%v: %v", userId, vaultId, err)
	}

	return items, nil
}

func CreateItem(ctx context.Context, db *sql.DB, item *schemas.Item) error {
	item.ID = uuid.Must(uuid.NewRandom()).String()
	tags, err := json.Marshal(item.Tags)
	_, err = db.ExecContext(ctx, "INSERT INTO items (id, vault_id, user_id, title, description, username, password, website, tags, type, is_favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		item.ID,
		item.VaultID,
		item.UserID,
		item.Title,
		item.Description,
		item.Username,
		item.Password,
		item.Website,
		string(tags),
		item.Type,
		item.IsFavorite,
	)
	if err != nil {
		return fmt.Errorf("CreateItem: %v", err)
	}
	return nil
}

func UpdateItem(ctx context.Context, db *sql.DB, item *schemas.Item) error {
	tags, err := json.Marshal(item.Tags)
	_, err = db.ExecContext(ctx, "UPDATE items set vault_id=?, title=?, description=?, username=?, password=?, website=?, tags=?, type=?, is_favorite=? where id=?",
		item.VaultID,
		item.Title,
		item.Description,
		item.Username,
		item.Password,
		item.Website,
		string(tags),
		item.Type,
		item.IsFavorite,
		item.ID,
	)

	if err != nil {
		return fmt.Errorf("UpdateItem: %v", err)
	}
	return nil
}

func DeleteItem(ctx context.Context, db *sql.DB, itemId string) error {
	_, err := db.ExecContext(ctx, "DELETE from items where id=?;", itemId)
	if err != nil {
		return fmt.Errorf("DeleteVault: %v", err)
	}
	return nil
}
