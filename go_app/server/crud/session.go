package crud

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"terafill.com/m/server/schemas"
)

func GetSession(ctx context.Context, db *sql.DB, sessionId string) (*schemas.Session, error) {
	var session schemas.Session

	row := db.QueryRowContext(ctx, "SELECT id, client_id, platform_client_id, expiry_at, session_token, user_id, activated, session_srp_client_public_key, session_srp_server_private_key FROM sessions WHERE id = ?", sessionId)
	if err := row.Scan(&session.ID, &session.ClientId, &session.PlatformClientId, &session.ExpiryAt, &session.SessionToken, &session.UserId, &session.Activated, &session.SrpClientPublicKey, &session.SrpServerPrivateKey); err != nil {
		if err == sql.ErrNoRows {
			return &session, fmt.Errorf("GetSession %v: no such session found", sessionId)
		}
		return &session, fmt.Errorf("GetSession %v: %v", sessionId, err)
	}
	return &session, nil
}

func CreateSession(ctx context.Context, db *sql.DB, session *schemas.Session) error {
	// Equivalent to Python's datetime.utcnow()
	created_at := time.Now().UTC()

	// Equivalent to datetime.utcnow() + timedelta(hours=2)
	expiry_at := time.Now().UTC().Add(time.Hour * 2)

	_, err := db.ExecContext(ctx, "INSERT INTO sessions (id, user_id, client_id, platform_client_id, client_type, created_at, expiry_at, session_private_key, session_srp_server_private_key, session_srp_client_public_key, session_token, session_encryption_key, activated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		session.ID,
		session.UserId,
		session.ClientId,
		session.PlatformClientId,
		session.ClientType,
		created_at,
		expiry_at,
		session.SessionPrivateKey,
		session.SrpServerPrivateKey,
		session.SrpClientPublicKey,
		session.SessionToken,
		session.SessionEncryptionKey,
		session.Activated,
	)
	if err != nil {
		return fmt.Errorf("CreateSession: %v", err)
	}
	return nil
}

func ExpireActiveSessions(ctx context.Context, db *sql.DB, platformClientId string, sessionId string) (bool, error) {

	_, err := db.ExecContext(
		ctx, "Delete from sessions where platform_client_id != ? and id != ?;", platformClientId, sessionId)
	if err != nil {
		return false, fmt.Errorf("ExpireActiveSessions: %v", err)
	}

	return true, nil
}

func ActivateSession(ctx context.Context, db *sql.DB, sessionId string) (bool, error) {

	_, err := db.ExecContext(
		ctx, "Update sessions set activated=true where id = ? ;", sessionId)
	if err != nil {
		return false, fmt.Errorf("ExpireActiveSessions: %v", err)
	}

	return true, nil
}
