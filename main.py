from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt
import os
import webbrowser
import threading
import time
import uvicorn
from datetime import datetime, timedelta, timezone

from database import engine, Base, get_db
from models import User, Message
from ws_manager import manager

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me-0123456789")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Автоматически открываем браузер
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8080")

    threading.Thread(target=open_browser).start()
    yield


app = FastAPI(title="Web Messenger MVP", lifespan=lifespan)


@app.get("/")
async def get_frontend():
    """Отдает интерфейс. Если файла нет, покажет понятную ошибку."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Ошибка: файл index.html не найден!</h1>")


@app.post("/register")
async def register(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first():
        return {"message": "Уже зарегистрирован"}
    new_user = User(username=username)
    db.add(new_user)
    await db.commit()
    return {"message": "Успешно"}


@app.post("/login")
async def login(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Не найден")

    exp = datetime.now(timezone.utc) + timedelta(minutes=5)
    token = jwt.encode({"sub": str(user.id), "name": user.username, "exp": exp}, SECRET_KEY, algorithm="HS256")
    return {"ws_token": token}


@app.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message.content, User.username)
        .join(User, Message.sender_id == User.id)
        .order_by(Message.id)
    )
    history = []
    for row in result.all():
        history.append({
            "sender": row.username,
            "content": row.content,
            "type": "message"
        })
    return history


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        username = payload.get("name")
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    await manager.broadcast({"type": "system", "content": f"{username} вошел в чат"})

    try:
        while True:
            data = await websocket.receive_text()
            new_msg = Message(sender_id=int(user_id), chat_id=0, content=data)
            db.add(new_msg)
            await db.commit()

            await manager.broadcast({
                "type": "message",
                "sender": username,
                "content": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.broadcast({"type": "system", "content": f"{username} покинул чат"})


# Этот блок позволяет запускать сервер прямо из PyCharm кнопкой Play
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)