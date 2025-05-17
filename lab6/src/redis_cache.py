from hashlib import sha256
import redis.asyncio as redis


def redis_connection(func):

    async def wrapper(*args, **kwargs):

        try:
            redis_client = redis.Redis(host="redis", port=6379, db=0)
            response = await func(*args, **kwargs, redis_client=redis_client)
        except Exception as er:
            response = {"status": "Error", "message": er}

        finally:
            await redis_client.aclose()
            return response

    return wrapper


@redis_connection
async def add_user_ttl(login: str, json_data: dict, redis_client=None):
    # Add data in db HSET
    for key, value in json_data.items():
        response = await redis_client.hset(login, key, value)
    # Set TTL for key
    await redis_client.expire(login, 2 * 60)
    return response


@redis_connection
async def check_user_request(login: str, redis_client=None):
    response = await redis_client.hgetall(login)
    if response:
        return {
            key.decode("utf-8"): value.decode("utf-8")
            for key, value in response.items()
        }
    else:
        return {"status": "Error", "message": "Not Found"}


@redis_connection
async def init(redis_client=None):
    # Удалить все записи из бд
    print("!Redis INITED!")
    await redis_client.flushdb()
    await redis.add_user_ttl(
        "admin",
        {
            "name": "alex",
            "surname": "fil",
            "password": sha256("secret".encode()).hexdigest(),
        },
    )
    await redis.check_user_request("admin")
