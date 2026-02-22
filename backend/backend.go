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

	"google.golang.org/genai"
)

var db *pgxpool.Pool

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

//the player's range is 1-2, and questPos' range is 1-3
func fetchAndInsertAnswers(id string, player int, questPos int, questStr string) {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, nil)
	if err!=nil { log.Fatal(err) }
	aiResponse, err := client.Models.GenerateContent(
		ctx,
		"gemma-3-1b-it",
		genai.Text("%s", questStr),
		nil,
	)
	if err!=nil { log.Fatal(err) }
	switch player {
	case 1:
		switch questPos {
			case 1:
				err := db.Exec(`UPDATE sessions SET p1_a1=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			case 2:
				err := db.Exec(`UPDATE sessions SET p1_a2=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			case 3:
				err := db.Exec(`UPDATE sessions SET p1_a3=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			default:
				log.Fatal(questPos)
		}
	case 2:
		switch questPos {
			case 1:
				err := db.Exec(`UPDATE sessions SET p2_a1=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			case 2:
				err := db.Exec(`UPDATE sessions SET p2_a2=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			case 3:
				err := db.Exec(`UPDATE sessions SET p2_a3=$1 WHERE id=$2`, aiResponse.Text(), id)
				if err!=nil { log.Fatal(err) }
			default:
				log.Fatal(questPos)
		}
	default:
		log.Fatal(player)
	}
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
	router.Run(":2026")
}
