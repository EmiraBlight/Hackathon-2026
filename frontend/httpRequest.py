import requests

def ping():
    return requests.get("http://10.109.206.111:2026/ping").json()["message"] == "pong"

def player2Connect(gameCode: str):
    payload = {"id" : gameCode}
    return requests.get("http://10.109.206.111:2026/join", params=payload).json()

def createRoom(gameCode: str):
    payload = {"id" : gameCode}
    return requests.get("http://10.109.206.111:2026/create", params=payload).json()

def getGame(gameCode: str, player: str):
    payload = {"id" : gameCode, "player" : player}
    return requests.get("http://10.109.206.111:2026/getGame", params=payload).json()

def submitAnswer(gameCode: str, player: str, answer: str):
    payload = {"id" : gameCode, "player" : player, "answer" : answer}
    return requests.get("http://10.109.206.111:2026/submit", params=payload).json()