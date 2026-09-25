"""Общая конфигурация тестов: тестовая БД и ключ подписи задаются
до импорта приложения, чтобы engine и SECRET_KEY поднялись на них."""
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_messenger.db"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789-abcdef"

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client():
    # вход в контекст запускает lifespan: создаются таблицы тестовой БД
    with TestClient(app) as c:
        yield c
