package main

import (
	"context"
	"database/sql"
	"encoding/hex"
	"fmt"
	"log"
	"math/big"
	"math/rand"
	"strconv"

	"github.com/1Password/srp"
	"github.com/aws/aws-sdk-go/service/ses"
	"github.com/go-sql-driver/mysql"
	"github.com/gofiber/fiber/v2"
	"terafill.com/m/server/crud"
	"terafill.com/m/server/schemas"
	"terafill.com/m/server/utils"
)

var db *sql.DB

// type SignupRequest struct {
// 	email string
// }

type SignupConfirmationRequest struct {
	Email            string
	VerificationCode string
	// firstName               string
	// lastName                string
	Verifier                string
	Salt                    string
	EncryptedKeyWrappingKey string `json:"encrypted_key_wrapping_key"`
}

type SaltRequest struct {
	Email string
}

func arrayFind(arr []string, el string) (int, bool, error) {

	for i, v := range arr {
		if v == el {
			// Found the value at index i
			return i, true, nil
		}
	}
	return -1, false, nil
}

func SetupDB() *sql.DB {
	// Capture connection properties.
	cfg := mysql.Config{
		User:      "go_user",     //os.Getenv("DBUSER"),
		Passwd:    "Go_pass_123", //os.Getenv("DBPASS"),
		Net:       "tcp",
		Addr:      "127.0.0.1:3306",
		DBName:    "terafill",
		ParseTime: true,
	}
	// Get a database handle.
	var err error
	db, err = sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		log.Fatal(err)
	}

	pingErr := db.Ping()
	if pingErr != nil {
		log.Fatal(pingErr)
	}
	fmt.Println("Connected!")

	return db
}

