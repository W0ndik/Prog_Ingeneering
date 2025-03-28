from pydantic import BaseModel

class WallPost(BaseModel):
    username: str
    content: str