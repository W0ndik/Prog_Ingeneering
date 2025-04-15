from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from models import WallPost, WallPostInDB
import os
import httpx

SECRET_KEY = "secret"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = MongoClient(MONGO_URL)
db = client["wall_db"]
collection = db["wall"]

collection.create_index([("username", ASCENDING)])

app = FastAPI()
router = APIRouter()

if collection.count_documents({}) == 0:
    collection.insert_many([
        {"username": "admin", "content": "Первый пост"},
        {"username": "admin", "content": "Второй пост"}
    ])

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@router.post("/token")
async def proxy_token(request: Request):
    form = await request.form()
    async with httpx.AsyncClient() as client:
        response = await client.post("http://user_service:8000/token", data=form)
    return JSONResponse(status_code=response.status_code, content=response.json())

app.include_router(router)

@app.post("/post", response_model=WallPostInDB)
def add_post(post: WallPost, username: str = Depends(verify_token)):
    try:
        data = post.dict()
        data["username"] = username
        result = collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return WallPostInDB(**data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при добавлении поста")


@app.get("/wall", response_model=list[WallPostInDB])
def get_wall():
    posts = []
    for doc in collection.find():
        doc["_id"] = str(doc["_id"]) 
        posts.append(WallPostInDB(**doc))
    return posts


@app.get("/posts/{post_id}", response_model=WallPostInDB)
def get_post(post_id: str):
    post = collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    post["_id"] = str(post["_id"])  # 🔧 фикс ObjectId → str
    return WallPostInDB(**post)

# Удалить пост
@app.delete("/posts/{post_id}")
def delete_post(post_id: str, username: str = Depends(verify_token)):
    result = collection.delete_one({"_id": ObjectId(post_id), "username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Пост не найден или нет доступа")
    return {"message": "Пост удалён"}
