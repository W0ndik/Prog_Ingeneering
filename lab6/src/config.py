from pydantic import BaseModel
from typing import Optional

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Message(BaseModel):
    body: str
    author: str


# Модель данных для чатов
class Chat(BaseModel):
    messages: list[Message]
    login1: str
    login2: str


# Модель данных для стены
class Wall(BaseModel):
    posts: list[str]


# Модель данных для пользователя
class User(BaseModel):
    login: str
    hashed_password: str
    name: Optional[str] = None
    surname: Optional[str] = None
    wall: Optional[Wall] = None
    chats: Optional[list[Chat]] = None


# Псевдо-база данных пользователей
client_db = {
    "admin": User(
        login="admin",
        hashed_password="2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b",
        name="Ivan",
        surname="Ivanov",
    )
}
