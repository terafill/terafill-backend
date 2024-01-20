package crud

import (
	"context"
	"database/sql"
	"fmt"

	"terafill.com/m/server/schemas"
)

func GetSrpData(ctx context.Context, db *sql.DB, userId string) (*schemas.SRPData, error) {
	var srpData schemas.SRPData

	row := db.QueryRowContext(ctx, "SELECT user_id, verifier, salt FROM srp_data WHERE user_id = ?", userId)
	if err := row.Scan(&srpData.UserID, &srpData.Verifier, &srpData.Salt); err != nil {
		if err == sql.ErrNoRows {
			return &srpData, fmt.Errorf("GetSrpData %v: no such user found", userId)
		}
		return &srpData, fmt.Errorf("GetSrpData %v: %v", userId, err)
	}
	return &srpData, nil
}

func CreateSrpData(ctx context.Context, db *sql.DB, salt string, verifier string, userId string) error {
	_, err := db.ExecContext(ctx, "INSERT INTO srp_data (user_id, verifier, salt) VALUES (?, ?, ?)", userId, verifier, salt)
	if err != nil {
		return fmt.Errorf("CreateSrpData: %v", err)
	}
	return nil
}
