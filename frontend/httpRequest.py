import requests

URL = "http://10.109.206.111:2026"

def ping():
    return requests.get(f"{URL}/ping").json()["message"] == "pong"

def player2Connect(gameCode: str):
    payload = {"id": gameCode}
    return requests.get(f"{URL}/join", params=payload).json()

def createRoom(gameCode: str):
    payload = {"id": gameCode}
    return requests.get(f"{URL}/create", params=payload).json()

def getGame(gameCode: str, player: str):
    payload = {"id": gameCode, "player": player}
    return requests.get(f"{URL}/getGame", params=payload).json()

def submitAnswer(gameCode: str, player: str, answer: str):
    payload = {"id": gameCode, "player": player, "answer": answer}
    return requests.get(f"{URL}/submit", params=payload).json()