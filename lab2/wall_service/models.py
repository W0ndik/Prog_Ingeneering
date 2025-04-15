from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(ObjectId):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Неверный ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):  # обновлённый вариант
        return {"type": "string"}



class WallPost(BaseModel):
    content: str

class WallPostInDB(WallPost):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "content": "Привет, мир!",
            }
        }
