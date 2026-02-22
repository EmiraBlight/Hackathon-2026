package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

var db *pgxpool.Pool

func startGame(c *gin.Context) {
	id := c.Query("id")

	if !gameReady(id) {
		c.JSON(http.StatusBadRequest, gin.H{"status": "Game not ready yet!"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "Game ready"})

}

func gameReady(id string) bool {
	var count int
	err := db.QueryRow(context.Background(),
		`SELECT COUNT(*) FROM sessions WHERE id = $1`,
		id).Scan(&count)

	if err != nil || count < 1 {
		return false
	}
	var hasfilled bool
	err = db.QueryRow(context.Background(),
		`SELECT (
    (p1_a1 <> '')::int +
    (p1_a2 <> '')::int +
    (p1_a3 <> '')::int +
    (p2_a1 <> '')::int +
    (p2_a2 <> '')::int +
    (p2_a3 <> '')::int
    ) >= 4
	FROM sessions
	WHERE id = $1`,
		id,
	).Scan(&hasfilled)

	if err != nil {
		return false
	}

	return hasfilled

}

func player2Connect(c *gin.Context) {
	id := c.Query("id")
	var count int
	err := db.QueryRow(context.Background(),
		`SELECT COUNT(*) FROM sessions WHERE id = $1`,
		id).Scan(&count)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"result": "error counting"})
		return
	}

	if count < 1 {
		c.JSON(http.StatusNotFound, gin.H{"result": "Room not found"})
		return
	}

	_, err = db.Exec(context.Background(),
		`UPDATE sessions SET p2_connect_status=true WHERE id=$1`,
		id,
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"result": "error updating db"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"result": "Game joined"})

}

func create_room(c *gin.Context) {
	id := c.Query("id")
	_, err := db.Exec(context.Background(),
		`INSERT INTO sessions (id,p2_connect_status) VALUES  ($1,$2)`,
		id,
		false,
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"result": "failed to create room"})
	}
	c.JSON(http.StatusOK, gin.H{"result": "Room created"})

}

func isp2(id string) bool {
	var isConn bool

	err := db.QueryRow(
		context.Background(),
		`SELECT p2_connect_status WHERE id=$1`,
		id,
	).Scan(&isConn)

	if err != nil {
		return false
	}

	return isConn

}

func dba(c *gin.Context) {
	var id string
	err := db.QueryRow(
		context.Background(),
		`SELECT id FROM sessions;`,
	).Scan(&id)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"err": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"result": id})
}

func ping(c *gin.Context) {
	c.JSON(200, gin.H{"message": "pong"})
}

func main() {
	e := godotenv.Load() //load enviorment variables from .env file
	if e != nil {
		log.Fatalf("Failed to load .env file : %s", e)
	}
	password := os.Getenv("DB_PASS")
	dbURL := fmt.Sprintf("postgres://postgres:%s@localhost:5432/hack_db", password)
	var err error
	db, err = pgxpool.New(context.Background(), dbURL)

	if err != nil {
		log.Fatalf("Failed to connect to db: %s", err)
	}

	router := gin.Default()

	router.GET("/ping", ping)
	router.GET("/id", dba)
	router.GET("/join", player2Connect)
	router.GET("start", startGame)
	router.Run(":2026")
}