func SetupApp(db *sql.DB, sesClient *ses.SES) *fiber.App {
	app := fiber.New()

	app.Get("/", func(c *fiber.Ctx) error {
		// return c.SendString("Hello, World 👋!")
		return c.SendString("{\"msg\":\"Hello this is a test message\"}")
	})

	app.Post("/auth/signup", func(c *fiber.Ctx) error {

		var ctx context.Context = c.Context()

		// Get a Tx for making transaction requests.
		tx, err := db.BeginTx(ctx, nil)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}
		// Defer a rollback in case anything fails.
		defer tx.Rollback()

		user := new(schemas.User)
		c.BodyParser(&user)

		email := user.Email
		fmt.Printf("Email to be signed up: %v", email)
		var userType string = ""
		user, err = crud.GetUserByEmail(ctx, db, email)
		fmt.Println("User found is", user, err)
		if err != nil { // new user
			userData := schemas.User{
				Email:  email,
				Status: "unconfirmed",
			}
			user, err = crud.CreateUser(ctx, db, &userData)
			userType = "new"
		} else {
			userType = user.Status
		}

		fmt.Println("userType ", userType)

		q := c.Queries()

		// var updatedUser schemas.User

		if _, ok, _ := arrayFind([]string{
			"new",
			"need_sign_up",
			"unconfirmed",
		}, userType); ok == true { // send verification code
			verificationCode := rand.Intn(900000) + 100000

			mock, _ := strconv.ParseBool(q["mock"])

			fmt.Printf("Verification will be sent: %d\n", verificationCode)

			var awsClient *utils.AWSClient

			if mock != true {
				utils.SendVerificationCode(awsClient, sesClient, email, verificationCode)
			} else {
				fmt.Print("SendVerificationCode not triggered")
			}

			user.EmailVerificationCode = verificationCode
			user.Status = "unconfirmed"

			// fmt.Println("Updated user", updatedUser, user)
			ok, err = crud.UpdateUser(ctx, db, user)
			fmt.Println("err", err)
			if ok != true {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"err": err.Error(),
				})
			}
		} else if userType == "confirmed" {
			return c.Status(fiber.StatusConflict).JSON(fiber.Map{
				"err": "Email is already registered",
			})
		} else if userType == "deactivated" {
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"err": "Email is deactivated. Please contact support for resolution.",
			})
		}

		// Commit the transaction.
		if err = tx.Commit(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		return c.Status(fiber.StatusNoContent).JSON("")
	})

	app.Post("/auth/signup/confirm", func(c *fiber.Ctx) error {

		var ctx context.Context = c.Context()

		// Get a Tx for making transaction requests.
		tx, err := db.BeginTx(ctx, nil)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}
		// Defer a rollback in case anything fails.
		defer tx.Rollback()

		confirmationRequest := new(SignupConfirmationRequest)
		c.BodyParser(&confirmationRequest)

		email := confirmationRequest.Email
		fmt.Printf("Email to be signed up: %v", email)
		// var userType string = ""
		user, err := crud.GetUserByEmail(ctx, db, email)
		fmt.Println("User found is", user, err)
		if err != nil { // new user
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"err": "User not found.",
			})
		}

		fmt.Println("userType ", user.Status)

		user.Status = "confirmed"

		ok, err := crud.UpdateUser(ctx, db, user)
		fmt.Println("err", err)
		if ok != true {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// Store salt and verifier
		err = crud.CreateSrpData(ctx, db, confirmationRequest.Salt, confirmationRequest.Verifier, user.ID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// fmt.Println("confirmationRequest: ", confirmationRequest)

		// Store salt and verifier
		err = crud.CreateKeyWrappingKey(
			ctx,
			db,
			user.ID,
			confirmationRequest.EncryptedKeyWrappingKey,
		)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// Create deafult vault
		vault := &schemas.Vault{
			Name:      "Default Vault",
			IsDefault: true,
			UserID:    user.ID,
		}

		err = crud.CreateVault(ctx, db, vault)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// Commit the transaction.
		if err = tx.Commit(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		return c.Status(fiber.StatusNoContent).JSON("")
	})

	app.Post("/auth/salt", func(c *fiber.Ctx) error {

		var ctx context.Context = c.Context()

		// Get a Tx for making transaction requests.
		tx, err := db.BeginTx(ctx, nil)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}
		// Defer a rollback in case anything fails.
		defer tx.Rollback()

		saltRequest := new(SaltRequest)
		c.BodyParser(&saltRequest)

		email := saltRequest.Email
		fmt.Printf("Email requested is: %v", email)

		user, err := crud.GetUserByEmail(ctx, db, email)
		fmt.Println("User found is", user, err)
		if err != nil { // User not found
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"err": "User not found.",
			})
		}

		srpData, err := crud.GetSrpData(ctx, db, user.ID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// Commit the transaction.
		if err = tx.Commit(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"Salt": srpData.Salt,
		})
	})

	app.Post("/auth/login", func(c *fiber.Ctx) error {

		var ctx context.Context = c.Context()

		// Get a Tx for making transaction requests.
		tx, err := db.BeginTx(ctx, nil)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}
		// Defer a rollback in case anything fails.
		defer tx.Rollback()

		loginRequest := new(struct {
			Email           string
			ClientPublicKey string
		})
		c.BodyParser(&loginRequest)

		email := loginRequest.Email
		clientPublicKey := loginRequest.ClientPublicKey
		fmt.Printf("Email requested is: %v\n", email)
		fmt.Printf("ClientPublicKey requested is: %v\n", clientPublicKey)

		user, err := crud.GetUserByEmail(ctx, db, email)
		fmt.Println("User found is", user, err)
		if err != nil { // User not found
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"err": "User not found.",
			})
		}
		userId := user.ID

		srpData, err := crud.GetSrpData(ctx, db, user.ID)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		group := srp.RFC5054Group2048

		v_hex := srpData.Verifier
		salt_hex := srpData.Salt
		A_hex := clientPublicKey

		v := new(big.Int)      // create new *big.Int object (allocates the memory for it)
		v.SetString(v_hex, 16) // convert to *big.Int from base 16 string

		// salt := new(big.Int)
		// salt.SetString(salt_hex, 16)

		A := new(big.Int)
		A.SetString(A_hex, 16)

		server := srp.NewServerStd(srp.KnownGroups[group], v)
		if server == nil {
			log.Fatal("Couldn't set up server")
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"err": "Couldn't set up server",
			})
		}

		fmt.Println("Server was initialized!")

		if err = server.SetOthersPublic(A); err != nil {
			log.Fatal(err)
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"err": "Couldn't set up client's public key",
			})
		}

		fmt.Println("Client's public key was setup!")

		var B *big.Int

		if B = server.EphemeralPublic(); B == nil {
			log.Fatal("server couldn't make B")
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"err": "Server couldn't make server's public key",
			})
		}

		B_hex := hex.EncodeToString(B.Bytes())
		fmt.Println("Server's public key was generated!")

		// server can now make the key.
		sessionKey, err := server.Key()
		if err != nil || sessionKey == nil {
			log.Fatalf("something went wrong making server key: %s\n", err)
			return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"err": "Couldn't generate common session key",
			})
		}

		sessionKey_hex := hex.EncodeToString(sessionKey)

		headers := c.GetReqHeaders()
		fmt.Println("headers", headers)
		clientId := headers["Client-Id"][0]
		serverPrivateKey := server.EphemeralPrivate()
		serverPrivateKey_hex := hex.EncodeToString(serverPrivateKey.Bytes())

		session, err := utils.BuildSession(
			ctx,
			db,
			userId,
			clientId,
			sessionKey_hex,
			clientPublicKey,
			serverPrivateKey_hex,
		)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		// Commit the transaction.
		if err = tx.Commit(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		c.Cookie(&fiber.Cookie{
			Name:  "userId",
			Value: userId,
		})
		c.Cookie(&fiber.Cookie{
			Name:  "sessionId",
			Value: session.ID,
		})
		c.Cookie(&fiber.Cookie{
			Name:  "platformClientId",
			Value: session.PlatformClientId,
		})

		return c.Status(fiber.StatusOK).JSON(&fiber.Map{
			"salt":             salt_hex,
			"serverPublicKey":  B_hex,
			"sessionId":        session.ID,
			"platformClientId": session.PlatformClientId,
			"userId":           userId,
		})
	})

	app.Post("/auth/login/confirm", func(c *fiber.Ctx) error {

		var ctx context.Context = c.Context()

		// Get a Tx for making transaction requests.
		tx, err := db.BeginTx(ctx, nil)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}
		// Defer a rollback in case anything fails.
		defer tx.Rollback()

		loginConfirmationRequest := new(struct {
			Email       string
			ClientProof string
		})
		c.BodyParser(&loginConfirmationRequest)

		email := loginConfirmationRequest.Email
		clientProof := loginConfirmationRequest.ClientProof
		fmt.Printf("Email requested is: %v\n", email)
		fmt.Printf("Client Proof requested is: %v\n", clientProof)

		user, err := crud.GetUserByEmail(ctx, db, email)
		fmt.Println("User found is", user, err)
		if err != nil { // User not found
			return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
				"err": "User not found.",
			})
		}
		userId := user.ID

		cookies := new(struct {
			SessionId string `cookie:"sessionId"`
		})
		c.CookieParser(cookies)

		sessionId := cookies.SessionId

		fmt.Printf("Session Id found from cookies %v\n", sessionId)

		session, err := crud.GetSession(ctx, db, sessionId)

		var serverProof_hex string

		if err == nil { // A valid session is found
			srpData, err := crud.GetSrpData(ctx, db, userId)
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"err": err.Error(),
				})
			}

			group := srp.RFC5054Group2048

			A_hex := session.SrpClientPublicKey
			A := new(big.Int)
			A.SetString(A_hex, 16)

			v_hex := srpData.Verifier
			v := new(big.Int)      // create new *big.Int object (allocates the memory for it)
			v.SetString(v_hex, 16) // convert to *big.Int from base 16 string

			salt_hex := srpData.Salt

			server := srp.NewServerStd(srp.KnownGroups[group], v)
			if server == nil {
				log.Fatal("Couldn't set up server")
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Couldn't set up server",
				})
			}

			fmt.Println("Server was initialized!")
			// fmt.Println("session.SrpClientPublicKey", session.SrpClientPublicKey)
			// fmt.Println("A: ", A)
			// fmt.Println("V: ", v)

			if err = server.SetOthersPublic(A); err != nil {
				log.Fatal(err)
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Couldn't set up client's public key",
				})
			}

			fmt.Println("Client's public key was setup!")

			mySecret_hex := session.SrpServerPrivateKey
			fmt.Printf("Try mySecret_hex: %v\n", mySecret_hex)
			mySecret := new(big.Int)
			mySecret.SetString(mySecret_hex, 16)
			err = server.SetMySecret(mySecret)
			if err != nil {
				log.Fatal("server couldn't set Server private key")
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Server couldn't make Server private key",
				})
			}

			fmt.Print("Server private key was setup!\n")

			var B *big.Int

			if B = server.EphemeralPublic(); B == nil {
				log.Fatal("server couldn't make B")
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Server couldn't make server's public key",
				})
			}

			// B_hex := hex.EncodeToString(B.Bytes())
			fmt.Println("Server's public key was generated!")

			// server can now make the key.
			sessionKey, err := server.Key()
			if err != nil || sessionKey == nil {
				log.Fatalf("something went wrong making server key: %s\n", err)
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Couldn't generate common session key",
				})
			}

			salt_bytes, _ := hex.DecodeString(salt_hex)
			clientProof_bytes, _ := hex.DecodeString(clientProof)

			// client sends its proof to the server. Server checks
			if !server.GoodClientProof(salt_bytes, email, clientProof_bytes) {
				log.Fatal("bad proof from client")
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Invalid email or password",
				})
			}

			serverProof, err := server.ServerProof()
			if err != nil {
				log.Fatal("Failed to generate server proof", err)
				return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
					"err": "Invalid email or password",
				})
			}

			serverProof_hex = hex.EncodeToString(serverProof)

		} else { // No session found
			if err != nil {
				return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
					"err": err.Error(),
				})
			}
		}

		keyWrappingKey, err := crud.GetKeyWrappingKey(ctx, db, userId)

		_, err = crud.ExpireActiveSessions(ctx, db, session.PlatformClientId, sessionId)
		if err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": "Session Expiration not successful",
			})
		}

		_, err = crud.ActivateSession(ctx, db, sessionId)
		if err != nil {
			log.Fatal("Session Activation not successful", err.Error())
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": "Session Activation not successful",
			})
		}

		// Commit the transaction.
		if err = tx.Commit(); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"err": err.Error(),
			})
		}

		c.Cookie(&fiber.Cookie{
			Name:  "sessionToken",
			Value: session.SessionToken,
		})

		return c.Status(fiber.StatusOK).JSON(&fiber.Map{
			"serverProof":    serverProof_hex,
			"keyWrappingKey": keyWrappingKey.EncryptedPrivateKey,
			"sessionToken":   session.SessionToken,
		})
	})

	return app
}

func main() {
	sesClient := utils.SetupSES()  // Setup AWS SES
	db := SetupDB()                // Setup MySQL database
	app := SetupApp(db, sesClient) // Setup app
	app.Listen(":3000")            // Run app
	defer db.Close()
}
