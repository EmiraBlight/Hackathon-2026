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
	router.Run(":2026")
}
