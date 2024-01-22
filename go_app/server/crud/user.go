package crud

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"

	"terafill.com/m/server/schemas"
)

// albumByID queries for the album with the specified ID.
func GetUserByEmail(ctx context.Context, db *sql.DB, email string) (*schemas.User, error) {
	// An album to hold data from the returned row.
	var user schemas.User

	row := db.QueryRowContext(ctx, "SELECT id, created_at, status FROM users WHERE email = ?", email)
	if err := row.Scan(&user.ID, &user.CreatedAt, &user.Status); err != nil {
		if err == sql.ErrNoRows {
			return &user, fmt.Errorf("getUserByEmail %v: no such user found", email)
		}
		return &user, fmt.Errorf("getUserByEmail %v: %v", email, err)
	}
	return &user, nil
}

func CreateUser(ctx context.Context, db *sql.DB, user *schemas.User) (*schemas.User, error) {
	userId := uuid.Must(uuid.NewRandom()).String()

	_, err := db.ExecContext(ctx, "INSERT INTO users (email, id, status) VALUES (?, ?, ?)", user.Email, userId, user.Status)
	if err != nil {
		return nil, fmt.Errorf("CreateUser: %v", err)
	}

	user, err = GetUserByEmail(ctx, db, user.Email)
	if err != nil {
		return nil, fmt.Errorf("CreateUser: %v", err)
	}

	return user, nil
}

func UpdateUser(ctx context.Context, db *sql.DB, updatedUser *schemas.User) (bool, error) {

	// fmt.Printf("New updated user is: %v", updatedUser)

	_, err := db.ExecContext(
		ctx, "UPDATE users SET status=?, email_verification_code=?;", updatedUser.Status, updatedUser.EmailVerificationCode)
	if err != nil {
		return false, fmt.Errorf("UpdateUser: %v", err)
	}

	return true, nil
}
