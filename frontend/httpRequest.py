import requests
from requests.models import Response
from requests.sessions import Request

URL = "http://10.109.206.111:2026"


def ping():
    return requests.get(f"{URL}/ping").json()["message"] == "pong"


def player2Connect(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(f"{URL}/join", params=payload)


def createRoom(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(f"{URL}/create", params=payload)


def getGame(gameCode: str, player: str):
    payload = {"id": gameCode, "player": player}
    result = requests.get(f"{URL}/getGame", params=payload)
    for i in dict(result.json()).keys():
        yield result.json()[i]


def join(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(URL + "/join", params=payload)


def submitAnswer(gameCode: str, player: str, answer: str) -> Response:
    payload = {"id": gameCode, "player": player, "answer": answer}
    return requests.get(f"{URL}/submit", params=payload)
