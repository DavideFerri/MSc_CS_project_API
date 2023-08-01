from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from bson import ObjectId


# todo: ensure that validator names are unique

# ------------------------------- UTILITIES --------------------------------- #

# define class to handle serialization of ObjectId, that is required for object ids but is
# not natively supported by MongoDb (see https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Custom Response model for binary data
class BinaryResponseModel:
    def __init__(self, content: bytes, media_type: str):
        self.content = content
        self.media_type = media_type