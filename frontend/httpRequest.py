import requests
from requests.models import Response

URL = "http://10.109.206.111:2026"


def ping() -> bool:
    return requests.get("http://10.109.206.111:2026/ping").json()["message"] == "pong"


def player2Connect(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(URL + "/join", params=payload)


def createRoom(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(URL + "/create", params=payload)


def getGame(gameCode: str, player: str) -> Response:
    payload = {"id": gameCode, "player": player}
    return requests.get(URL + "/getGame", params=payload)


def join(gameCode: str) -> Response:
    payload = {"id": gameCode}
    return requests.get(URL + "/join", params=payload)


def submitAnswer(gameCode: str, player: str, answer: str) -> Response:
    payload = {"id": gameCode, "player": player, "answer": answer}
    return requests.get(URL + "/submit", params=payload)


def getResults(gameCode: str, player: str) -> Response:
    payload = {"id": gameCode, "player": player}
    return requests.get(URL + "/qnaOfPlayer", params=payload)
