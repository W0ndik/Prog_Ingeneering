import json
import asyncpg
import asyncio
import os
import time
from utils import print_table

DATABASE_URL = os.getenv("DATABASE_URL")


def db_connection(func):
    """
    Decorator for database connection management.
    """

    async def wrapper(*args, **kwargs):
        while True:
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                break
            except:
                time.sleep(1)

        try:
            async with conn.transaction():
                response = await func(*args, **kwargs, conn=conn)

        except Exception as er:
            # Handle any exceptions that may occur
            response = {"status": "Error", "message": er}

        finally:
            # Ensure the connection is released back to the pool
            await conn.close()
            return response

    return wrapper


@db_connection
async def init(conn=None) -> None:
    await conn.execute(
        """
            DROP TABLE IF EXISTS Users CASCADE;
            DROP TABLE IF EXISTS Walls CASCADE;
            DROP TABLE IF EXISTS Chats CASCADE;
            DROP TABLE IF EXISTS Messages CASCADE;
            CREATE TABLE Walls (
                id SERIAL PRIMARY KEY,
                posts text
            );
            CREATE TABLE Users (
                id SERIAL PRIMARY KEY,
                login char(128),
                name varchar(64),
                surname varchar(64),
                hashed_password char(128),
                wall_id integer,
                FOREIGN KEY (wall_id) REFERENCES Walls(id)
            );
            CREATE TABLE Chats(
                id SERIAL PRIMARY KEY,
                user1 integer,
                user2 integer,
                FOREIGN KEY (user1) REFERENCES Users(id),
                FOREIGN KEY (user2) REFERENCES Users(id)
            );
            CREATE TABLE Messages(
                id SERIAL PRIMARY KEY,
                chat_id integer,
                author char(128),
                body text,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES Chats(id)
            );
        """
    )
    # TODO: Убрать после дебага работы БД.
    await conn.execute(
        """
    INSERT INTO Walls (posts) VALUES ('Это страница админа, добро пожаловать!'),('Это страница второго админа, добро пожаловать!');
    """
    )
    await conn.execute(
        """
    INSERT INTO Users (login, hashed_password, name, surname, wall_id) VALUES ('admin','2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b','alex','fil',1),('admin2','2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b','alex2','fil2',2);
    """
    )
    await conn.execute(
        """
    INSERT INTO Chats (user1, user2) VALUES (1,2);
    """
    )
    await conn.execute(
        """
    INSERT INTO Messages (chat_id, author, body) VALUES (1,'admin','Hi! I`m admin, who are you?'),(1,'admin2','Hi! I`m admin too, glad to meet with you!');
    """
    )
    return None


@db_connection
async def add_new_user(login, password, name, surname, conn=None):
    return await conn.execute(
        """
    INSERT INTO Users (login, hashed_password, name, surname) VALUES ($1,$2,$3,$4);
    """,
        login,
        password,
        name,
        surname,
    )


@db_connection
async def get_user(login, conn=None):
    response = await conn.fetch("""SELECT * FROM Users WHERE login = $1;""", login)

    if response:
        response = [dict(record) for record in response][0]
    else:
        response = {"status": "Error"}

    return response


@db_connection
async def get_user_by_name(name, surname, conn=None):
    response = await conn.fetch(
        """SELECT * FROM Users WHERE name = $1 AND surname = $2;""", name, surname
    )
    if response:
        response = [dict(record) for record in response][0]
    else:
        response = {"status": "Error"}
    return response


@db_connection
async def add_new_post(post, login, conn=None):
    response = await conn.execute(
        """
    INSERT INTO Walls (posts) VALUES ($1);
    """,
        post,
    )
    wall_id = dict(
        await conn.fetchrow(
            """
    SELECT max(id) FROM Walls;
    """
        )
    )
    response = await conn.execute(
        """
    UPDATE Users SET wall_id = $1 WHERE login = $2;
    """,
        wall_id["max"],
        login,
    )
    return response


@db_connection
async def get_wall(login, conn=None):
    wall_id = await conn.fetch("""SELECT wall_id FROM Users WHERE login = $1;""", login)
    if wall_id:
        response = await conn.fetch(
            """SELECT posts FROM Walls WHERE id = $1;""", wall_id[0]["wall_id"]
        )

    if response:
        response = [dict(record) for record in response][0]
    else:
        response = {"status": "Error"}
    return response


@db_connection
async def get_chats(login, target_login, conn=None):
    response = await conn.fetch(
        """SELECT Chats.id, User1.login as login1, User2.login as login2
            FROM Chats
            JOIN Users AS User1 ON Chats.user1 = User1.id
            JOIN Users AS User2 ON Chats.user2 = User2.id
            WHERE 
                (User1.login = $1 AND User2.login = $2) 
                OR 
                (User1.login = $2 AND User2.login = $1);""",
        login,
        target_login,
    )
    print(response)
    if response:
        response = [dict(record) for record in response][0]
        chat_id = response["id"]
        user1 = response["login1"]
        user2 = response["login2"]

        messages = await conn.fetch(
            """
            SELECT body, author FROM Messages WHERE chat_id = $1;
            """,
            chat_id,
        )

        if messages:
            messages = [dict(record) for record in messages]
        else:
            messages = []

        return {"messages": messages, "users": [user1, user2], "chat_id": chat_id}
    else:
        return {"status": "Error"}


@db_connection
async def add_new_chat(login, target_login, conn=None):
    user1 = dict(
        await conn.fetchrow("""SELECT id FROM Users WHERE login = $1;""", login)
    )
    user2 = dict(
        await conn.fetchrow("""SELECT id FROM Users WHERE login = $1;""", target_login)
    )

    await conn.execute(
        """
    INSERT INTO Chats (user1, user2) VALUES ($1,$2);
    """,
        user1,
        user2,
    )


@db_connection
async def add_message(chat_id, login, body, conn=None):
    await conn.execute(
        """
    INSERT INTO Messages (chat_id, author, body) VALUES ($1,$2,$3);
    """,
        chat_id,
        login,
        body,
    )


@db_connection
async def select_all_users(conn=None):
    response = await conn.fetch("""SELECT * FROM Users;""")
    response = [dict(record) for record in response]

    print_table([elem.values() for elem in response], list(response[0].keys()))
    return response


@db_connection
async def select_all_chats(conn=None):
    response = await conn.fetch("""SELECT * FROM Chats;""")
    response = [dict(record) for record in response]

    print_table([elem.values() for elem in response], list(response[0].keys()))
    return response


@db_connection
async def select_all_messages(conn=None):
    response = await conn.fetch("""SELECT * FROM Messages;""")
    response = [dict(record) for record in response]

    print_table([elem.values() for elem in response], list(response[0].keys()))
    return response


@db_connection
async def select_all_walls(conn=None):
    response = await conn.fetch("""SELECT * FROM Walls;""")
    response = [dict(record) for record in response]

    print_table([elem.values() for elem in response], list(response[0].keys()))
    return response


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task1 = loop.create_task(init())
    loop.run_until_complete(asyncio.wait([task1]))
