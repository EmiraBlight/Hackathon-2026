package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"

	"google.golang.org/genai"
)

type Questions struct {
	QuestionList []string `json:"questions"`
}

var db *pgxpool.Pool

func funcSubmitAnswer(c *gin.Context) {
	id := c.Query("id")
	player := c.Query("player")
	answer := c.Query("answer")
	var q int
	p := "p" + player + "_real"

	query := fmt.Sprintf("SELECT %s FROM sessions WHERE id=$1", p)

	err := db.QueryRow(context.Background(),
		query,
		id,
	).Scan(&q)

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error(), "q": p})
		return
	}

	real := "p" + player + "_a" + strconv.Itoa(q)
	updateQuery := fmt.Sprintf("UPDATE sessions SET %s=$1 WHERE id=$2", real)
	_, err = db.Exec(context.Background(), updateQuery, answer, id)

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error(), "q": updateQuery})
		return
	}

	c.JSON(http.StatusOK, gin.H{"result": "Answer submitted"})

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

// player's range is 1-2, questPos 1-3
func questionGenerator(id string, player int, questPos int, real bool) {
	byteValue, err := os.ReadFile("questions.json")
	if err != nil {
		log.Fatal(err)
	}
	var questions Questions
	json.Unmarshal([]byte(byteValue), &questions)
	playerQuestionPair := "p" + strconv.Itoa(player) + "_q" + strconv.Itoa(questPos)
	playerRealPair := "p" + strconv.Itoa(player) + "_real"
	questStr := questions.QuestionList[rand.Intn(55)]
	query := fmt.Sprintf("UPDATE sessions SET %s=$1 WHERE id=$2", playerQuestionPair)
	queryReal := fmt.Sprintf("UPDATE sessions SET %s=%s,%s=$1 WHERE id=$2", playerRealPair, strconv.Itoa(questPos), playerQuestionPair)
	_, err = db.Exec(
		context.Background(),
		query, questStr, id)
	if err != nil {
		log.Fatal(err)
	}
	if !real {
		fetchAndInsertAnswers(id, player, questPos, questStr)
	} else {
		_, err := db.Exec(
			context.Background(),
			queryReal, questStr, id)
		if err != nil {
			log.Fatal(err)
		}
	}
}

