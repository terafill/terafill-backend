package crud

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/google/uuid"
	"terafill.com/m/server/schemas"
)

func GetVault(ctx context.Context, db *sql.DB, userId string, vaultId string) (*schemas.Vault, error) {
	var vault schemas.Vault

	row := db.QueryRowContext(ctx, "SELECT id, name, description, user_id, created_at, tags, is_default FROM vaults WHERE user_id = ? and vault_id = ?", userId, vaultId)
	if err := row.Scan(&vault.ID, &vault.Name, &vault.Description, &vault.UserID, &vault.CreatedAt, &vault.Tags, &vault.IsDefault); err != nil {
		if err == sql.ErrNoRows {
			return &vault, fmt.Errorf("GetVault %v: no such vault found", vaultId)
		}
		return &vault, fmt.Errorf("GetVault %v: %v", userId, err)
	}
	return &vault, nil
}

func CreateVault(ctx context.Context, db *sql.DB, vault *schemas.Vault) error {
	vaultId := uuid.Must(uuid.NewRandom()).String()
	tags, err := json.Marshal(vault.Tags)
	_, err = db.ExecContext(ctx, "INSERT INTO vaults (id, name, description, user_id, tags, is_default) VALUES (?, ?, ?, ?, ?, ?)",
		vaultId,
		vault.Name,
		vault.Description,
		vault.UserID,
		string(tags),
		vault.IsDefault,
	)
	if err != nil {
		return fmt.Errorf("CreateVault: %v", err)
	}
	return nil
}
