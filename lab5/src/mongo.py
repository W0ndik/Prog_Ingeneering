import os
import traceback
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from functools import wraps

# Настройка подключения
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/my_database")
DATABASE_NAME = "my_database"
COLLECTION_NAME = "my_collection"


def mongo_connection(func):
    """Декоратор для подключения к базе данных MongoDB."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]

        try:
            result = func(db, *args, **kwargs)

        except:
            result = None
            print(traceback.format_exc())
        finally:
            client.close()

        return result

    return wrapper


@mongo_connection
def create_index(db):
    """Создание индекса по полю user_name."""
    collection = db[COLLECTION_NAME]
    index_name = collection.create_index([("user_name", ASCENDING)], unique=True)
    return f"Индекс создан: {index_name}"


@mongo_connection
def insert_document(db, document):
    """Добавление JSON-документа в коллекцию."""
    collection = db[COLLECTION_NAME]

    try:
        collection.update_one(
            {"user_name": document["user_name"]},
            {"$push": {"posts": {"$each": document["posts"]}}},
        )
        return f"Документ добавлен с _id: {document['user_name']}"

    except DuplicateKeyError:
        return {
            "status": "Error",
            "message": "Ошибка: Документ с таким user_name уже существует",
        }


@mongo_connection
def find_document_by_user_name(db, user_name):
    """Поиск документа по полю user_name."""
    collection = db[COLLECTION_NAME]
    document = collection.find_one({"user_name": user_name})
    if document:
        print(document)
        return document

    return {"status": "Error", "message": "Документ не найден"}


@mongo_connection
def init(db):
    create_index()

    cllection = db[COLLECTION_NAME]

    new_document = {
        "user_name": "admin",
        "posts": ["My first post", "My second post"],
    }

    cllection.insert_one(new_document)

    new_document2 = {
        "user_name": "admin2",
        "posts": ["My first post too", "My second post too"],
    }

    cllection.insert_one(new_document2)


# Пример использования
if __name__ == "__main__":
    # Создание индекса
    print(create_index())

    # Добавление документа
    sample_document = {
        "user_name": "john_doe",
        "email": "john.doe@example.com",
        "age": 30,
    }
    print(insert_document(sample_document))

    # Поиск документа
    print(find_document_by_user_name("john_doe"))