func returnQNAsOfPlayer(c *gin.Context) {
	id := c.Query("id")
	p := c.Query("player")
	var hasfilled bool
	err := db.QueryRow(context.Background(),
		`SELECT (
    (p1_a1 <> '')::int +
    (p1_a2 <> '')::int +
    (p1_a3 <> '')::int +
    (p2_a1 <> '')::int +
    (p2_a2 <> '')::int +
    (p2_a3 <> '')::int
    ) = 6
	FROM sessions
	WHERE id = $1`,
		id,
	).Scan(&hasfilled)

	if !hasfilled || err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"status": "Not ready"})
		return
	}

	player, _ := strconv.Atoi(p)
	returnValue := make(map[string]string)
	var queryRowValue string
	switch player {
	case 1:
		for i := 1; i < 4; i++ {
			query := fmt.Sprintf("SELECT p2_q" + strconv.Itoa(i) + " FROM sessions WHERE id=$1")
			err := db.QueryRow(context.Background(), query, id).Scan(&queryRowValue)
			if err != nil {
				log.Print(query)
				log.Fatal(err)
			}
			returnValue["q"+strconv.Itoa(i)] = queryRowValue
		}
		for i := 1; i < 4; i++ {
			query := fmt.Sprintf("SELECT p2_a" + strconv.Itoa(i) + " FROM sessions WHERE id=$1")
			err := db.QueryRow(context.Background(), query, id).Scan(&queryRowValue)
			if err != nil {
				log.Fatal(err)
			}
			returnValue["a"+strconv.Itoa(i)] = queryRowValue
		}
		err := db.QueryRow(context.Background(), `SELECT p2_real FROM sessions WHERE id=$1`, id).Scan(&queryRowValue)
		if err != nil {
			log.Fatal(err)
		}
		returnValue["real"] = queryRowValue
	case 2:
		for i := 1; i < 4; i++ {
			query := fmt.Sprintf("SELECT p1_q" + strconv.Itoa(i) + " FROM sessions WHERE id=$1")
			err := db.QueryRow(context.Background(), query, id).Scan(&queryRowValue)
			if err != nil {
				log.Fatal(err)
			}
			returnValue["q"+strconv.Itoa(i)] = queryRowValue
		}
		for i := 1; i < 4; i++ {
			query := fmt.Sprintf("SELECT p1_a" + strconv.Itoa(i) + " FROM sessions WHERE id=$1")
			err := db.QueryRow(context.Background(), query, id).Scan(&queryRowValue)
			if err != nil {
				log.Fatal(err)
			}
			returnValue["a"+strconv.Itoa(i)] = queryRowValue
		}
		err := db.QueryRow(context.Background(), `SELECT p1_real FROM sessions WHERE id=$1`, id).Scan(&queryRowValue)
		if err != nil {
			log.Fatal(err)
		}
		returnValue["real"] = queryRowValue
	}
	c.JSON(http.StatusOK, returnValue)
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

	p1_rand1 := rand.Intn(3) + 1
	p1_rand2 := p1_rand1
	p1_real := p1_rand1
	for p1_rand1 == p1_rand2 {
		p1_rand2 = rand.Intn(3) + 1
	}
	for p1_real == p1_rand1 || p1_real == p1_rand2 {
		p1_real = rand.Intn(3) + 1
	}
	p2_rand1 := rand.Intn(3) + 1
	p2_rand2 := p2_rand1
	p2_real := p2_rand1
	for p2_rand1 == p2_rand2 {
		p2_rand2 = rand.Intn(3) + 1
	}
	for p2_real == p2_rand1 || p2_real == p2_rand2 {
		p2_real = rand.Intn(3) + 1
	}
	go questionGenerator(id, 1, p1_real, true)
	go questionGenerator(id, 1, p1_rand1, false)
	go questionGenerator(id, 1, p1_rand2, false)
	go questionGenerator(id, 2, p2_real, true)
	go questionGenerator(id, 2, p2_rand1, false)
	go questionGenerator(id, 2, p2_rand2, false)
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

type PlayerQA struct {
	Q1 string `json:"q1"`
	A1 string `json:"a1"`
	Q2 string `json:"q2"`
	A2 string `json:"a2"`
	Q3 string `json:"q3"`
	A3 string `json:"a3"`
}

func getGame(c *gin.Context) {
	id := c.Query("id")
	player := c.Query("player")

	if id == "" || player == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "missing id or player"})
		return
	}

	if !gameReady(id) {
		c.JSON(http.StatusInternalServerError, gin.H{"result": "game not ready"})
		return
	}

	var query string

	switch player {
	case "1":
		query = `
				SELECT p1_q1, p1_a1,
				       p1_q2, p1_a2,
				       p1_q3, p1_a3
				FROM sessions
				WHERE id = $1
			`
	case "2":
		query = `
				SELECT p2_q1, p2_a1,
				       p2_q2, p2_a2,
				       p2_q3, p2_a3
				FROM sessions
				WHERE id = $1
			`
	default:
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid player"})
		return
	}

	var result PlayerQA

	err := db.QueryRow(
		c.Request.Context(),
		query,
		id,
	).Scan(
		&result.Q1, &result.A1,
		&result.Q2, &result.A2,
		&result.Q3, &result.A3,
	)

	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			c.JSON(http.StatusNotFound, gin.H{"error": "game not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
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

	defer db.Close()

	router := gin.Default()

	router.GET("/join", player2Connect)
	router.GET("/start", startGame)
	router.GET("/getGame", getGame)
	router.GET("/create", create_room)
	router.GET("/submit", funcSubmitAnswer)
	router.GET("/qnaOfPlayer", returnQNAsOfPlayer)
	router.Run(":2026")
}
