from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from bson import ObjectId
from typing import Optional, Union, List, Dict, Literal, Any
from src.api.models.general import PyObjectId


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    disabled: Union[bool, None] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "andrea",
                "email": "andrea@tamarix.com",
            }
        }


class UserInDB(UserModel):
    hashed_password: str


class TokenModel(BaseModel):
    username: str
    access_token: str
    token_type: str


class TokenDataModel(BaseModel):
    username: Union[str, None] = None
