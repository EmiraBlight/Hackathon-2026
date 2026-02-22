import requests
from requests.models import Response

URL = "http://10.109.206.111:2026"

def ping():
    return requests.get(f"{URL}/ping").json()["message"] == "pong"

def player2Connect(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(f"{URL}/join", params=payload).json()

def createRoom(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(f"{URL}/create", params=payload).json()

def getGame(gameCode: str, player: str) -> Response:
    payload = {"id": gameCode, "player": player}
    return requests.get(f"{URL}/getGame", params=payload).json()

def join(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(URL + "/join", params=payload)


def submitAnswer(gameCode: str, player: str, answer: str) -> Response:
    payload = {"id": gameCode, "player": player, "answer": answer}
    return requests.get(f"{URL}/submit", params=payload).json()
