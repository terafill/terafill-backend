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

func GetVaultsByUserId(ctx context.Context, db *sql.DB, userId string) ([]schemas.Vault, error) {
	var vaults []schemas.Vault

	rows, err := db.QueryContext(ctx, "SELECT id, name, description, user_id, created_at, tags, is_default FROM vaults WHERE user_id = ?;", userId)
	if err != nil {
		return nil, fmt.Errorf("GetVaults %q: %v", userId, err)
	}

	defer rows.Close()

	for rows.Next() {
		var vault schemas.Vault
		var tags interface{}
		if err := rows.Scan(&vault.ID, &vault.Name, &vault.Description, &vault.UserID, &vault.CreatedAt, &tags, &vault.IsDefault); err != nil {
			return vaults, fmt.Errorf("GetVaults %v: %v", userId, err)
		}
		var tagsBytes = tags.([]byte)
		json.Unmarshal(tagsBytes, &vault.Tags)
		vaults = append(vaults, vault)
	}

	return vaults, nil
}

func CreateVault(ctx context.Context, db *sql.DB, vault *schemas.Vault) error {
	vault.ID = uuid.Must(uuid.NewRandom()).String()
	tags, err := json.Marshal(vault.Tags)
	_, err = db.ExecContext(ctx, "INSERT INTO vaults (id, name, description, user_id, tags, is_default) VALUES (?, ?, ?, ?, ?, ?)",
		vault.ID,
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

func UpdateVault(ctx context.Context, db *sql.DB, vault *schemas.Vault) error {
	tags, err := json.Marshal(vault.Tags)
	_, err = db.ExecContext(ctx, "UPDATE vaults set name=?, description=?, user_id=?, tags=?, is_default=? where id=?;",
		vault.Name,
		vault.Description,
		vault.UserID,
		string(tags),
		vault.IsDefault,
		vault.ID,
	)
	if err != nil {
		return fmt.Errorf("UpdateVault: %v", err)
	}
	return nil
}

func DeleteVault(ctx context.Context, db *sql.DB, vaultId string) error {
	_, err := db.ExecContext(ctx, "DELETE from vaults where id=?;",
		vaultId,
	)
	if err != nil {
		return fmt.Errorf("DeleteVault: %v", err)
	}
	return nil
}
