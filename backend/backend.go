package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func ping(c *gin.Context) {
	c.JSON(200, gin.H{"message": "pong"})
}

func main() {

	e := godotenv.Load() //load enviorment variables from .env file
	if e != nil {
		log.Fatalf("Failed to load .env file : %s", e)
	}

	certFile := os.Getenv("CERT")
	keyFile := os.Getenv("KEY")

	router := gin.Default()
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*") //Enables cores
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type")
	})

	router.GET("/ping", ping)

	router.RunTLS(":2026", certFile, keyFile)

}
