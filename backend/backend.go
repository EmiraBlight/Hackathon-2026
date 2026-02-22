package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"math/rand"
	"encoding/json"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"

	"google.golang.org/genai"
)

type Questions struct {
	QuestionList []string `json:"questions"`
}

var db *pgxpool.Pool

func ask(c *gin.Context) {
	id := c.Query("id")
	p := c.Query("p")
	q := c.Query("q")
	s := c.Query("s")

	player, _ := strconv.Atoi(p)
	question, _ := strconv.Atoi(q)

	fetchAndInsertAnswers(id, player, question, s)

}

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

//player's range is 1-2, questPos 1-3
func questionGenerator(id string, player int, questPos int) {
	byteValue, err := os.ReadFile("questions.json")
	if err!=nil { log.Fatal(err) }
	var questions Questions
	json.Unmarshal([]byte(byteValue), &questions)
	playerQuestionPair := `p`+string(player)+`_q`+string(questPos)
	questStr := questions.QuestionList[rand.Intn(55)]
	_, err = db.Exec(
		context.Background(),
		`UPDATE sessions SET $1=$2 WHERE id=$3`, playerQuestionPair, questStr, id)
	if err != nil {	log.Fatal(err) }
	fetchAndInsertAnswers(id, player, questPos, questStr)
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

	p1_rand1 := rand.Intn(2)+1
	p1_rand2 := p1_rand1
	for (p1_rand1==p1_rand2) { p1_rand2=rand.Intn(2)+1 }
	p2_rand1 := rand.Intn(2)+1
	p2_rand2 := p2_rand1
	for (p2_rand1==p2_rand2) { p2_rand2=rand.Intn(2)+1 }
	go questionGenerator(id, 1, p1_rand1)
	go questionGenerator(id, 1, p1_rand2)
	go questionGenerator(id, 2, p2_rand1)
	go questionGenerator(id, 2, p2_rand2)
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

// the player's range is 1-2, and questPos' range is 1-3
func fetchAndInsertAnswers(id string, player int, questPos int, questStr string) {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}
	aiResponse, err := client.Models.GenerateContent(
		ctx,
		"gemma-3-1b-it",
		genai.Text(questStr+" (keep the answer under 2 sentences)"),
		nil,
	)
	if err != nil {
		log.Fatal(err)
	}
	switch player {
	case 1:
		switch questPos {
		case 1:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p1_a1=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
		case 2:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p1_a2=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
		case 3:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p1_a3=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
		default:
			log.Fatal(questPos)
		}
	case 2:
		switch questPos {
		case 1:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p2_a1=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
		case 2:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p2_a2=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
		case 3:
			_, err := db.Exec(
				context.Background(),
				`UPDATE sessions SET p2_a3=$1 WHERE id=$2`, aiResponse.Text(), id)
			if err != nil {
				log.Fatal(err)
			}
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
	router.GET("/start", startGame)
	router.GET("/ai", ask)
	router.Run(":2026")
}
