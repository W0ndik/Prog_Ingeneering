from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from hashlib import sha256
from config import client_db, ACCESS_TOKEN_EXPIRE_MINUTES, Chat, User, Wall, Message
from jwt_auth import pwd_context, create_access_token, get_current_client

app = FastAPI()

# Маршрут для получения токена


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    if form_data.username in client_db:
        password = client_db[form_data.username].hashed_password
        print(
            form_data.password,
            sha256(form_data.password.encode()).hexdigest(),
            password,
        )
        if sha256(form_data.password.encode()).hexdigest() == password:
            password_check = True

    if password_check:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# PUT /users/{login}/send_message/{target_login} - Отправка сообщения
@app.put("/users/{login}/send_message/{target_login}", response_model=Chat)
def send_message(
    login: str,
    target_login: str,
    body: str,
    current_user: str = Depends(get_current_client),
):
    if login in client_db.keys() and target_login in client_db.keys():
        # Находим кто общается
        user = client_db[login]
        target = client_db[target_login]
        # Создаём новое сообщение
        message = Message(
            body=body, user_name=user.name if getattr(user, "name") else login
        )

        # Если у пользователя есть чаты
        if getattr(user, "chats"):
            for chat in user.chats:
                # Если у двух пользователей уже существует чат
                if target_login in (chat.login1, chat.login2):
                    chat.messages.append(message)
                    return chat
            # Если пробежали все, но не нашли нужный -> создаём новый

        # Если чата не существует
        # Создадим чат
        new_chat = Chat(messages=[message], login1=login, login2=target_login)
        # Добавим первому пользователю
        user.chats = [new_chat]

        # Добавим второму
        if getattr(target, "chats"):
            target.chats.append(new_chat)
        else:
            target.chats = [new_chat]

        return new_chat
    raise HTTPException(status_code=404, detail="User not found")


# GET /users/{user_id}/wall - Получить список сообщений (требует аутентификации)
@app.get("/users/{login}/chat/{target_login}", response_model=Chat)
def get_chat(
    login: str, target_login: str, current_user: str = Depends(get_current_client)
):
    if login in client_db.keys():
        user = client_db[login]
        if getattr(user, "chats"):
            for chat in user.chats:
                if target_login in (chat.login1, chat.login2):
                    return chat

        raise HTTPException(status_code=404, detail="Chat not found")
    raise HTTPException(status_code=404, detail="User not found")


# GET /users/{user_id}/wall - Получить стену пользователя (требует аутентификации)
@app.get("/users/{login}/wall", response_model=Wall)
def get_wall(login: str, current_user: str = Depends(get_current_client)):
    if login in client_db.keys():
        if getattr(client_db[login], "wall"):
            return client_db[login].wall

        raise HTTPException(status_code=404, detail="Wall not found")
    raise HTTPException(status_code=404, detail="User not found")


# POST /users/{login}/create_post - Создать нового поста на стене
@app.post("/users/{login}/create_post", response_model=Wall)
def create_post(
    login: str, post_txt: str, current_user: str = Depends(get_current_client)
):
    if login in client_db.keys():
        user = client_db[login]
        if getattr(user, "wall"):
            user.wall.posts.append(post_txt)
        else:
            user.wall = Wall(posts=[post_txt])
        return user.wall

    raise HTTPException(status_code=404, detail="User not found")


# GET /users/{user_id} - Получить пользователя по имени и фамилии (требует аутентификации)
@app.get("/users/{name}/{surname}", response_model=User)
def get_user_by_name(
    name: str, surname: str, current_user: str = Depends(get_current_client)
):
    for login in client_db.keys():
        if name == client_db[login].name and surname == client_db[login].surname:
            return client_db[login]
    raise HTTPException(status_code=404, detail="User not found")


# GET /users/{user_id} - Получить пользователя по логину (требует аутентификации)
@app.get("/users/{login}", response_model=User)
def get_user(login: str, current_user: str = Depends(get_current_client)):
    if login in client_db.keys():
        return client_db[login]
    raise HTTPException(status_code=404, detail="User not found")


# POST /users - Создать нового пользователя
@app.post("/users", response_model=User)
def create_user(user: User, current_user: str):
    if user.login in client_db.keys():
        raise HTTPException(status_code=404, detail="User already exist")
    else:
        # Предполагается, что при регистрации пользователь передаст не хэшированный пароль
        # (По правильному, конечно, надо сразу на стороне клиента пароль хэшировать)
        user.hashed_password = sha256(user.hashed_password.encode()).hexdigest()
        client_db[user.login] = user
    print(client_db)
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
