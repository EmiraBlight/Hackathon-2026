import requests

URL = "http://10.109.206.111:2026"


def ping():
    return requests.get("http://10.109.206.111:2026/ping").json()["message"] == "pong"


def player2Connect(gameCode: str):
    payload = {"id": gameCode}
    return requests.get(URL + "/join", params=payload).json()


def createRoom(gameCode: str):
    payload = {"id": gameCode}
    return requests.get(URL + "/create", params=payload).json()


def getGame(gameCode: str, player: str):
    payload = {"id": gameCode, "player": player}
    return requests.get(URL + "/getGame", params=payload).json()


def submitAnswer(gameCode: str, player: str, answer: str):
    payload = {"id": gameCode, "player": player, "answer": answer}
    return requests.get(URL + "/submit", params=payload).json()
