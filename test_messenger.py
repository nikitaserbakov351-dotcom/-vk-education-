"""Тесты веб-мессенджера: REST-эндпоинты, JWT-авторизация, WebSocket."""
import jwt as pyjwt
import pytest
from fastapi.websockets import WebSocketDisconnect

SECRET_KEY = "test-secret-key-0123456789-abcdef"


def test_index_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_register_and_duplicate(client):
    first = client.post("/register", params={"username": "alice"})
    assert first.status_code == 200
    assert first.json()["message"] == "Успешно"

    second = client.post("/register", params={"username": "alice"})
    assert second.json()["message"] == "Уже зарегистрирован"


def test_login_issues_valid_jwt(client):
    client.post("/register", params={"username": "alice"})
    response = client.post("/login", params={"username": "alice"})
    token = response.json()["ws_token"]

    payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload["name"] == "alice"
    assert "exp" in payload


def test_login_unknown_user_404(client):
    response = client.post("/login", params={"username": "no_such_user"})
    assert response.status_code == 404


def test_history_returns_list(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ws_rejects_invalid_token(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=not-a-jwt"):
            pass


def test_ws_connect_receive_and_broadcast(client):
    client.post("/register", params={"username": "bob"})
    token = client.post("/login", params={"username": "bob"}).json()["ws_token"]

    with client.websocket_connect(f"/ws?token={token}") as ws:
        greeting = ws.receive_json()
        assert greeting["type"] == "system"
        assert "bob" in greeting["content"]

        ws.send_text("привет из теста")
        message = ws.receive_json()
        assert message["type"] == "message"
        assert message["sender"] == "bob"
        assert message["content"] == "привет из теста"
